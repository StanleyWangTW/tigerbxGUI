from PySide6 import QtWidgets


class FileList(QtWidgets.QListWidget):

    def __init__(self):
        super(FileList, self).__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
