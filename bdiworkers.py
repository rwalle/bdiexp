import numpy as np
from datetime import datetime, timedelta
import scipy.misc, time

from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal as Signal

from experiment_plan import Tasks

"""
    IDLE = 0
    WAIT = 1
    MOVE_Z = 2
    CAPTURE_SAVE = 3
    PRE_PROCESSING = 4
    POST_PROCESSING = 5
"""


class Worker(QThread):

    update_status = Signal(tuple)

    def __init__(self, exp_system, exp_plan, params = None):

        super().__init__()

        self.exp_system = exp_system
        self.exp_plan = exp_plan

        self.task_func = {
            
            Tasks.WAIT: self.wait_time,
            Tasks.MOVE_Z: self.move_z,
            Tasks.CAPTURE_SAVE: self.capture_save,
            Tasks.PRE_PROCESSING: self.pre_processing,
            Tasks.POST_PROCESSING: self.post_processing,

        }

        self.params = params

    def wait_time(self, args):
        time_to_wait = args
        time.sleep(time_to_wait)

    def capture_save(self, args):
        # (fps, count, ptn, frame_start)

        param = args

        self.exp_system.fourier_camera.grab_n_save(*param)

    def move_z(self, args):

        rel_pos = args

        self.exp_system.mc.move_relative(rel_pos)

    def pre_processing(self, args):

        pass

    def post_processing(self, args):

        import subprocess
        try:
            subprocess.run(["plink", "pi", "python beep.py"])
        except Exception as err:
            print("fail to beep")

    def run(self):

        try:

            while not self.exp_plan.completed:

                task = self.exp_plan.get_current_task()

                task_id = task[0]
                task_func = self.task_func[task_id]
                task_arg = task[1]
                task_txt = task[2]

                self.update_status.emit((task_id, task_txt))
                
                task_func(task_arg)

                self.exp_plan.next_task()

        except Exception as e:

            print(e)
            raise