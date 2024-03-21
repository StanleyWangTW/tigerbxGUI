import os

from PySide6 import QtWidgets
import PySide6.QtCore as Qt


class RunDialog(QtWidgets.QDialog):

    def __init__(self, fnum, output_dir):
        super(RunDialog, self).__init__()
        self.output_dir = output_dir
        self.fnum = fnum
        self.setup_ui()

        self.timer = Qt.QTimer(self)
        self.timer.timeout.connect(self.check_progress)
        self.timer.start(100)

    def setup_ui(self):
        self.setWindowTitle(f'Running 1 of {self.fnum}')
        v_layout = QtWidgets.QVBoxLayout()

        self.pbar = QtWidgets.QProgressBar()
        self.pbar.setValue(0)
        self.pbar.setMaximum(self.fnum)
        v_layout.addWidget(self.pbar)
        self.setLayout(v_layout)

        self.pbar.valueChanged.connect(self.if_finish)

    def check_progress(self):
        num_of_files = len(os.listdir(self.output_dir))
        if num_of_files != self.pbar.value():
            self.update_progress(num_of_files)

    def update_progress(self, num_of_files):
        self.pbar.setValue(len(os.listdir(self.output_dir)))
        self.setWindowTitle(f'Running {self.pbar.value() + 1} of {self.fnum}')

    def if_finish(self, value):
        if value == self.pbar.maximum():
            finish_dialog = FinishDialog()
            finish_dialog.exec()
            self.accept()


class FinishDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("FINISH")
        QBtn = QtWidgets.QDialogButtonBox.Ok
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel('Segmentation finished')
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
