#!/bin/python

import os, json
from enum import Enum
from datetime import datetime, timedelta


class Tasks(Enum):
    IDLE = 0
    WAIT = 1
    MOVE_Z = 2
    CAPTURE_SAVE = 3
    PRE_PROCESSING = 4
    POST_PROCESSING = 5


class ExpPlan:

    def __init__(self):
        self.current_task = 0
        self.tasks = []
        self.completed = False

    def next_iteration(self):
        pass

    def next_task(self):
        self.current_task += 1

        if self.current_task == len(self.tasks):
            self.current_task = 0
            self.next_iteration()

    def get_current_task(self):
        task = self.tasks[self.current_task]
        return task


class BDMSingleLoop(ExpPlan):
    _CONFIG_FILE = 'bdm_unified_settings.json'

    def __init__(self, params):

        super().__init__()

        self.save_dir = params['save_dir']
        self.FILE_PREFIX = 'test-'
        self.FILE_FORMAT = 'tiff'

        self.fps = 25

        with open(self._CONFIG_FILE, 'r') as json_file:
            bdm_params = json.load(json_file)

        capture_params = bdm_params['CAPTURE_SETTINGS']

        self.BG_FRAME_COUNT = capture_params['BG_FRAME']
        self.HOLO_FRAME_COUNT = capture_params['HOLOG_FRAME']
        self.START_WAIT = capture_params['START_WAIT']
        self.CONTROLLER_WAIT = capture_params['Z_WAIT']

        self.done = False

        self.next_iteration()


    def next_iteration(self):

        if not self.done:

            file_ptn = os.path.join(self.save_dir, self.FILE_PREFIX + '%d' + '.' + self.FILE_FORMAT)
            bg_capture_params = (self.BG_FRAME_COUNT, self.fps, file_ptn, 1)
            holo_capture_params = (self.HOLO_FRAME_COUNT, self.fps, file_ptn, 1 + self.BG_FRAME_COUNT)

            self.tasks = [
                (Tasks.PRE_PROCESSING, None, 'Pre processing'),
                (Tasks.WAIT, self.START_WAIT, 'wait'),
                (Tasks.MOVE_Z, -1, 'move z -'),
                (Tasks.WAIT, self.CONTROLLER_WAIT, 'wait for controller'),
                (Tasks.CAPTURE_SAVE, bg_capture_params, 'capture background'),
                (Tasks.MOVE_Z, 1, 'move z +'),
                (Tasks.WAIT, self.CONTROLLER_WAIT, 'wait for controller'),
                (Tasks.CAPTURE_SAVE, holo_capture_params, 'capture holograms'),
                (Tasks.POST_PROCESSING, None, 'Post processing')
            ]

            self.done = True

        else:

            self.tasks = []
            self.completed = True
