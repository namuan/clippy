import sys
from PyQt6 import QtWidgets
from .ui.window import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.hide()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
