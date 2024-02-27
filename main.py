import sys

from PySide6.QtWidgets import QApplication

from view import MainWindow

app = QApplication(sys.argv)

window = MainWindow(app)
window.show()

app.exec()