import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import mahotas

from utils.display import color_show
from utils.qt import newIcon


class iFrame(QtWidgets.QWidget):

    def __init__(self, tool_bar):
        super().__init__()
        # self.setStyleSheet("background-color: black;")
        # self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.image = None
        self.scr = None
        self.overlay = None
        self.draw = True # draw label flag
        self.coords = [] # coords for polygon drawing
        self.alpha = 0
        self.cmap = 'gray'
        self.overlay_cmap = 'freesurfer'
        self.minv = 0
        self.maxv = 0
        self.layers = [0, 0, 0]
        self.tool_bar = tool_bar
        self.mode = 'crosshair'

        self.viewers = [SliceViewer(self, slice_type='coronal'), SliceViewer(self, slice_type='sagittal'), SliceViewer(self, slice_type='axial')]
        layout = QGridLayout()
        layout.addWidget(self.viewers[0], 0, 0)
        layout.addWidget(self.viewers[1], 0, 1)
        layout.addWidget(self.viewers[2], 1, 0)
        self.setLayout(layout)
        self.disply_mode = 3
        self.viewers[0].full_screen_btn.clicked.connect(self.coronal_full_screen)
        self.viewers[1].full_screen_btn.clicked.connect(self.sagittal_full_screen)
        self.viewers[2].full_screen_btn.clicked.connect(self.axial_full_screen)
        
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
        for i in range(3):
            layers[i] = int(layers[i])
            if 0 <= layers[i] < self.image.shape[i]:
                self.layers[i] = layers[i]

        self.tool_bar.x_line.setValue(self.layers[0])
        self.tool_bar.y_line.setValue(self.layers[1])
        self.tool_bar.z_line.setValue(self.layers[2])
        self.update_image()

    def set_image(self, image):
        self.image = image
        self.minv = np.min(self.image)
        self.maxv = np.max(self.image)
        self.tool_bar.minv.setValue(self.minv)
        self.tool_bar.maxv.setValue(self.maxv)
        # RAS: R:0, A:1, S:2
        self.R = self.image.shape[0]
        self.A = self.image.shape[1]
        self.S = self.image.shape[2]
        self.set_layers(np.array(self.image.shape) // 2)

    def show_cross(self, img, plane):
        color = np.array([0, 0, 255]) # blue

        if plane == 'coronal':
            img[self.S - self.layers[2] - 1, :, :] = color # row 
            img[:, self.layers[0], :] = color # col

        elif plane == 'sagittal':
            img[self.S - self.layers[2] - 1, :, :] = color # row 
            img[:, self.layers[1], :] = color # col

        elif plane == 'axial':
            img[self.A - self.layers[1] - 1, :, :] = color # row 
            img[:, self.layers[0], :] = color # col

        return img


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
                                         np.min(self.overlay), np.max(self.overlay), self.overlay_cmap)
                    overlay = np.ones(overlay.shape) * overlay

                    mask = np.sum(overlay, axis=2)
                    mask[mask > 0] = 1 - self.alpha
                    mask = np.stack([mask, ]*3, axis=2)
                    img_data = (1 - mask) * img_data + mask * overlay

                img_data = self.show_cross(img_data, direction)

                self.viewers[i].set_image(img_data)

    def crosshair_mode(self):
        self.mode = 'crosshair'
        print(self.mode)

    def zoom_mode(self):
        self.mode = 'zoom'
        print(self.mode)
    
    # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    #     if self.draw:

    #         if event.button() == QtCore.Qt.LeftButton:
    #             x, y = event.position().x(), event.position().y()
    #             x = int(x * self.scr.shape[1]/self.pixmap().size().width())
    #             y = int(y * self.scr.shape[0]/self.pixmap().size().height())

    #             if 0 <= x < self.R and 0 <= y < self.S: # mouse in coronal plane
    #                 self.coords.append([x, self.S - y - 1])

    #         elif event.button() == QtCore.Qt.RightButton:
    #             mahotas.polygon.fill_polygon(self.coords, self.image[:, self.layers[1], :], color=self.tool_bar.pen_label)
    #             self.coords.clear()

    #         self.update_image()

    def coronal_full_screen(self):
        if self.disply_mode == 3:
            self.hide_viewers((1, 2))
            self.disply_mode = 0
            self.viewers[0].full_screen_btn.setIcon(newIcon('menu'))

        elif self.disply_mode == 0:
            self.show_3_viewers()
            self.disply_mode = 3
            self.viewers[0].full_screen_btn.setIcon(newIcon('letter-c'))
            
    def sagittal_full_screen(self):
        if self.disply_mode == 3:
            self.hide_viewers((0, 2))
            self.disply_mode = 0
            self.viewers[1].full_screen_btn.setIcon(newIcon('menu'))
            
        elif self.disply_mode == 0:
            self.show_3_viewers()
            self.disply_mode = 3
            self.viewers[1].full_screen_btn.setIcon(newIcon('letter-s'))
    
    def axial_full_screen(self):
        if self.disply_mode == 3:
            self.hide_viewers((0, 1))
            self.disply_mode = 0
            self.viewers[2].full_screen_btn.setIcon(newIcon('menu'))
            
        elif self.disply_mode == 0:
            self.show_3_viewers()
            self.disply_mode = 3
            self.viewers[2].full_screen_btn.setIcon(newIcon('letter-a'))

    def hide_viewers(self, slice_index):
        for i in slice_index:
            self.viewers[i].hide()

    def show_3_viewers(self):
        for viewer in self.viewers:
                viewer.show()

    # def enterEvent(self, event):
    #     self.setCursor(Qt.CrossCursor)

    # def leaveEvent(self, event):
    #     self.setCursor(Qt.ArrowCursor)


