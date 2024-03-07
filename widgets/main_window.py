from PySide6.QtCore import Qt
from PySide6 import QtWidgets, QtGui
import nibabel as nib
import numpy as np

from UI import Ui_MainWindow
from widgets import ToolBar, Models, Canvas


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, app):
        super().__init__()
        # self.setupUi(self)
        self.app = app
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
        self.tool_bar = ToolBar()
        self.addToolBar(self.tool_bar)

        self.tool_bar.x_line.textEdited.connect(self.update_coronal)
        self.tool_bar.x_slide.valueChanged.connect(self.update_coronal)

        # dock widgets
        self.file_dock = QtWidgets.QDockWidget(self.tr(''), self)
        dock_widget = Models()
        self.file_dock.setWidget(dock_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)

        #  central widget
        self.central_widget = Canvas()
        self.setCentralWidget(self.central_widget)

    def open_file(self):
        print('Open File')
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'select file', r'.',
                                                            'Nii Files (*.nii *.nii.gz)')

        global input_dir
        input_dir = fileName
        self.statusBar().showMessage(f'Opened: {input_dir}')

        self.image = nib.load(input_dir).get_fdata()
        self.image = (self.image - self.image.min()) / (self.image.max() - self.image.min()) * 255
        self.image = self.image.astype(np.uint8)

        self.tool_bar.x_slide.setRange(0, self.image.shape[0])

    def update_coronal(self, layer):
        if self.image is not None:
            layer = layer if layer is int() else int(layer)
            if 0 <= layer < self.image.shape[0]:
                qImg = QtGui.QPixmap(
                    QtGui.QImage(np.ascontiguousarray(self.image[layer, :, :]), self.image.shape[2],
                                 self.image.shape[1], QtGui.QImage.Format_Grayscale8))
                self.central_widget.disp1.coronal.setPixmap(qImg)
            else:
                print('blank')

    def exit(self):
        self.app.quit()
