from PySide6.QtWidgets import *
from PySide6.QtGui import QImage, QPixmap, Qt, QIntValidator
import numpy as np

import utils.label as utils_label
from utils.qt import newIcon


class LeftWidget(QTabWidget):
    def __init__(self):
        super(LeftWidget, self).__init__()
        self.setTabShape(self.TabShape.Rounded)

class LabelEditor(QWidget):
    def __init__(self):
        super(LabelEditor, self).__init__()
        self.current_labels = dict()
        self.initUI()
        self.connect_signals()

    def initUI(self):
        tools = QGroupBox('Tools', self)
        self.crosshair_btn = QPushButton(icon=newIcon('crosshair'))
        self.crosshair_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.zoom_btn = QPushButton(icon=newIcon('zoom'))
        self.zoom_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        tools_layout = QHBoxLayout()
        tools_layout.addWidget(self.crosshair_btn)
        tools_layout.addWidget(self.zoom_btn)
        tools.setLayout(tools_layout)

        self.label_list = LabelList()
        
        self.new_btn = QPushButton('new')
        self.delete_btn = QPushButton('delete')
        hbox = QHBoxLayout()
        hbox.addWidget(self.new_btn)
        hbox.addWidget(self.delete_btn)

        vbox = QVBoxLayout()
        vbox.addWidget(tools)
        vbox.addWidget(self.label_list)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def connect_signals(self):
        self.new_btn.clicked.connect(self.create_label)

    def create_label(self):
        label_picker = LabelCreater()
        number, name, rgba = label_picker.create_label()
        if number is not None:
            if number in self.current_labels:
                self.current_labels[number] = utils_label.Label(name, rgba)
                show_error_message(f'Label value={number} alreay exits.\nPlease enter a different value.')
                return

            self.label_list.addLabel(number, name, rgba)

    def load_labels(self, arr):
        self.label_list.clear()
        unique_values_int = np.unique(arr).astype(np.int32)
        for i, value in enumerate(unique_values_int):
            if i > len(utils_label.LABEL_DATA.keys()):
                return
            
            if value in utils_label.LABEL_DATA.keys():
                label = utils_label.LABEL_DATA[value]
                self.current_labels[value] = label
                self.label_list.addLabelObj(value, label)


class  LabelList(QListWidget):
    def __init__(self):
        super(LabelList, self).__init__()

    def addLabel(self, number, name, rgba):
        row = Label(number, name, rgba)
        item = QListWidgetItem(self)
        item.setSizeHint(row.minimumSizeHint())
        self.addItem(item)
        self.setItemWidget(item, row)

    def addLabelObj(self, number, label):
        row = Label(number, label.name, label.rgba)
        item = QListWidgetItem(self)
        item.setSizeHint(row.minimumSizeHint())
        self.addItem(item)
        self.setItemWidget(item, row)


class LabelCreater(QDialog):
    def __init__(self):
        super(LabelCreater, self).__init__()
        self.setModal(True)

        self.color = [255, 0, 0, 255]

        self.initUI()
        self.connect_signals()

    def initUI(self):
        self.setWindowTitle('Label Picker - TigerBx')

        vbox = QVBoxLayout()

        self.number = QLineEdit()
        self.number.setValidator(QIntValidator())
        vbox.addWidget(QLabel('Label Value:'))
        vbox.addWidget(self.number)

        self.name = QLineEdit()
        vbox.addWidget(QLabel('Name:'))
        vbox.addWidget(self.name)

        color_hbox = QHBoxLayout()
        color_hbox.addWidget(QLabel('Color:'))
        self.color_btn = QPushButton()
        self.color_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.set_color_btn_color()
        color_hbox.addWidget(self.color_btn)
        vbox.addLayout(color_hbox)

        opacity_vbox = QVBoxLayout()
        opacity_vbox.addWidget(QLabel('Opacity:'))
        hbox = QHBoxLayout()
        self.opacity_ledt = QLineEdit('255')
        self.opacity_ledt.setValidator(QIntValidator())
        self.opacity_ledt.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        hbox.addWidget(self.opacity_ledt)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        hbox.addWidget(self.opacity_slider)
        opacity_vbox.addLayout(hbox)
        vbox.addLayout(opacity_vbox)

        btn_hbox = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.cancel_btn = QPushButton('CANCEL')
        btn_hbox.addWidget(self.ok_btn)
        btn_hbox.addWidget(self.cancel_btn)
        vbox.addLayout(btn_hbox)
        self.setLayout(vbox)

    def connect_signals(self):
        self.color_btn.clicked.connect(self.pick_color)
        self.opacity_slider.valueChanged.connect(self.set_opacity)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def create_label(self):
        if self.exec() == QDialog.Accepted:
            try:
                number = int(self.number.text())
            except ValueError:
                show_error_message('Label value should be an integer.')
                return None, None, None

            self.color[-1] = int(self.opacity_ledt.text())
            name = self.name.text()
            return number, name, self.color
        else:
            return None, None, None

    def pick_color(self):
        color_dlg = QColorDialog()
        new_color = color_dlg.getColor()
        if new_color.isValid():
            self.color = list(new_color.getRgb())
            self.opacity_ledt.setText(str(new_color.alpha()))
            self.set_color_btn_color()

    def set_opacity(self, value):
        self.opacity_ledt.setText(str(value))
        self.color[-1] = value

    def set_color_btn_color(self):
        square = np.zeros((10, 10, 3))
        square[..., :3] = self.color[:3]
        pixmap = QPixmap.fromImage(QImage(square.astype(np.uint8),
                                          square.shape[0],
                                          square.shape[1],
                                          square.shape[1] * 3,
                                          QImage.Format_RGB888))
        self.color_btn.setIcon(pixmap)


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


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

def show_error_message(message):
    msg_box = QMessageBox(QMessageBox.Critical, 'Input Error', message)
    msg_box.exec()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win  = LabelList()
    win.show()
    app.exec()