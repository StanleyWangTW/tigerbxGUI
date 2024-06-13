from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import numpy as np

class MyText(QGraphicsTextItem):
    def __init__(self, text, font, s, color):
        super().__init__(text)
        self.setFont(QFont(font, s))
        self.setDefaultTextColor(color)


class MyPixmapItem(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()


class SliceViewer(QWidget):
    def __init__(self, texts):
        super().__init__()
        self.viewer = NewCanvas(texts)
        self.full_screen_btn = QPushButton(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.viewer)
        hbox.addWidget(self.full_screen_btn) 
        self.setLayout(hbox)


class NewCanvas(QGraphicsView):
    def __init__(self, texts):
        super().__init__()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 400, 400)

        self.texts = []
        for text in texts:
            self.texts.append(MyText(text, 'Arial', 24, QColor(255, 255, 0, 255)))
            self.scene.addItem(self.texts[-1])

        self.initUI()

        self.image_data = nib.load(r'test_file\CANDI_BPDwoPsy_030.nii.gz').get_fdata()[170, ...].astype(np.uint8)
        height, width  = self.image_data.shape

        self.pixmap = MyPixmapItem()
        self.pixmap.setPixmap(QPixmap.fromImage(QImage(np.ascontiguousarray(self.image_data), width, height, QImage.Format_Grayscale8)))
        self.pixmap.setPos(0, 0)
        self.scene.addItem(self.pixmap)

        # self.line = QGraphicsLineItem(0, 0, 400, 0)
        # self.line2 = QGraphicsLineItem(0, 0, 400, 0)
        # pen = QPen(Qt.blue)
        # pen.setStyle(Qt.DashLine)  # 设置虚线风格
        # self.line.setPen(pen)
        # self.line2.setPen(pen)
        # self.scene.addItem(self.line)
        # self.scene.addItem(self.line2)

        self.view_size = self.size()
        self.setScene(self.scene)

    def initUI(self):
        self.setBackgroundBrush(QColor(0, 0, 0, 255))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMouseTracking(False)

    def resizeEvent(self, event):
        h, w = self.image_data.shape
        self.scene.setSceneRect(QRectF(QPointF(0, 0), event.size()))
        # self.pixmap.setPos(self.size().width() // 2 - w//2, self.size().height() // 2 - h//2)

        self.view_size = self.size()
        ww = self.view_size.width()
        hh = self.view_size.height()
        scale_x = (self.view_size.width() - 2*self.texts[0].boundingRect().width()) / w
        scale_y = (self.view_size.height() - 2*self.texts[0].boundingRect().height()) / h
        scale_factor = min(scale_x, scale_y)

        self.setMinimumSize(w + 2*self.texts[0].boundingRect().width(), h + 2*self.texts[0].boundingRect().height())
        self.pixmap.setScale(scale_factor)
        self.pixmap.setPos(QPointF((ww - w * scale_factor) // 2, (hh - h * scale_factor) // 2))

        self.write_text()
        # self.line.setLine(0, 0, self.view_size.width(), 0)
        # self.line2.setLine(0, 0, 0, self.view_size.height())

    def write_text(self):
        AlignLeft(self.texts[0], self)
        HorizontalCenter(self.texts[0], self)
        self.texts[1].setPos(QPointF(self.view_size.width() - self.texts[1].boundingRect().width(),  self.view_size.height() / 2))
        self.texts[2].setPos(QPointF(self.view_size.width() / 2, self.view_size.height() - self.texts[3].boundingRect().height()))
        self.texts[3].setPos(QPointF(0, self.view_size.height() / 2))

    def mouseMoveEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            print('a')
        x, y = event.position().x(), event.position().y()

        x = self.pixmap.pos().x() if x < self.pixmap.pos().x() else x
        y = self.pixmap.pos().y() if y < self.pixmap.pos().y() else y

        # self.line.setPos(0, y)
        # self.line2.setPos(x, 0)

def AlignLeft(item, view):
    item.setPos(0, item.pos().y())

def AlignRight(item, view):
    item.setPos(0, item.pos().y())

def HorizontalCenter(item, view):
    item.setPos(QPointF(view.size().width() / 2, item.pos().y()))

def VetricalCenter(item, view):
    item.setPos(QPointF(item.pos().x(), view.size().height() / 2))

# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
#         layout = QGridLayout()
#         layout.addWidget(NewCanvas(), 0, 0)
#         layout.addWidget(NewCanvas(), 0, 1)
#         layout.addWidget(NewCanvas(), 1, 0)
#         self.setLayout(layout)


if __name__ == "__main__":
    import sys
    import nibabel as nib
    app = QApplication(sys.argv)
    win = SliceViewer(['S', 'A', 'R', 'P'])
    # win = Window()
    win.show()
    app.exec()