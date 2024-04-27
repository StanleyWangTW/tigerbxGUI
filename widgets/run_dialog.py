import os

from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


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

        self.pbar = QtWidgets.QProgressBar()
        self.pbar.setValue(0)
        self.pbar.setMaximum(self.fnum)

        v_layout = QtWidgets.QVBoxLayout()
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
            # finish_dialog = FinishDialog()
            # finish_dialog.exec()
            self.accept()


class FinishDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("finish")
        QBtn = QtWidgets.QDialogButtonBox.Ok
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.close)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel('Finished')
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class RunningDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('running')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.layout = QVBoxLayout(self)
        self.label = QLabel('Running segmentation...', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.finish_dialog = FinishDialog()

    def creating_csv(self):
        self.label.setText('Creating CSV reports...')
    
    def close(self) -> bool:
        self.finish_dialog.show()
        return super().close()