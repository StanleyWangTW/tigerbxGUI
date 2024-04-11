import numpy as np
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt

from utils.display import color_show


class iFrame(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.image = None
        self.cmap = 'gray'
        self.minv = 0
        self.maxv = 255
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
        layer = int(layer)
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
            qImg1 = np.ascontiguousarray(np.rot90(self.image[:, self.layers[1], :]))
            qImg1 = QtGui.QImage(color_show(qImg1, self.minv, self.maxv, self.cmap),
                                 self.image.shape[0],
                                 self.image.shape[2],
                                 self.image.shape[2] * 3,
                                 QtGui.QImage.Format_RGB888)
            qImg1 = qImg1.scaled(self.coronal.frameSize(), aspectMode=Qt.KeepAspectRatio)

            qImg2 = np.ascontiguousarray(np.rot90(self.image[self.layers[0], :, :]))
            qImg2 = QtGui.QImage(color_show(qImg2, self.minv, self.maxv, self.cmap),
                                 self.image.shape[1],
                                 self.image.shape[2],
                                 self.image.shape[1] * 3,
                                 QtGui.QImage.Format_RGB888)
            qImg2 = qImg2.scaled(self.sagittal.frameSize(), aspectMode=Qt.KeepAspectRatio)

            qImg3 = np.ascontiguousarray(np.rot90(self.image[:, :, self.layers[2]]))
            qImg3 = QtGui.QImage(color_show(qImg3, self.minv, self.maxv, self.cmap),
                                 self.image.shape[0],
                                 self.image.shape[1],
                                 self.image.shape[0] * 3,
                                 QtGui.QImage.Format_RGB888)
            qImg3 = qImg3.scaled(self.axial.frameSize(), aspectMode=Qt.KeepAspectRatio)

            self.coronal.setPixmap(QtGui.QPixmap.fromImage(qImg1))
            self.sagittal.setPixmap(QtGui.QPixmap.fromImage(qImg2))
            self.axial.setPixmap(QtGui.QPixmap.fromImage(qImg3))


class Canvas(QtWidgets.QWidget):

    def __init__(self):
        super(Canvas, self).__init__()

        v_layout = QtWidgets.QVBoxLayout()
        self.setLayout(v_layout)

        self.disp1 = iFrame()
        v_layout.addWidget(self.disp1, 1)
        self.disp2 = iFrame()
        v_layout.addWidget(self.disp2, 1)
