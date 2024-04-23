import numpy as np
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt

from utils.display import color_show


class iFrame(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        # self.setStyleSheet("background-color: black;")

        self.image = None
        self.overlay = None
        self.alpha = 0
        self.cmap = 'gray'
        self.minv = 0
        self.maxv = 255
        self.layers = [0, 0, 0]
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        labels = ['coronal', 'sagittal', 'axial']
        for label_name in labels:
            label = QtWidgets.QLabel()
            setattr(self, label_name, label)
            label.setMinimumHeight(100)
            label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding)
            # label.setStyleSheet("background-color: black;")
            if not label_name == 'axial':
                layout.addWidget(label)
            label.mouseMoveEvent = self.mouseMoveEvent

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
            directions = [(slice(None, None, None), self.layers[1],          slice(None, None, None)),
                          (self.layers[0],          slice(None, None, None), slice(None, None, None)),
                          (slice(None, None, None), slice(None, None, None), self.layers[2])]

            for i, direction in enumerate(['coronal', 'sagittal', 'axial']):
                img_data = np.rot90(self.image[directions[i]])
                img_data = np.ones(img_data.shape) * img_data
                qImg = color_show(img_data, self.minv, self.maxv, self.cmap)

                if self.overlay is not None:
                    overlay = color_show(np.rot90(self.overlay[directions[i]]),
                                         np.min(self.overlay), np.max(self.overlay), 'copper')
                    overlay = np.ones(overlay.shape) * overlay

                    mask = np.sum(overlay, axis=2)
                    mask[mask > 0] = 1 - self.alpha
                    mask = np.stack([mask, ]*3, axis=2)
                    qImg = (1 - mask) * qImg + mask * overlay

                qImg = QtGui.QImage(qImg.astype(np.uint8),
                                    img_data.shape[1],
                                    img_data.shape[0],
                                    img_data.shape[1] * 3,
                                    QtGui.QImage.Format_RGB888)
                qImg = qImg.scaled(getattr(self, direction).frameSize(), aspectMode=Qt.KeepAspectRatio)

                getattr(self, direction).setPixmap(QtGui.QPixmap.fromImage(qImg))


class Canvas(QtWidgets.QWidget):

    def __init__(self):
        super(Canvas, self).__init__()

        self.disp1 = iFrame()
        self.disp2 = iFrame()

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.disp1, 1)
        self.setLayout(layout)
