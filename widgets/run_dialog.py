from PySide6 import QtWidgets
import PySide6.QtCore as Qt


class RunDialog(QtWidgets.QDialog):

    def __init__(self, fnum=None):
        super(RunDialog, self).__init__()
        self.value = 0
        self.setup_ui(fnum)

        self.timer = Qt.QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def setup_ui(self, fnum):
        self.setWindowTitle('Running')
        v_layout = QtWidgets.QVBoxLayout()

        self.pbar = QtWidgets.QProgressBar()
        self.pbar.setValue(1)
        v_layout.addWidget(self.pbar)
        self.setLayout(v_layout)

        # self.pbar.valueChanged.connect(self.finish)

    def update_progress(self):
        self.value += 1
        self.pbar.setValue(self.value + 1)

    # def finish(self, value):
    #     self.done()
    # if value == self.pbar.maximum():
    # self.accept()
