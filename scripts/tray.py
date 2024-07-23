from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu


class AppTray(QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setIcon(QIcon("icons/icon.png"))

    def add_tray(self):
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show_action)
        hide_action.triggered.connect(self.hide_action)
        quit_action.triggered.connect(self.quit_action)
        tray_menu = QMenu()
        tray_menu.setStyleSheet("color: black;")
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.setContextMenu(tray_menu)
        self.show()

    def show_action(self):
        self.parent().show()

    def hide_action(self):
        self.parent().hide()

    def quit_action(self):
        self.parent().complete_close()
