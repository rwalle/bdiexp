import os
from enum import Enum

from bdiworkers import Worker

class ExpDispatcher:

    def __init__(self, exp_system, exp_plan, worker_params = None, start_fcn = (lambda:None), 
                 update_fcn = (lambda res: None), finish_fcn = (lambda: None)):

        """
        start_fcn()
        update_fcn((state_code, state_text))
        finish_fcn()
        """

        self.exp_system = exp_system
        self.exp_plan = exp_plan
        
        self.worker_params = worker_params

        self.start_fcn = start_fcn
        self.update_fcn = update_fcn
        self.finish_fcn = finish_fcn

    def start_exp(self):

        self.worker = Worker(self.exp_system, self.exp_plan, self.worker_params)

        self.start_fcn()
        self.worker.update_status.connect(self.update_fcn)
        self.worker.finished.connect(self.finish_fcn)

        self.worker.setTerminationEnabled(True)

        self.worker.start()

    def terminate(self):

        self.worker.terminate()

        print("Experiment terminated")

    def update(self, p):
        pass