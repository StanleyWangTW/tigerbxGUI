from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QListWidget, QListWidgetItem, QSizePolicy, QTabWidget
from PySide6.QtGui import QImage, QPixmap
import numpy as np

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class Label(QWidget):
    def __init__(self, number, name, rgba) -> None:
        super().__init__()
        self.number = QLabel(str(number))
        self.name = QLabel(name)
        self.rgba = rgba
        self.color_square = QLabel()
        self.init_ui()

    def init_ui(self):
        def rgb_square(width, height, rgb):
            square = np.zeros((width, height, 3))
            for c in range(3):
                square[..., c] = rgb[c]

            return square

        self.number.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        square = rgb_square(10, 10, self.rgba[:-1])
        pixmap = QPixmap.fromImage(QImage(square.astype(np.uint8),
                                          square.shape[0],
                                          square.shape[1],
                                          square.shape[1] * 3,
                                          QImage.Format_RGB888))
        self.color_square.setPixmap(pixmap)
        self.color_square.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout()
        layout.addWidget(self.number)
        layout.addWidget(self.color_square)
        layout.addWidget(QVLine())
        layout.addWidget(self.name)
        self.setLayout(layout)


class  LabelList(QListWidget):
    def __init__(self):
        super(LabelList, self).__init__()
        self.setLayout(QVBoxLayout())

    # def addLabel(self, number, name, rgba):
    #     row = Label(number, name, rgba)
    #     item = QListWidgetItem(self)
    #     item.setSizeHint(row.minimumSizeHint())
    #     self.addItem(item)
    #     self.setItemWidget(item, row)

    def addLabel(self, number, label):
        row = Label(number, label.name, label.rgba)
        item = QListWidgetItem(self)
        item.setSizeHint(row.minimumSizeHint())
        self.addItem(item)
        self.setItemWidget(item, row)


class LeftWidget(QTabWidget):
    def __init__(self):
        super(LeftWidget, self).__init__()
        self.setTabShape(self.TabShape.Rounded)