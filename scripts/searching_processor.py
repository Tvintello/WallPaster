from PyQt6.QtCore import QObject, pyqtSignal as Signal


class SearchingProcessor(QObject):
    finished = Signal()
    error_signal = Signal(str)

    def __init__(self, start_func, show_error):
        super().__init__()
        self.start = start_func
        self.error_signal.connect(show_error)

    def run(self):
        self.start()
        self.finished.emit()