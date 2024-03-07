from PySide6 import QtWidgets
import numpy as np


class iFrame(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.coronal = QtWidgets.QLabel()
        layout.addWidget(self.coronal)
        self.sagittal = QtWidgets.QLabel()
        layout.addWidget(self.sagittal)
        self.axial = QtWidgets.QLabel()
        layout.addWidget(self.axial)


class Canvas(QtWidgets.QWidget):

    def __init__(self):
        super(Canvas, self).__init__()

        v_layout = QtWidgets.QVBoxLayout()
        self.setLayout(v_layout)

        self.disp1 = iFrame()
        v_layout.addWidget(self.disp1)
        self.disp2 = iFrame()
        v_layout.addWidget(self.disp2)
