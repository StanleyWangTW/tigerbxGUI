import numpy as np
from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QPixmap, Qt

from utils.display import color_show


class iFrame(QtWidgets.QLabel):

    def __init__(self, tool_bar):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.image = None
        self.scr = None
        self.overlay = None
        self.alpha = 0
        self.cmap = 'gray'
        self.minv = 0
        self.maxv = 255
        self.layers = [0, 0, 0]
        self.tool_bar = tool_bar

    def set_layer(self, layer, i):
        layer = int(layer)
        if 0 <= layer < self.image.shape[i]:
            self.layers[i] = layer

            if i==0:
                self.tool_bar.x_line.setValue(self.layers[0])
            elif i==1:
                self.tool_bar.y_line.setValue(self.layers[1])
            elif i==2:
                self.tool_bar.z_line.setValue(self.layers[2])
        
        self.update_image()

    def set_layers(self, layers):
        for i, layer in enumerate(layers):
            self.set_layer(layer, i)

    def set_image(self, image):
        self.image = image
        # RAS: R:0, A:1, S:2
        self.R = self.image.shape[0]
        self.A = self.image.shape[1]
        self.S = self.image.shape[2]
        self.set_layers(np.array(self.image.shape) // 2)
        self.update_image()

    def update_image(self):
        if self.image is not None:
            directions = [(slice(None, None, None), self.layers[1],          slice(None, None, None)),
                          (self.layers[0],          slice(None, None, None), slice(None, None, None)),
                          (slice(None, None, None), slice(None, None, None), self.layers[2])]

            self.scr = np.zeros([self.S + self.A + 1, self.R + self.A + 1, 3])
            for i, direction in enumerate(['coronal', 'sagittal', 'axial']):
                img_data = np.rot90(self.image[directions[i]])
                img_data = np.ones(img_data.shape) * img_data

                img_data = color_show(img_data, self.minv, self.maxv, self.cmap)

                if self.overlay is not None:
                    overlay = color_show(np.rot90(self.overlay[directions[i]]),
                                         np.min(self.overlay), np.max(self.overlay), 'copper')
                    overlay = np.ones(overlay.shape) * overlay

                    mask = np.sum(overlay, axis=2)
                    mask[mask > 0] = 1 - self.alpha
                    mask = np.stack([mask, ]*3, axis=2)
                    img_data = (1 - mask) * img_data + mask * overlay

                if i==0:
                    self.scr[0:self.S, 0:self.R, :] = img_data
                if i==1:
                    self.scr[0:self.S, self.R+1:self.R+1+self.A, :] = img_data
                if i==2:
                    self.scr[self.S+1:self.S+1+self.A, 0:self.R, :] = img_data

            self.paint()

    def paint(self):
        if self.scr is not None:
            pixmap = QPixmap.fromImage(
                QtGui.QImage(
                    self.scr.astype(np.uint8),
                    self.scr.shape[1],
                    self.scr.shape[0],
                    self.scr.shape[1] * 3,
                    QtGui.QImage.Format_RGB888
                )
            )
            pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.setPixmap(pixmap)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.paint()
        return super().resizeEvent(event)
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        x, y = event.pos().x(), event.pos().y()

        x = int(x * self.scr.shape[1]/self.pixmap().size().width())
        y = int(y * self.scr.shape[0]/self.pixmap().size().height())
        
        if 0 <= x < self.R and 0 <= y < self.S: # mouse in coronal plane
            self.set_layer(x, 0)
            self.set_layer(self.S-y-1, 2)

        elif self.R < x <= (self.R + self.A) and 0 <= y < self.S: # mouse in sagittal plane
            x = x - self.R - 1
            self.set_layer(x, 1)
            self.set_layer(self.S-y-1, 2)

        elif 0 <= x < self.R and self.S < y <= self.S + self.A: # mouse in axial plane
            y = y - self.S - 1
            self.set_layer(x, 0)
            self.set_layer(self.A-y-1, 1)

        return super().mouseMoveEvent(event)
    
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        x, y = event.position().x(), event.position().y()

        x = int(x * self.scr.shape[1]/self.pixmap().size().width())
        y = int(y * self.scr.shape[0]/self.pixmap().size().height())

        if 0 <= x < self.R and 0 <= y < self.S: # mouse in coronal plane
            angle = 1 if event.angleDelta().y() > 0 else -1
            self.set_layer(angle + self.layers[1], 1)

        elif self.R < x <= (self.R + self.A) and 0 <= y < self.S: # mouse in sagittal plane
            angle = 1 if event.angleDelta().y() > 0 else -1
            self.set_layer(angle + self.layers[0], 0)

        elif 0 <= x < self.R and self.S < y <= self.S + self.A: # mouse in axial plane
            angle = 1 if event.angleDelta().y() > 0 else -1
            self.set_layer(angle + self.layers[2], 2)

        return super().wheelEvent(event)


class Canvas(QtWidgets.QWidget):

    def __init__(self, tool_bar):
        super(Canvas, self).__init__()

        self.disp1 = iFrame(tool_bar)
        self.disp2 = iFrame(tool_bar)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.disp1, 1)
        self.setLayout(layout)