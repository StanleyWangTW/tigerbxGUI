import numpy as np
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt


class iFrame(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.image = None
        self.layers = [0, 0, 0]
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

    def set_layer(self, layer, i):
        if 0 <= layer < self.image.shape[i]:
            self.layers[i] = layer

    def set_layers(self, layers):
        for i in range(3):
            if 0 <= layers[i] < self.image.shape[i]:
                self.layers[i] = layers[i]

    def set_image(self, image):
        self.image = image
        self.set_layers(np.array(self.image.shape) // 2)
        self.update_image()

    def update_image(self):
        if self.image is not None:
            qImg2 = QtGui.QPixmap(
                QtGui.QImage(
                    np.ascontiguousarray(np.rot90(self.image[self.layers[0], :, :])),
                    self.image.shape[1],
                    self.image.shape[2],
                    QtGui.QImage.Format_Grayscale8))
            qImg2 = qImg2.scaled(self.sagittal.frameSize(),
                                 aspectMode=Qt.KeepAspectRatio)

            qImg1 = QtGui.QPixmap(
                QtGui.QImage(
                    np.ascontiguousarray(np.rot90(self.image[:, self.layers[1], :])),
                    self.image.shape[0],
                    self.image.shape[2],
                    QtGui.QImage.Format_Grayscale8))
            qImg1 = qImg1.scaled(self.coronal.frameSize(),
                                 aspectMode=Qt.KeepAspectRatio)
            
            qImg3 = QtGui.QPixmap(
                QtGui.QImage(
                    np.ascontiguousarray(np.rot90(self.image[:, :, self.layers[2]])),
                    self.image.shape[0],
                    self.image.shape[1],
                    QtGui.QImage.Format_Grayscale8))
            qImg3 = qImg3.scaled(self.axial.frameSize(),
                                 aspectMode=Qt.KeepAspectRatio)

            self.coronal.setPixmap(qImg1)
            self.sagittal.setPixmap(qImg2)
            self.axial.setPixmap(qImg3)


class Canvas(QtWidgets.QWidget):

    def __init__(self):
        super(Canvas, self).__init__()

        v_layout = QtWidgets.QVBoxLayout()
        self.setLayout(v_layout)

        self.disp1 = iFrame()
        v_layout.addWidget(self.disp1, 1)
        self.disp2 = iFrame()
        v_layout.addWidget(self.disp2, 1)
