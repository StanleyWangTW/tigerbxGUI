from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class Slider(QtWidgets.QSlider):

    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        self.setRange(0, 100)
        self.setValue(50)


class ToolBar(QtWidgets.QToolBar):

    def __init__(self):
        super(ToolBar, self).__init__()
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)

        self.setup_ui()

    def setup_ui(self):
        self.addWidget(QtWidgets.QLabel('X'))
        self.x_line = QtWidgets.QLineEdit('0')
        self.addWidget(self.x_line)

        self.addWidget(QtWidgets.QLabel('Y'))
        self.y_line = QtWidgets.QLineEdit('0')
        self.addWidget(self.y_line)

        self.addWidget(QtWidgets.QLabel('Z'))
        self.z_line = QtWidgets.QLineEdit('0')
        self.addWidget(self.z_line)

        self.addWidget(QtWidgets.QLabel('color map'))
        self.cmap_combobox = QtWidgets.QComboBox()
        self.cmap_combobox.addItems(['Gray', 'Freesurfer'])
        self.addWidget(self.cmap_combobox)

        self.run_button = QtWidgets.QPushButton('run')
        self.addWidget(self.run_button)
