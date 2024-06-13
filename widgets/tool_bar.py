from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import Qt


class Slider(QtWidgets.QSlider):

    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        self.setRange(0, 100)
        self.setValue(50)

class ToolBar(QtWidgets.QToolBar):

    def __init__(self):
        super(ToolBar, self).__init__()

        self.pen_label = 0 # background

        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)

        self.init_UI()

    def init_UI(self):
        self.addWidget(QtWidgets.QLabel('X'))
        self.x_line = QtWidgets.QSpinBox()
        self.x_line.setRange(-1000, 1000)
        self.addWidget(self.x_line)

        self.addWidget(QtWidgets.QLabel('Y'))
        self.y_line = QtWidgets.QSpinBox()
        self.y_line.setRange(-1000, 1000)
        self.addWidget(self.y_line)

        self.addWidget(QtWidgets.QLabel('Z'))
        self.z_line = QtWidgets.QSpinBox()
        self.z_line.setRange(-1000, 1000)
        self.addWidget(self.z_line)

        self.addSeparator()

        self.minv = QtWidgets.QDoubleSpinBox()
        self.minv.setSingleStep(1)
        self.minv.setRange(-100000, 100000)
        self.minv.setDecimals(4)
        self.minv.setValue(0)
        self.addWidget(self.minv)

        self.maxv = QtWidgets.QDoubleSpinBox()
        self.maxv.setRange(-100000, 100000)
        self.maxv.setDecimals(4)
        self.maxv.setValue(255)
        self.addWidget(self.maxv)

        self.addSeparator()

        self.addWidget(QtWidgets.QLabel('color map'))
        self.cmap_combobox = QtWidgets.QComboBox()
        self.cmap_combobox.addItems(['gray', 'bone', 'hot', 'cool', 'winter', 'coolwarm', 'copper', 
                                     'rainbow', 'gist_ncar', 'freesurfer'])
        self.addWidget(self.cmap_combobox)

        self.overlay_cmap_cbb = QtWidgets.QComboBox()
        self.overlay_cmap_cbb.addItems(['gray', 'bone', 'hot', 'cool', 'winter', 'coolwarm', 'copper', 
                                     'rainbow', 'gist_ncar', 'freesurfer'])
        self.overlay_cmap_cbb.setCurrentText('freesurfer')
        self.addWidget(self.overlay_cmap_cbb)

        self.addSeparator()

        self.run_button = QtWidgets.QPushButton('run')
        self.addWidget(self.run_button)