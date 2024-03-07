import sys

from PySide6 import QtWidgets
from widgets import MainWindow

app = QtWidgets.QApplication(sys.argv)

window = MainWindow(app)
window.show()

sys.exit(app.exec())