class Canvas(QtWidgets.QWidget):

    def __init__(self, tool_bar):
        super(Canvas, self).__init__()

        self.disp1 = iFrame(tool_bar)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.disp1, 1)
        self.setLayout(layout)


class SliceViewer(QWidget):
    def __init__(self, parent, image_data=np.zeros((255, 255, 3)), slice_type=None):
        super().__init__()
        self.slice_type = slice_type
        self.viewer = NewCanvas(parent, image_data, slice_type=slice_type)
        self.full_screen_btn = QPushButton(self)

        if self.slice_type == 'coronal':
            self.full_screen_btn.setIcon(newIcon('letter-c'))
        if self.slice_type == 'sagittal':
            self.full_screen_btn.setIcon(newIcon('letter-s'))
        if self.slice_type == 'axial':
            self.full_screen_btn.setIcon(newIcon('letter-a'))

        hbox = QHBoxLayout()
        hbox.addWidget(self.viewer)
        hbox.addWidget(self.full_screen_btn) 
        self.setLayout(hbox)

    def set_image(self, image):
        self.viewer.set_image(image)


class NewCanvas(QGraphicsView):
    def __init__(self, parent, image_data, slice_type):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 400, 400)
        self.slice_type = slice_type
        self.mouse_start_pos = None
        self.zoom_factor = 1
        self.pan_pos = QPointF(0, 0)
        self.drag_flag = False
        # self.line_x = 200
        # self.line_y = 200

        self.image_data = image_data
        height, width, _  = self.image_data.shape
        self.scale_factor = 1

        self.pixmap = MyPixmapItem()
        self.pixmap.setPixmap(QPixmap.fromImage(QImage(np.ascontiguousarray(self.image_data), width, height, QImage.Format_Grayscale8)))
        self.pixmap.setPos(0, 0)
        self.scene.addItem(self.pixmap)

        # self.line = QGraphicsLineItem(0, 0, 400, 0)
        # self.line2 = QGraphicsLineItem(0, 0, 400, 0)
        # pen = QPen(Qt.blue)
        # pen.setStyle(Qt.DashLine)
        # self.line.setPen(pen)
        # self.line2.setPen(pen)
        # self.scene.addItem(self.line)
        # self.scene.addItem(self.line2)

        texts = []
        if self.slice_type == 'coronal':
            texts = ['S', 'L', 'I', 'R']
        if self.slice_type == 'sagittal':
            texts = ['S', 'A', 'I', 'P']
        if self.slice_type == 'axial':
            texts = ['A', 'L', 'P', 'R']

        self.texts = []
        for text in texts:
            self.texts.append(MyText(text, 'Arial', 24, QColor(255, 255, 0, 255)))
            self.scene.addItem(self.texts[-1])

        self.initUI()

        self.view_size = self.size()
        self.setScene(self.scene)

    def initUI(self):
        self.setBackgroundBrush(QColor(0, 0, 0, 255))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMouseTracking(False)

    def set_image(self, image):
        self.image_data = image
        height, width, _  = self.image_data.shape
        self.pixmap.setPixmap(QPixmap.fromImage(
            QImage(self.image_data.astype(np.uint8),
                   width,
                   height,
                   width*3,
                   QImage.Format_RGB888)
            )
        )

    def resizeEvent(self, event):
        self.resize()

    def resize(self):
        # resize scene
        self.scene.setSceneRect(QRectF(QPointF(0, 0), self.size()))

        # calculate scale factor
        h, w, _ = self.image_data.shape
        self.view_size = self.size()
        ww = self.view_size.width()
        hh = self.view_size.height()
        scale_x = (self.view_size.width() - 2*self.texts[0].boundingRect().width()) / w
        scale_y = (self.view_size.height() - 2*self.texts[0].boundingRect().height()) / h
        self.scale_factor = min(scale_x, scale_y)
        factor = self.scale_factor * self.zoom_factor

        # scale pixmap
        self.pixmap.setScale(factor)
        self.pixmap.setPos(QPointF((ww - w * factor) // 2 + self.pan_pos.x(), (hh - h * factor) // 2 + self.pan_pos.y()))

        # set view minimum size by pixmap size
        self.setMinimumSize(w + 2*self.texts[0].boundingRect().width(), h + 2*self.texts[0].boundingRect().height())

        # write text after resize view
        self.write_text()

    def write_text(self):
        AlignLeft(self.texts[0], self)
        HorizontalCenter(self.texts[0], self)
        self.texts[1].setPos(QPointF(self.view_size.width() - self.texts[1].boundingRect().width(),  self.view_size.height() / 2))
        self.texts[2].setPos(QPointF(self.view_size.width() / 2, self.view_size.height() - self.texts[3].boundingRect().height()))
        self.texts[3].setPos(QPointF(0, self.view_size.height() / 2))

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        iframe = self.parent().parent()
        mode = iframe.mode
        if iframe.image is not None:
            if self.drag_flag:
                if mode == 'crosshair':
                    x, y = event.pos().x(), event.pos().y()

                    pixmap_x = self.pixmap.pos().x()
                    pixmap_y = self.pixmap.pos().y()

                    x = int((x - pixmap_x) / (self.scale_factor * self.zoom_factor))
                    y = int((y - pixmap_y) / (self.scale_factor * self.zoom_factor))

                    factor = (self.scale_factor * self.zoom_factor)
                    # self.line_x = pixmap_x + x*factor + factor / 2
                    # self.line_y = pixmap_y + y*factor + factor / 2
                    # self.line.setLine(0, self.line_y, self.view_size.width(), self.line_y)
                    # self.line2.setLine(self.line_x, 0, self.line_x, self.view_size.height())

                    if self.slice_type == 'coronal': # mouse in coronal plane
                        iframe.set_layer(x, 0)
                        iframe.set_layer(iframe.S-y-1, 2)

                    elif self.slice_type == 'sagittal': # mouse in sagittal plane
                        iframe.set_layer(x, 1)
                        iframe.set_layer(iframe.S-y-1, 2)

                    elif self.slice_type == 'axial': # mouse in axial plane
                        iframe.set_layer(x, 0)
                        iframe.set_layer(iframe.A-y-1, 1)
                
                elif mode == 'zoom':
                    self.zoom(event)

    def mousePressEvent(self, event):
            mode = self.parent().parent().mode
            self.drag_flag = True
            if mode == 'zoom':
                if event.buttons() & Qt.LeftButton:
                    self.mouse_start_pos = event.pos()
                elif event.buttons() & Qt.RightButton:
                    self.mouse_start_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self.drag_flag = False
        self.mouse_start_pos = None

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        ifame = self.parent().parent()
        if self.slice_type == 'coronal': # mouse in coronal plane
            angle = 1 if event.angleDelta().y() > 0 else -1
            ifame.set_layer(angle + ifame.layers[1], 1)
        
        elif self.slice_type == 'sagittal': # mouse in sagitall plane
            angle = 1 if event.angleDelta().y() > 0 else -1
            ifame.set_layer(angle + ifame.layers[0], 0)

        elif self.slice_type == 'axial': # mouse in axial plane
            angle = 1 if event.angleDelta().y() > 0 else -1
            ifame.set_layer(angle + ifame.layers[2], 2)

    def zoom(self, event):
        dx = event.pos().x() - self.mouse_start_pos.x()
        dy = event.pos().y() - self.mouse_start_pos.y()

        if event.buttons() & Qt.LeftButton:
            self.pan_pos = QPointF(self.pan_pos.x() + dx, self.pan_pos.y() + dy)

        elif event.buttons() & Qt.RightButton:
            self.zoom_factor -= dy / 100
            if self.zoom_factor * self.scale_factor < 1:
                self.zoom_factor = 1 / self.scale_factor

        self.resize()
        self.mouse_start_pos = event.pos()


class MyText(QGraphicsTextItem):
    def __init__(self, text, font, s, color):
        super().__init__(text)
        self.setFont(QFont(font, s))
        self.setDefaultTextColor(color)


class MyPixmapItem(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()


def AlignLeft(item, view):
    item.setPos(0, item.pos().y())

def AlignRight(item, view):
    item.setPos(0, item.pos().y())

def HorizontalCenter(item, view):
    item.setPos(QPointF(view.size().width() / 2, item.pos().y()))

def VetricalCenter(item, view):
    item.setPos(QPointF(item.pos().x(), view.size().height() / 2))