from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QWidget, QLineEdit)


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)


class MPLCanvas(FigureCanvas):

    def __init__(self, parent=None):
        fig = Figure()
        FigureCanvas.__init__(self, fig)