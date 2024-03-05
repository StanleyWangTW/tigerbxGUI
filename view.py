from os.path import basename

import numpy as np
import nibabel as nib

from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from PySide6.QtWidgets import QWidget, QMainWindow, QToolBar, QDockWidget, QStatusBar, QHBoxLayout, QVBoxLayout
from PySide6.QtWidgets import QFileDialog, QLineEdit, QLabel, QComboBox, QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

import tigerbx

model = 'aseg'
input_dir = None


class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle('TigerBx')
        self.resize(640, 480)

        self.image = None

        # menu bar
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')
        open_action = file_menu.addAction('Open')
        open_action.triggered.connect(self.open_file)
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.exit)

        overlay_menu = menu_bar.addMenu('Overlay')
        add_action = overlay_menu.addAction('Add')

        window_menu = menu_bar.addMenu('Window')

        setting_menu = menu_bar.addMenu('Setting')

        help_menu = menu_bar.addMenu('Help')
        about_action = help_menu.addAction('About')

        # tool bar
        tool_bar = ToolBar()
        tool_bar.x_line.textEdited.connect(self.update_coronal)
        self.addToolBar(tool_bar)

        # dock widgets
        self.file_dock = QDockWidget(self.tr('File List'), self)
        self.file_dock.setObjectName('Files')
        fileListWidget = QtWidgets.QWidget()
        fileListWidget.setLayout(QVBoxLayout())
        self.file_dock.setWidget(fileListWidget)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)

        #  central widget
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        # status bar
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

    def open_file(self):
        print('Open File')
        fileName, _ = QFileDialog.getOpenFileName(self, 'select file', r'.',
                                                  'Nii Files (*.nii *.nii.gz)')

        global input_dir
        input_dir = fileName
        self.statusBar().showMessage(f'Opened: {input_dir}')

        self.image = nib.load(input_dir).get_fdata()

    def update_coronal(self, text):
        if self.image is not None:
            layer = int(text)
            if 0 <= layer < self.image.shape[0]:
                self.central_widget.image.coronal.set_data(self.image[layer, ...])
                self.central_widget.image.coronal.autoscale()
                print(layer)
                print(self.image[layer, ...].mean())
                self.central_widget.image.coronal.figure.canvas.draw()
            else:
                self.central_widget.image.coronal.set_data(np.zeros((256, 256)))
                self.central_widget.image.coronal.autoscale()
                self.central_widget.image.coronal.figure.canvas.draw()

    def exit(self):
        self.app.quit()


class ToolBar(QToolBar):

    def __init__(self):
        super().__init__()

        self.x_line = QLineEdit('0')
        self.y_line = QLineEdit('0')
        self.z_line = QLineEdit('0')

        self.run_button = QPushButton('run')
        self.run_button.clicked.connect(self.run)

        self.init_gui()

    def init_gui(self):
        self.addWidget(QLabel('X'))
        self.addWidget(self.x_line)
        self.addWidget(QLabel('Y'))
        self.addWidget(self.y_line)
        self.addWidget(QLabel('Z'))
        self.addWidget(self.z_line)

        self.addWidget(QLabel('model'))
        self.addWidget(ModelComboBox())

        self.addWidget(QLabel('color map'))
        self.addWidget(CmapComboBox())

        self.addWidget(self.run_button)

    def run(self):
        args = {'aseg': 'a', 'dgm': 'd'}
        print('run', input_dir)

        if input_dir:
            print('run model')
            tigerbx.run(args[model], input_dir)


class ModelComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        self.addItems(['aseg', 'dgm'])
        self.currentTextChanged.connect(self.model_changed)

    def model_changed(self, text):
        global model
        model = text
        print('select model: ', model)


class CmapComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        self.addItems(['Grayscale', 'Freesurfer'])


class CentralWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.image = iFrame()
        self.mask_ = iFrame()

        layout = QVBoxLayout()
        layout.addWidget(self.image)
        layout.addWidget(self.mask_)
        self.setLayout(layout)


class iFrame(QWidget):

    def __init__(self):
        super().__init__()

        self.coronal_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.coronal = self.coronal_canvas.figure.subplots().imshow(np.zeros((256, 256)),
                                                                    cmap='gray')
        # coronal_canvas.figure.subplots().axis('off')

        layout = QHBoxLayout()
        layout.addWidget(self.coronal_canvas)
        layout.addWidget(QLabel('X'))
        layout.addWidget(QLabel('X'))
        self.setLayout(layout)
