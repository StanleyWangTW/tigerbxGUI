import argparse
import sys

from PySide6 import QtWidgets

from widgets import MainWindow
from utils import newIcon

__appname__ = "TigerBX"
__version__ = "0.0.4"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", "-V", action="store_true", help="show version")
    args = parser.parse_args()

    if args.version:
        print(f"{__appname__} {__version__}")
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(newIcon("icon"))
    app.setApplicationName(__appname__)
    window = MainWindow(app)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()