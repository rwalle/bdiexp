# bdiexp: A GUI App for Digital Holography Acquisition, Monitoring and Analysis

This is a Python based GUI app designed for digital holography research. It integrates instrument control, experiment workflow and data analysis. Features include:

* Fast real-time FFT reconstructions
* Automatic instrument control
* Integration with MATLAB
* Running asynchronous sequential experiment
* Experiment status update
* more...

The package uses the following instruments, but you are free to write your own Python class and include them in the `bdi_system.py`.

* Basler pilot piA1600-35gm camera
* Thorlabs T-Cube stepper motor
* Superlum superluminescent diode (BLMS mini)
* A relay switch controlled by Arduino (serial output over USB)

Although the app is written for digital holography experiments, the framework can be applied to many lab work in different areas.

[Screenshot](https://i.imgur.com/T7XCsWj.png)

## Prerequisites

Basic dependencies:

* [NumPy](https://numpy.org/)
* [Matplotlib](https://matplotlib.org/)
* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)

Instrument related dependencies:

* [pySerial](https://pythonhosted.org/pyserial/)
* [py_thorlabs_ctrl](https://github.com/rwalle/py_thorlabs_ctrl)
* [py_blms_ctrl](https://github.com/rwalle/py_blms_ctrl)
* [pybasler](https://github.com/rwalle/pybasler)

## Usage

`bdm_unified.py` is the GUI program.

## Customization

To start an asynchronous experiment, use the following code in a function of the GUI class:

```Python
self.exp_plan = NewExperimentPlan(params)
self.job = ExpDispatcher(self.exp_system, self.exp_plan, params, self.before_exp, self.update_status, self.after_exp)
self.job.start_exp()
```

experiment plan, experiment dispatcher need to be properties of the GUI class, because otherwise the objects may be deallocated (i.e. deleted) by the garbage collector.

Details of the classes are explained below.

### Experiment system

A class that serves as the interface for controlling lab instruments.

### Experiment plan

The sequence for an experiment is described in `experiment_plan.py`. All experiment plan class should inherit the `ExpPlan` base class. Class structure:

```Python
class NewExperimentPlan:
    tasks # list of tuples
    current_task # int
    completed # boolean
    __init__()
    get_current_task()
    next_task()
    next_iteration()
```

* `next_iteration`: Save new tasks to the `tasks` variable. The "BDI worker" will run the tasks in this variable sequentially.
* `next_task()`: run the next task and increase `current_task` index by 1.

Tasks are lists of tuples of three elements:

```Python
(task_type, params, help_text)
```

which are task types defined by `Tasks` enumerator, parameters of the task, and help text that will be shown on the GUI and sent to remote server when updating experiment status.

### Dispatcher

new dispatcher:
```Python
from .dispatcher import ExpDispatcher
dispatcher = ExpDispatcher(exp_system, exp_plan, worker_params = None,
             start_fcn = (lambda:None), update_fcn = (lambda res: None),
             finish_fcn = (lambda: None))
```

pass the experiment systems, experiment plans, worker parameters, and functions to call before starting, after each iteration, and after the experiment finishes to the dispatcher.