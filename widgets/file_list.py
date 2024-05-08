from PySide6.QtWidgets import QListWidget, QVBoxLayout


class FileList(QListWidget):
    def __init__(self):
        super(FileList, self).__init__()