from functools import partial

import numpy as np
import nibabel as nib
from nilearn.image import resample_to_img
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import mahotas

from utils.display import color_show, overlay_color_show
from utils.qt import newIcon


class Canvas(QtWidgets.QWidget):

    def __init__(self, tool_bar, label_editor):
        super().__init__()
        self.initUI(tool_bar, label_editor)

        self.image = None                   # np.array of selected nii
        self.overlay = None                 # np.array of overlay nii
        self.image_display = None           # RGBA array of image for display
        # self.alpha = 0                      # alpha value of overlay
        self.image_cmap = 'gray'            # cmap of image
        # self.overlay_cmap = 'freesurfer'    # cmap of overlay
        self.minv = 0                       # min display value of image
        self.maxv = 0                       # max display value of image
        self.layers = [0, 0, 0]             # coordinate of slices of 3 planes
        self.display_mode = 3               # display mode of SliceViewers

        self.mode = 'crosshair'             # current selected tool
        self.brush_size = self.label_editor.brush_editor.brush_size_spnbox.value() # brush size of brush tool

    def initUI(self, tool_bar, label_editor):
        layout = QGridLayout()
        self.setLayout(layout)

        self.viewers = [                    # SliceViewers of 3 planes
            SliceViewer(self, slice_type='coronal'),
            SliceViewer(self, slice_type='sagittal'),
            SliceViewer(self, slice_type='axial')
        ]
        layout.addWidget(self.viewers[0], 0, 0)
        layout.addWidget(self.viewers[1], 0, 1)
        layout.addWidget(self.viewers[2], 1, 0)

        self.viewers[0].full_screen_btn.clicked.connect(self.coronal_full_screen)
        self.viewers[1].full_screen_btn.clicked.connect(self.sagittal_full_screen)
        self.viewers[2].full_screen_btn.clicked.connect(self.axial_full_screen)

        # other input widgets' connect
        self.tool_bar = tool_bar            # tool bar of mainwindow
        self.tool_bar.minv.valueChanged.connect(self.set_minv)
        self.tool_bar.maxv.valueChanged.connect(self.set_maxv)
        self.tool_bar.cmap_combobox.currentTextChanged.connect(self.set_image_cmap)
        self.tool_bar.x_line.valueChanged.connect(partial(self.set_layer, i=0))
        self.tool_bar.y_line.valueChanged.connect(partial(self.set_layer, i=1))
        self.tool_bar.z_line.valueChanged.connect(partial(self.set_layer, i=2))

        self.label_editor = label_editor
        self.label_editor.crosshair_btn.clicked.connect(self.set_mode)
        self.label_editor.zoom_btn.clicked.connect(self.set_mode)
        self.label_editor.brush_btn.clicked.connect(self.set_mode)
        self.label_editor.brush_editor.brush_size_spnbox.valueChanged.connect(self.set_brush_size)

    def set_layer(self, layer: int, i: int):
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

    def set_minv(self, minv):
        self.minv = minv
        self.tool_bar.minv.setValue(self.minv)
        self.update_image_display()

    def set_maxv(self, maxv):
        self.maxv = maxv
        self.tool_bar.maxv.setValue(self.maxv)
        self.update_image_display()

    def set_image_cmap(self, cmap):
        self.image_cmap = cmap
        self.update_image_display()

    def set_image(self, image):
        self.image = image
        self.R = self.image.shape[0] # RAS: R:0, A:1, S:2
        self.A = self.image.shape[1]
        self.S = self.image.shape[2]

        self.set_minv(np.min(self.image))
        self.set_maxv(np.max(self.image))
        self.update_image_display()

        self.overlay = np.zeros(self.image.shape)

        for i in range(3):
            self.set_layer(np.array(self.image.shape[i]) // 2, i)

    def update_image_display(self):
        self.image_display = color_show(self.image, self.minv, self.maxv, self.image_cmap)
        self.update_image()

    def set_overlay(self, overlay):
        self.overlay = overlay
        self.update_image()

    def clear_overlay(self):
        self.overlay = None if self.image is None else np.zeros(self.image.shape)
        for i in range(3):
            self.viewers[i].viewer.clear_overlay()
        self.update_image()

    def save_overlay(self, file_name, current_nii, current_nii_resp):
        if self.overlay is not None:
            output_nii = nib.Nifti1Image(self.overlay,
                                         affine=current_nii_resp.affine,
                                         header=current_nii_resp.header)
            output_nii = resample_to_img(output_nii, current_nii, interpolation='nearest')
            nib.save(output_nii, file_name)

    def set_brush_size(self, size):
        self.brush_size = size

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

            for i, direction in enumerate(['coronal', 'sagittal', 'axial']):
                img_data = np.ascontiguousarray(np.rot90(self.image_display[directions[i]]))
                # img_data = self.show_cross(img_data, direction)
                self.viewers[i].viewer.set_image(img_data)

                if self.overlay is not None:
                    overlay = overlay_color_show(
                        np.rot90(self.overlay[directions[i]]),
                        current_labels=self.label_editor.current_labels
                    )
                    self.viewers[i].viewer.set_overlay(overlay)

    def set_mode(self):
        if self.label_editor.zoom_btn.isChecked():
            self.mode = 'zoom'
        elif self.label_editor.brush_btn.isChecked():
            self.mode = 'brush'
        else:
            self.mode = 'crosshair'
        print('current mode: ', self.mode)

    def get_brush_value(self):
        selected_item = self.label_editor.label_list.currentItem()
        if selected_item:
            selected_label = self.label_editor.label_list.itemWidget(selected_item)
            return int(selected_label.number.text())
        else:
            return None
        
    def paint_sqaure(self, x, y, slice):
        brush_value = self.get_brush_value()
        if brush_value is None or self.brush_size <= 0:
            return

        b1 = b2 = self.brush_size // 2
        if self.brush_size % 2 != 0:
            b2 += 1

        is_3d = self.label_editor.brush_editor.brush_3d_chkbox.isChecked()

        if slice == 'coronal':
            y = self.S-y-1
            ly = self.layers[1]
            if is_3d:
                self.overlay[x-b1:x+b2, ly-b1:ly+b2, y-b1:y+b2] = brush_value
            else:
                self.overlay[x-b1:x+b2, ly, y-b1:y+b2] = brush_value


        elif slice == 'sagittal':
            y = self.S-y-1
            ly = self.layers[0]
            if is_3d:
                self.overlay[ly-b1:ly+b2, x-b1:x+b2, y-b1:y+b2] = brush_value
            else:
                self.overlay[ly, x-b1:x+b2, y-b1:y+b2] = brush_value

        elif slice == 'axial':
            y = self.A-y-1
            ly = self.layers[2]
            if is_3d:
                self.overlay[x-b1:x+b2, y-b1:y+b2, ly-b1:ly+b2] = brush_value
            else:
                self.overlay[x-b1:x+b2, y-b1:y+b2, ly] = brush_value

    def coronal_full_screen(self):
        if self.display_mode == 3:
            self.hide_viewers((1, 2))
            self.display_mode = 0
            self.viewers[0].full_screen_btn.setIcon(newIcon('menu'))

        elif self.display_mode == 0:
            self.show_3_viewers()
            self.display_mode = 3
            self.viewers[0].full_screen_btn.setIcon(newIcon('letter-c'))
            
    def sagittal_full_screen(self):
        if self.display_mode == 3:
            self.hide_viewers((0, 2))
            self.display_mode = 0
            self.viewers[1].full_screen_btn.setIcon(newIcon('menu'))
            
        elif self.display_mode == 0:
            self.show_3_viewers()
            self.display_mode = 3
            self.viewers[1].full_screen_btn.setIcon(newIcon('letter-s'))
    
    def axial_full_screen(self):
        if self.display_mode == 3:
            self.hide_viewers((0, 1))
            self.display_mode = 0
            self.viewers[2].full_screen_btn.setIcon(newIcon('menu'))
            
        elif self.display_mode == 0:
            self.show_3_viewers()
            self.display_mode = 3
            self.viewers[2].full_screen_btn.setIcon(newIcon('letter-a'))

    def hide_viewers(self, slice_index):
        for i in slice_index:
            self.viewers[i].hide()

    def show_3_viewers(self):
        for viewer in self.viewers:
            viewer.show()


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
        self.square = None

        self.image_data = image_data
        height, width, _  = self.image_data.shape
        self.scale_factor = 1

        # pixmap of image
        self.pixmap = QGraphicsPixmapItem()
        self.pixmap.setPixmap(QPixmap.fromImage(QImage(np.ascontiguousarray(self.image_data), width, height, QImage.Format_Grayscale8)))
        self.pixmap.setPos(0, 0)
        self.scene.addItem(self.pixmap)

        # overlay
        self.overlay = np.ones((255, 255, 4), dtype=np.uint8)
        self.overlay[..., 3] = 0 # all transparent
        self.overlay_pixmap = QGraphicsPixmapItem(self.numpy_array_to_pixmap(self.overlay))
        self.overlay_pixmap.setPos(0, 0)
        self.scene.addItem(self.overlay_pixmap)

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
        # crosshair
        self.horizontal_line = QGraphicsLineItem()
        self.vertical_line = QGraphicsLineItem()

        pen = QPen(Qt.DashLine)
        pen.setWidth(1)
        pen.setColor(Qt.blue)
        self.horizontal_line.setPen(pen)
        self.vertical_line.setPen(pen)

        self.scene.addItem(self.horizontal_line)
        self.scene.addItem(self.vertical_line)


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

    def set_overlay(self, overlay):
        self.overlay = overlay
        self.overlay_pixmap.setPixmap(self.numpy_array_to_pixmap(self.overlay))

    def clear_overlay(self):
        self.overlay = np.ones((255, 255, 4), dtype=np.uint8)
        self.overlay[..., 3] = 0 # all transparent
        self.overlay_pixmap.setPixmap(self.numpy_array_to_pixmap(self.overlay))

    def numpy_array_to_pixmap(self, array):
        # Ensure the input array is in RGBA mode
        if array.ndim != 3 or array.shape[2] != 4:
            raise ValueError("Input array must be a 3D numpy array with a shape of (height, width, 4)")

        # Convert the numpy array to QImage
        height, width, channel = array.shape
        bytes_per_line = 4 * width
        q_image = QImage(array.data, width, height, bytes_per_line, QImage.Format_RGBA8888)

        # Convert QImage to QPixmap
        q_pixmap = QPixmap.fromImage(q_image)
        return q_pixmap

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
        self.overlay_pixmap.setScale(factor)
        self.overlay_pixmap.setPos(QPointF((ww - w * factor) // 2 + self.pan_pos.x(), (hh - h * factor) // 2 + self.pan_pos.y()))

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
            x, y = event.pos().x(), event.pos().y()
            pixmap_x = self.pixmap.pos().x()
            pixmap_y = self.pixmap.pos().y()
            x = int((x - pixmap_x) / (self.scale_factor * self.zoom_factor))
            y = int((y - pixmap_y) / (self.scale_factor * self.zoom_factor))

            if self.drag_flag:
                

                if mode == 'crosshair':
                    if self.slice_type == 'coronal': # mouse in coronal plane
                        iframe.set_layer(x, 0)
                        iframe.set_layer(iframe.S-y-1, 2)

                    elif self.slice_type == 'sagittal': # mouse in sagittal plane
                        iframe.set_layer(x, 1)
                        iframe.set_layer(iframe.S-y-1, 2)

                    elif self.slice_type == 'axial': # mouse in axial plane
                        iframe.set_layer(x, 0)
                        iframe.set_layer(iframe.A-y-1, 1)

                    self.update_crosshair(event.pos())

                elif mode == 'zoom':
                    self.zoom(event)

            if mode == 'brush':
                if self.square:
                    self.update_square_position(self.mapToScene(event.pos()), iframe.brush_size)
                else:
                    # draw brush square
                    # scene_pos = self.mapToScene(event.pos())
                    self.start_drawing_square(event.pos(), iframe.brush_size)
                
                if self.drag_flag:
                    iframe.paint_sqaure(x, y, self.slice_type)

                iframe.update_image()

    def mousePressEvent(self, event):
        iframe = self.parent().parent()
        self.drag_flag = True

        if iframe.mode == 'zoom':
            if event.buttons() & Qt.LeftButton:
                self.mouse_start_pos = event.pos()
            elif event.buttons() & Qt.RightButton:
                self.mouse_start_pos = event.pos()

        if iframe.mode == 'brush':
            x, y = event.pos().x(), event.pos().y()
            pixmap_x = self.pixmap.pos().x()
            pixmap_y = self.pixmap.pos().y()
            x = int((x - pixmap_x) / (self.scale_factor * self.zoom_factor))
            y = int((y - pixmap_y) / (self.scale_factor * self.zoom_factor))
            iframe.paint_sqaure(x, y, self.slice_type)
            iframe.update_image()

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

    # crosshair tool
    def update_crosshair(self, pos, stay_in_pixmap=True):
        # get border of scene
        rect = self.pixmap.mapRectToScene(self.pixmap.boundingRect())

        pos = self.mapToScene(pos)
        x = pos.x()
        y = pos.y()
        # keep crosshair in self.pixmap's boundingRect
        if stay_in_pixmap:
            x = x if x >= rect.left() else rect.left()
            x = x if x <= rect.right() else rect.right()

            y = y if y >= rect.top() else rect.top()
            y = y if y <= rect.bottom() else rect.bottom()

        # set coordinates of 2 lines
        self.horizontal_line.setLine(QLineF(rect.left(), y, rect.right(), y))
        self.vertical_line.setLine(QLineF(x, rect.top(), x, rect.bottom()))

    # zoom tool
    def zoom(self, event):
        dx = event.pos().x() - self.mouse_start_pos.x()
        dy = event.pos().y() - self.mouse_start_pos.y()

        if event.buttons() & Qt.LeftButton:
            self.pan_pos = QPointF(self.pan_pos.x() + dx, self.pan_pos.y() + dy)
            # # add zoom tool's pan displacement to crosshair
            # crosshair_x = self.vertical_line.line().x1()
            # crosshair_y = self.horizontal_line.line().y1()
            # self.update_crosshair(QPoint(xpos=crosshair_x + self.pan_pos.x(),
            #                              ypos=crosshair_y + self.pan_pos.y()),
            #                       stay_in_pixmap=False)

        elif event.buttons() & Qt.RightButton:
            self.zoom_factor -= dy / 100
            if self.zoom_factor * self.scale_factor < 1:
                self.zoom_factor = 1 / self.scale_factor

        self.resize()
        self.mouse_start_pos = event.pos()

    # drawing tool
    def start_drawing_square(self, center_point, size):
        half_size = size / 2 # * self.scale_factor * self.zoom_factor
        rect = QRectF(center_point.x() - half_size, center_point.y() - half_size, size, size)

        self.square = QGraphicsRectItem(rect)
        pen = QPen(QColor('red'))
        pen.setWidth(1)
        self.square.setPen(pen)
        self.square.setBrush(Qt.transparent)

        self.scene.addItem(self.square)

    def update_square_position(self, center_point, size):
        half_size = size / 2 # * self.scale_factor * self.zoom_factor
        # print(size, half_size * 2)
        rect = QRectF(center_point.x() - half_size, center_point.y() - half_size, size, size)
        self.square.setRect(rect)


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