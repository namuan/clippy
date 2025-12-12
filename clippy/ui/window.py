import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from .settings import Settings
from ..core.worker import PetWorker, load_pets
from ..utils.paths import LOGO_DIR

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.setWindowTitle("Pet Manager")
        self.resize(800, 600)
        self.setWindowIcon(QtGui.QIcon(LOGO_DIR))

        app_icon = QtGui.QIcon(LOGO_DIR)
        app.setWindowIcon(app_icon)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.settings = Settings(self)
        layout.addWidget(self.settings)

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(LOGO_DIR))

        show_action = QtGui.QAction("Show", self)
        refresh_action = QtGui.QAction("Refresh", self)
        quit_action = QtGui.QAction("Quit", self)

        show_action.triggered.connect(self.show_window)
        refresh_action.triggered.connect(self.start_refresh)
        quit_action.triggered.connect(QtWidgets.QApplication.instance().quit)

        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(refresh_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.show()

        self.pets = []
        self.worker = None
        self.start_refresh()

    def start_refresh(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()

        for pet in getattr(self, "pets", []):
            pet.close()

        self.pets = load_pets()
        self.worker = PetWorker(self.pets)
        self.worker.start()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Pet Manager",
            "Application minimized to tray",
            QtWidgets.QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()
