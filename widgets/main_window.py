import threading
import os

from PySide6.QtCore import Qt
from PySide6 import QtWidgets

import tigerbx

from .tool_bar import ToolBar
from .models import Models
from .canvas import Canvas
from .run_dialog import RunDialog
from utils import image_process


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.filenames = None
        self.current_file = None
        self.setup_ui()
        self.connect()

    def setup_ui(self):
        # menu bar
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')
        self.open_action = file_menu.addAction('Open')
        file_menu.addAction('Seperate CSV')
        self.exit_action = file_menu.addAction('Exit')

        overlay_menu = menu_bar.addMenu('Overlay')
        add_action = overlay_menu.addAction('Add')

        window_menu = menu_bar.addMenu('Window')

        setting_menu = menu_bar.addMenu('Setting')

        help_menu = menu_bar.addMenu('Help')
        about_action = help_menu.addAction('About')

        # tool bar
        self.tool_bar = ToolBar()
        self.addToolBar(self.tool_bar)

        # dock widgets
        self.model_dock = QtWidgets.QDockWidget(self.tr(''), self)
        self.model_dock.setWidget(Models())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.model_dock)

        self.file_dock = QtWidgets.QDockWidget(self.tr('Input Files'))
        self.file_list_widget = QtWidgets.QListWidget()
        self.file_list_widget.itemSelectionChanged.connect(self.file_selection_changed)
        self.file_dock.setWidget(self.file_list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)

        self.output_dock = QtWidgets.QDockWidget(self.tr('Output Files'))
        self.output_list_widget = QtWidgets.QListWidget()
        self.output_dock.setWidget(self.output_list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.output_dock)

        #  central widget
        self.central_widget = Canvas()
        self.setCentralWidget(self.central_widget)

    def connect(self):
        self.open_action.triggered.connect(self.open_files)
        self.exit_action.triggered.connect(self.exit)

        self.tool_bar.y_line.textEdited.connect(self.update_coronal)
        self.tool_bar.x_line.textEdited.connect(self.update_sagittal)
        self.tool_bar.z_line.textEdited.connect(self.update_axial)
        self.tool_bar.run_button.clicked.connect(self.run)

        self.central_widget.disp1.coronal.mouseMoveEvent = self.coronal_mve
        self.central_widget.disp1.sagittal.mouseMoveEvent = self.sagittal_mve
        self.central_widget.disp1.axial.mouseMoveEvent = self.axial_mve
        self.central_widget.disp1.coronal.wheelEvent = self.coronal_we
        self.central_widget.disp1.sagittal.wheelEvent = self.sagittal_we
        self.central_widget.disp1.axial.wheelEvent = self.axial_we

    def open_files(self):
        print('Open File')
        self.filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'select file', r'.',
                                                                   'Nii Files (*.nii *.nii.gz)')

        self.file_list_widget.clear()
        for filename in self.filenames:
            item = QtWidgets.QListWidgetItem(filename)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.file_list_widget.addItem(item)

        self.change_current_file(self.filenames[0])

    def file_selection_changed(self):
        items = self.file_list_widget.selectedItems()

        if not items:
            return

        item = items[0]
        self.change_current_file(str(item.text()))

    def change_current_file(self, f):
        self.current_file = image_process.file_to_arr(f)
        self.central_widget.disp1.set_image(self.current_file)
        self.statusBar().showMessage(f'Opened: {f}')

    def coronal_we(self, event):
        print('angle', event.angleDelta().y())
        angle = 1 if event.angleDelta().y() > 0 else -1
        self.update_coronal(angle + self.central_widget.disp1.layers[1])

    def sagittal_we(self, event):
        angle = event.angleDelta().y()
        self.update_sagittal(angle + self.central_widget.disp1.layers[0])

    def axial_we(self, event):
        angle = event.angleDelta().y()
        self.update_axial(angle + self.central_widget.disp1.layers[2])

    def coronal_mve(self, event):
        x, y = event.pos().x(), event.pos().y()
        self.update_sagittal(x)
        self.update_axial(self.central_widget.disp1.image.shape[2] - y)

    def sagittal_mve(self, event):
        x, y = event.pos().x(), event.pos().y()
        self.update_coronal(x)
        self.update_axial(self.central_widget.disp1.image.shape[2] - y)

    def axial_mve(self, event):
        x, y = event.pos().x(), event.pos().y()
        self.update_sagittal(x)
        self.update_coronal(self.central_widget.disp1.image.shape[1] - y)

    def update_coronal(self, layer):
        self.central_widget.disp1.set_layer(layer, 1)
        self.central_widget.disp1.update_image()
        self.tool_bar.y_line.setText(str(layer))

    def update_sagittal(self, layer):
        self.central_widget.disp1.set_layer(layer, 0)
        self.central_widget.disp1.update_image()
        self.tool_bar.x_line.setText(str(layer))

    def update_axial(self, layer):
        self.central_widget.disp1.set_layer(layer, 2)
        self.central_widget.disp1.update_image()
        self.tool_bar.z_line.setText(str(layer))

    def run(self):
        if self.filenames is not None:
            models = self.model_dock.widget()

            args = ''
            args = args + 'm' if models.brain_mask.isChecked() else args
            args = args + 'a' if models.aseg.isChecked() else args
            args = args + 'b' if models.extracted_brain.isChecked() else args
            args = args + 'B' if models.brain_age_mapping.isChecked() else args
            args = args + 'd' if models.dgm.isChecked() else args
            args = args + 'k' if models.dkt.isChecked() else args
            args = args + 'c' if models.cortical_thickness.isChecked() else args
            args = args + 'C' if models.fsl_style.isChecked() else args
            args = args + 't' if models.tumor.isChecked() else args
            args = args + 'w' if models.wm_parcellation.isChecked() else args
            args = args + 'W' if models.wm_hyperintensity.isChecked() else args
            args = args + 'q' if models.save_qc.isChecked() else args
            args = args + 'z' if models.force_gz.isChecked() else args

            output_dir = 'output'
            while os.path.exists(output_dir):
                output_dir += ' new'

            dlg = RunDialog(fnum=len(self.filenames), output_dir=output_dir)
            os.mkdir(output_dir)
            thread = threading.Thread(
                target=lambda filenames=self.filenames: tigerbx.run(args, filenames, output_dir))

            thread.start()
            dlg.exec()
            thread.join()

            if models.output_csv:
                import json
                with open(r'model_names.json', 'r') as f:
                    model_names = json.load(f)

                mds = list()
                for a in args:
                    mds.append(model_names[a])

                for f in self.filenames:
                    image_process.niif2csv(os.path.join(output_dir, os.path.basename(f)),
                                           models=mds,
                                           seperate=models.seperate_csv)

    def exit(self):
        self.app.quit()
