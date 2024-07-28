from PyQt6.QtCore import QObject, pyqtSignal as Signal
from random import choice


class SearchingProcessor(QObject):
    finished = Signal()
    error_signal = Signal(str)

    def __init__(self, start_func, show_error):
        super().__init__()
        self.start = start_func
        self.error_signal.connect(show_error)

    def run(self, images, main_lay, main_page, load_page, resolution, get_available_res):
        if not images:
            print("IMAGES WERE NOT FOUND")
            self.error_signal.emit("WARNING: images with these themes were not found")
            main_lay.setCurrentWidget(main_page)
            return

        link = choice(images)

        count = 0
        while not (resolution in get_available_res(link)):
            link = images[count]
            count += 1

            if count == len(images):
                print("IMAGES WERE NOT FOUND")
                self.error_signal.emit("WARNING: images with this resolution were not found")
                main_lay.setCurrentWidget(main_page)
                return
        self.start(link)
        self.finished.emit()