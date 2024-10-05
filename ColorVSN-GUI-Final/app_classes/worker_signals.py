from PyQt5.QtCore import QObject, pyqtSignal
from numpy import ndarray


class WorkerSignals(QObject):
    finished = pyqtSignal(bool, str)
    status = pyqtSignal(bool, str)
    update = pyqtSignal(ndarray)