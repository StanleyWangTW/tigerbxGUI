from PySide6 import QtWidgets


class iFrame(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.coronal = QtWidgets.QLabel()
        self.coronal.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.coronal)

        self.sagittal = QtWidgets.QLabel()
        self.sagittal.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.sagittal)

        self.axial = QtWidgets.QLabel()
        self.axial.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.axial)

        self.coronal.mouseMoveEvent = self.mouseMoveEvent
        self.sagittal.mouseMoveEvent = self.mouseMoveEvent
        self.axial.mouseMoveEvent = self.mouseMoveEvent


class Canvas(QtWidgets.QWidget):

    def __init__(self):
        super(Canvas, self).__init__()

        v_layout = QtWidgets.QVBoxLayout()
        self.setLayout(v_layout)

        self.disp1 = iFrame()
        v_layout.addWidget(self.disp1, 1)
        self.disp2 = iFrame()
        v_layout.addWidget(self.disp2, 1)
