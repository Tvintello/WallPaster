import json
import sys
import ctypes
import os
from random import choice
from pathlib import Path
import json

from PyQt6.QtCore import QSize, Qt, QThread, QTimer
from PyQt6.QtGui import QIcon, QMovie, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QSpinBox,
    QBoxLayout, QComboBox, QErrorMessage, QFileDialog, QStackedLayout)

from parsers.wallscloud_parser import WallsCloud
from scripts.style import style_sheet
from scripts.tray import AppTray
from scripts.searching_processor import SearchingProcessor
from scripts.support import get_image_name, save_json, read_json

ROOT = Path(__file__).resolve().parent
PARSERS = [WallsCloud]


class MainWindow(QMainWindow):
    def __init__(self, screen_size: QSize):
        super().__init__()

        # window properties and variables
        self.window_size = QSize(500, 300)
        self.setWindowTitle("WallPaster")
        self.setFixedSize(self.window_size)
        self.setStyleSheet("background-color: #303030;")
        self.setWindowIcon(QIcon("icons/icon.png"))

        if not os.path.exists(os.path.join(ROOT, "save.json")):
            open(os.path.join(ROOT, "save.json"), "w")

        self.saved = read_json()

        if not self.saved or (isinstance(self.saved, dict) and list(self.saved.keys()) != ["dir", "interval", "resolution"]):
            self.directory = os.path.join(ROOT, "images")
            self.saved = {"dir": self.directory, "interval": 60000,
                          "resolution": [screen_size.width(), screen_size.height()]}
            save_json(self.saved)
        self.query = {"q": "", "page": 1}
        self.url = PARSERS[0].url
        self.parser = PARSERS[0]()
        self.images = self.parser.get_image_links(self.query)
        self.resolution = self.saved["resolution"]
        self.directory = self.saved["dir"]
        self.loading_gif = QMovie("icons/loading.gif")
        self.is_recently_loaded = False
        self.search_thread = QThread()
        self.second_timer = QTimer()
        self.second_timer.timeout.connect(self.every_second_update)
        self.second_timer.start(1000)
        self.slide_timer = QTimer()
        self.slide_timer.timeout.connect(self.run)
        self.slide_timer.setInterval(self.saved["interval"])
        self.tray_icon = AppTray(self)
        self.tray_icon.add_tray()
        self.current_image = ""

        # window initialization
        self.container = QWidget()
        self.main_lay = QStackedLayout(self.container)
        self.main_lay.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.main_page = QWidget()
        main_page_lay = QVBoxLayout()
        main_page_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_page.setLayout(main_page_lay)
        self.main_lay.addWidget(self.main_page)

        self.slide_label = QLabel("Slide show")
        self.start_button = QPushButton(" Start")
        self.stop_button = QPushButton(" Stop")
        self.address = QComboBox()
        self.themes = QLineEdit()
        self.orientation = QComboBox()
        self.width_number = QSpinBox()
        self.height_number = QSpinBox()
        self.error_message = QErrorMessage(self.container)
        self.searching = SearchingProcessor(self.set_random_image, self.show_error)
        self.directory_button = QPushButton()
        self.directory_edit = QLineEdit()
        self.blackout = QWidget()
        self.interval_label = QLabel("time interval (min): ")
        self.interval_widget = QSpinBox()
        self.directory_label = QLabel("Image directory:")
        self.image_button = QPushButton("Set random wallpaper")
        self.remain_label = QLabel("Remaining time: ")

        self.header(main_page_lay)
        site = self.site_section(main_page_lay)
        self.directory_section(site["address_section"])
        self.resolution_section(site["search_section"])
        self.add_image_button(main_page_lay)
        main_page_lay.addStretch()
        self.start_section(main_page_lay)
        self.loading_page(self.main_lay)

        self.setCentralWidget(self.container)
        self.themes.setFocus()

    def every_second_update(self):
        self.remain_label.setText(f"Remaining time: {self.slide_timer.remainingTime() // 1000}s")
        self.second_timer.start(1000)

    def mousePressEvent(self, event) -> None:
        self.setFocus()

    def header(self, layout: QBoxLayout):
        caption = QLabel()
        caption.setText("WallPaster")
        caption.setStyleSheet("color: white; font-size: 20px; margin: 10px 0 20px 0;")
        caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(caption)

    def add_image_button(self, layout: QBoxLayout):
        image_lay = QHBoxLayout()
        image_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.image_button.setStyleSheet("padding: 5px;")
        self.image_button.pressed.connect(self.run)
        image_lay.addWidget(self.image_button)

        layout.addLayout(image_lay)

    def site_section(self, layout: QBoxLayout):
        self.address.setStyleSheet("border: 1px solid black;")
        self.address.addItems(map(lambda x: x.name, PARSERS))
        self.address.currentTextChanged.connect(self.set_parser)

        theme_lay = QHBoxLayout()

        all_button = QPushButton("all")
        all_button.pressed.connect(self.on_all_button)

        self.themes.setPlaceholderText("Search [all images]")
        self.themes.setStyleSheet("border: 1px solid black;")
        self.themes.editingFinished.connect(self.set_themes)
        self.themes.setFocus()

        theme_lay.addWidget(self.themes)
        theme_lay.addWidget(all_button)

        orientation_lay = QHBoxLayout()

        orientation_label = QLabel("orientation: ")
        orientation_lay.addWidget(orientation_label)

        self.orientation.addItems(["Landscape", "Portrait"])
        self.orientation.currentTextChanged.connect(self.on_orientation_changed)
        self.query["orientation"] = self.orientation.currentText().lower()
        orientation_lay.addWidget(self.orientation)

        input_section = QHBoxLayout()
        search_section = QVBoxLayout()
        search_section.addLayout(theme_lay)
        search_section.addLayout(orientation_lay)
        address_section = QVBoxLayout()
        address_section.addWidget(self.address)

        search_section.setAlignment(Qt.AlignmentFlag.AlignTop)
        address_section.setAlignment(Qt.AlignmentFlag.AlignTop)

        input_section.addLayout(address_section)
        input_section.addLayout(search_section)
        input_section.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addLayout(input_section)

        return {"input_section": input_section,
                "search_section": search_section, "address_section": address_section}

    def on_all_button(self):
        self.query["q"] = ""
        self.images = self.parser.get_image_links(self.query)
        self.themes.setText("")

    def resolution_section(self, layout: QBoxLayout):
        width_label = QLabel()
        width_label.setText("width: ")

        self.width_number.setMinimum(100)
        self.width_number.setMaximum(10000)
        self.width_number.setValue(self.resolution[0])
        self.width_number.editingFinished.connect(self.on_resolution_changed)

        width = QHBoxLayout()
        width.addWidget(width_label)
        width.addWidget(self.width_number)
        width.setAlignment(Qt.AlignmentFlag.AlignLeft)

        height_label = QLabel()
        height_label.setText("height: ")

        self.height_number.setMinimum(100)
        self.height_number.setMaximum(10000)
        self.height_number.setValue(self.resolution[1])
        self.height_number.editingFinished.connect(self.on_resolution_changed)

        height = QHBoxLayout()
        height.addWidget(height_label)
        height.addWidget(self.height_number)
        height.setAlignment(Qt.AlignmentFlag.AlignLeft)

        size = QHBoxLayout()
        size.addLayout(width)
        size.addLayout(height)

        layout.addLayout(size)

    def directory_section(self, layout: QBoxLayout):
        directory_layout = QHBoxLayout()
        directory_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.directory_button.pressed.connect(self.choose_directory)
        self.directory_button.setStyleSheet("fill: yellow;max-width: 20px;height: 20px;")
        self.directory_button.setIcon(QIcon("icons/image_folder.svg"))

        self.directory_edit.setText(self.directory)
        self.directory_edit.textEdited.connect(self.set_directory)

        directory_layout.addWidget(self.directory_button)
        directory_layout.addWidget(self.directory_edit)
        layout.addWidget(self.directory_label)
        layout.addLayout(directory_layout)

    def start_section(self, layout: QBoxLayout):
        label_lay = QVBoxLayout()

        self.slide_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.slide_label.setStyleSheet("font-size: 16px")
        label_lay.addWidget(self.slide_label)

        self.interval_section(label_lay)

        start_lay = QHBoxLayout()
        start_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        start_lay.setContentsMargins(0, 0, 0, 30)

        self.start_button.setObjectName("play_button")
        self.start_button.pressed.connect(self.on_timer_started)
        self.start_button.setIcon(QIcon("icons/play_button.png"))

        self.stop_button.setObjectName("stop_button")
        self.stop_button.setEnabled(False)
        self.stop_button.pressed.connect(self.on_timer_stopped)
        stop_icon = QIcon()
        stop_icon.addPixmap(QPixmap("icons/stop_button-active.png"), QIcon.Mode.Normal)
        stop_icon.addPixmap(QPixmap("icons/stop_button-disabled.png"), QIcon.Mode.Disabled)
        self.stop_button.setIcon(stop_icon)

        start_lay.addWidget(self.start_button)
        start_lay.addWidget(self.stop_button)

        label_lay.addLayout(start_lay)
        layout.addLayout(label_lay)

    def loading_page(self, layout: QStackedLayout):
        self.blackout.setStyleSheet("background-color: rgba(0,0,0,.3);")

        self.loading_gif = QMovie("icons/loading.gif")

        loading = QLabel()
        loading.setMovie(self.loading_gif)
        loading.move(self.window_size.width() // 2 - 16, self.window_size.height() // 2 - 16)
        loading.setFixedSize(32, 32)
        loading.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        loading.setParent(self.blackout)

        layout.addWidget(self.blackout)

    def interval_section(self, layout: QBoxLayout):
        interval = QHBoxLayout()
        interval.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.interval_widget.setMinimum(1)
        self.interval_widget.setMaximum(17000)
        self.interval_widget.setValue(self.saved["interval"] // 60000)
        self.interval_widget.editingFinished.connect(self.set_interval)

        interval.addWidget(self.interval_label)
        interval.addWidget(self.interval_widget)
        interval.addWidget(self.remain_label)
        layout.addLayout(interval)

    def set_interval(self) -> None:
        value = self.interval_widget.value()
        ms = value * 60 * 1000
        self.slide_timer.setInterval(ms)
        self.saved["interval"] = ms
        save_json(self.saved)
        print(self.slide_timer.interval())

    def show_error(self, text):
        self.error_message.showMessage(text)

    def complete_close(self):
        self.destroy()
        self.tray_icon.deleteLater()
        app.quit()

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()

    def run(self):
        self.search_thread = QThread()
        self.searching = SearchingProcessor(self.set_random_image, self.show_error)
        self.searching.moveToThread(self.search_thread)
        self.search_thread.started.connect(lambda: self.searching.run(self.images, self.main_lay, self.main_page,
                                                                      self.blackout, self.resolution,
                                                                      self.parser.get_available_resolutions))
        self.searching.finished.connect(self.search_thread.quit)
        self.searching.finished.connect(self.searching.deleteLater)
        self.search_thread.finished.connect(self.search_thread.deleteLater)
        self.search_thread.start()
        self.main_lay.setCurrentWidget(self.blackout)

    def set_directory(self, value):
        self.saved["dir"] = value
        save_json(self.saved)
        self.directory = value
        print(value)

    def choose_directory(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Directory", r"D:\apps\WallPaster")

        if dir:
            self.directory = dir

        self.saved["dir"] = self.directory
        save_json(self.saved)

        self.directory_edit.setText(self.directory)
        print(self.directory)

    def on_resolution_changed(self):
        self.resolution = [self.width_number.value(), self.height_number.value()]
        self.saved["resolution"] = self.resolution
        save_json(self.saved)
        print(self.resolution)

    def on_orientation_changed(self, value):
        self.query["orientation"] = value.lower()
        self.images = self.parser.get_image_links(self.query)
        print(value)

    def set_parser(self, value):
        self.parser = value
        self.url = self.parser.url
        self.images = self.parser.get_image_links(self.query)
        print(self.url)

    def on_timer_stopped(self):
        self.stop_button.setEnabled(False)
        self.slide_timer.stop()
        print(self.slide_timer.interval())

    def on_timer_started(self):
        self.run()
        self.stop_button.setEnabled(True)
        self.slide_timer.start()

    def set_random_image(self, link):
        print("START")
        print(self.query)
        print("Image: ", link)
        image = self.download_image_by_link(link)
        self.set_wallpaper(image)
        self.main_lay.setCurrentWidget(self.main_page)  # hide loading page

    def set_themes(self):
        self.query["q"] = self.themes.text()
        self.themes.clearFocus()
        self.images = self.parser.get_image_links(self.query)
        print(self.query)

    def set_query(self, value):
        self.query["q"] = value
        print(self.query)

    def download_image_by_link(self, link) -> str:
        img = self.parser.get_image(link, self.resolution)
        path = os.path.join(self.directory, f"{get_image_name(link)}.{img.format.lower()}")
        img.save(path)

        return path

    def download_image_by_bytes(self, byte: bytes, name: str) -> str:
        with open(self.directory + name, "wb") as f:
            f.write(byte)

        return name

    def set_wallpaper(self, path: str) -> int:
        cs = ctypes.c_buffer(path.encode())
        spi_setdeskwallpaper = 0x14
        return ctypes.windll.user32.SystemParametersInfoA(spi_setdeskwallpaper, 0, cs, 0)


if __name__ == "__main__":
    try:
        os.chdir(sys._MEIPASS)
    except AttributeError:
        os.chdir(ROOT)

    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    screensize = app.primaryScreen().geometry().size()
    window = MainWindow(screensize)
    window.show()
    app.exec()
