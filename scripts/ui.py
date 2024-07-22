import sys

import requests
from bs4 import BeautifulSoup
import ctypes
import os
from random import choice, random
from pathlib import Path
import math
from threading import Thread

from PyQt6.QtCore import QSize, Qt, QThread, QObject
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QLabel,
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QSpinBox,
    QBoxLayout, QComboBox, QErrorMessage, QFileDialog, QStackedLayout)


class UI(QMainWindow):
    def __init__(self, screen_size: QSize):
        super().__init__()

        # window properties and variables
        self.window_size = QSize(500, 300)
        self.setWindowTitle("WallPaster")
        self.setFixedSize(self.window_size)
        self.setStyleSheet("background-color: #303030;")

        self.loading_gif = QMovie("icons/loading.gif")

        # window initialization
        container = QWidget()
        self.main_lay = QStackedLayout(container)
        self.main_lay.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.main_page = QWidget()
        main_page_lay = QVBoxLayout()
        main_page_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_page.setLayout(main_page_lay)
        self.main_lay.addWidget(self.main_page)

        self.start_button = QPushButton()
        self.address = QComboBox()
        self.themes = QLineEdit()
        self.orientation = QComboBox()
        self.width_number = QSpinBox()
        self.height_number = QSpinBox()
        self.error_message = QErrorMessage(container)
        self.error_message.setStyleSheet("color: white")
        self.directory_button = QPushButton()
        self.directory_edit = QLineEdit()
        self.blackout = QWidget()

        self.header(main_page_lay)
        site = self.site_section(main_page_lay)
        self.directory_section(site["address_section"])
        self.resolution_section(site["address_section"])
        self.start_section(main_page_lay)
        self.loading_page(self.main_lay)

        self.setCentralWidget(container)
        self.themes.setFocus()

    def header(self, layout: QBoxLayout):
        caption = QLabel()
        caption.setText("WallPaster")
        caption.setStyleSheet("color: white; font-size: 20px; margin: 10px 0 20px 0;")
        caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(caption)

    def site_section(self, layout: QBoxLayout):
        self.address.setStyleSheet("border: 1px solid black; color: white")

        self.themes.setPlaceholderText("Themes")
        self.themes.setStyleSheet("border: 1px solid black; color: white")
        self.themes.setFocus()

        self.orientation.setStyleSheet("color: white")

        input_section = QHBoxLayout()
        search_section = QVBoxLayout()
        search_section.addWidget(self.themes)
        search_section.addWidget(self.orientation)
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

    def resolution_section(self, layout: QBoxLayout):
        width_label = QLabel()
        width_label.setText("width: ")
        width_label.setStyleSheet("color: white")

        self.width_number.setMinimum(100)
        self.width_number.setMaximum(10000)
        self.width_number.setStyleSheet("color: white")

        width = QHBoxLayout()
        width.addWidget(width_label)
        width.addWidget(self.width_number)
        width.setAlignment(Qt.AlignmentFlag.AlignLeft)

        height_label = QLabel()
        height_label.setText("height: ")
        height_label.setStyleSheet("color: white")

        self.height_number.setMinimum(100)
        self.height_number.setMaximum(10000)
        self.height_number.setStyleSheet("color: white")

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
        self.directory_edit.setStyleSheet("color: white;")
        self.directory_edit.textEdited.connect(self.set_directory)

        directory_layout.addWidget(self.directory_button)
        directory_layout.addWidget(self.directory_edit)
        layout.addLayout(directory_layout)

    def start_section(self, layout: QBoxLayout):
        start_lay = QHBoxLayout()
        start_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.start_button.setText("Start")
        self.start_button.setStyleSheet("color: white;width: 150px;")
        self.start_button.pressed.connect(self.run)

        start_lay.addWidget(self.start_button)
        layout.addLayout(start_lay)

    def loading_page(self, layout: QStackedLayout):
        self.blackout.setStyleSheet("background-color: rgba(0,0,0,.3);")

        self.loading_gif = QMovie("icons/loading.gif")

        loading = QLabel()
        loading.setMovie(self.loading_gif)
        loading.move(self.window_size.width() // 2 - 16, self.window_size.height() // 2 - 16)
        loading.setFixedSize(32, 32)
        loading.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        loading.setParent(self.blackout)
        self.loading_gif.start()

        layout.addWidget(self.blackout)
