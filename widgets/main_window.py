import os
import os.path as osp
from glob import glob

from PySide6.QtCore import Qt
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt, QThread, Signal
import numpy as np
import tigerbx

from .tool_bar import ToolBar
from .models import Models
from .canvas import Canvas
from .file_list import FileTree
from .run_dialog import RunningDialog
from .label_editor import LeftWidget, LabelEditor
from utils import image_process, load_labels, create_report_csv


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, app):
        self.filenames = None
        self.fnames_dict = dict()
        self.current_file = None
        self.overlay = None
        self.output_dir = 'output'

        super().__init__()
        self.app = app
        self.setup_ui()
        self.connect()

    def setup_ui(self):
        self.setWindowTitle('TigerBx')

        # menu bar
        menu_bar = self.menuBar()

        # file menu
        file_menu = menu_bar.addMenu('File')
        open_action = file_menu.addAction('Open')
        select_output = file_menu.addAction('choose output folder')
        file_menu.addSeparator()
        exit_action = file_menu.addAction('Exit')

        open_action.triggered.connect(self.open_files)
        select_output.triggered.connect(self.select_folder)
        exit_action.triggered.connect(self.exit)

        # overlay menu
        overlay_menu = menu_bar.addMenu('Overlay')
        addOverlay = overlay_menu.addAction('Add')
        clearOverlay = overlay_menu.addAction('Clear Overlays')
        transBG = overlay_menu.addMenu('Transparency on background')

        action_group = QtGui.QActionGroup(self)
        for i in range(0, 110, 10):
            action = QtGui.QAction(f'{i}%', self)
            action.setCheckable(True)
            action_group.addAction(action)
            transBG.addAction(action)
        action_group.setExclusive(True)

        addOverlay.triggered.connect(self.add_overlay)
        clearOverlay.triggered.connect(self.clear_overlay)
        action_group.triggered.connect(self.setTransparencyBG)

        # window menu
        window_menu = menu_bar.addMenu('Window')
        setting_menu = menu_bar.addMenu('Setting')
        help_menu = menu_bar.addMenu('Help')
        about_action = help_menu.addAction('About')

        # tool bar
        self.tool_bar = ToolBar()
        self.addToolBar(self.tool_bar)

        self.tool_bar.y_line.valueChanged.connect(self.update_coronal)
        self.tool_bar.x_line.valueChanged.connect(self.update_sagittal)
        self.tool_bar.z_line.valueChanged.connect(self.update_axial)

        self.tool_bar.minv.valueChanged.connect(self.change_min_max)
        self.tool_bar.maxv.valueChanged.connect(self.change_min_max)

        self.tool_bar.cmap_combobox.currentTextChanged.connect(self.change_cmap)
        self.tool_bar.overlay_cmap_cbb.currentTextChanged.connect(self.change_overlay_cmap)
        self.tool_bar.run_button.clicked.connect(self.run)

        # left dock widgets
        self.page1 = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.models = Models()
        layout.addWidget(self.models)
        self.file_tree = FileTree()
        self.file_tree.itemSelectionChanged.connect(self.file_selection_changed)
        file_group = QtWidgets.QGroupBox()
        file_group.setTitle('Files')
        file_group_layout = QtWidgets.QVBoxLayout()
        file_group_layout.addWidget(self.file_tree)
        file_group.setLayout(file_group_layout)
        layout.addWidget(file_group)
        self.page1.setLayout(layout)

        self.label_editor = LabelEditor()

        w = LeftWidget()
        w.addTab(self.page1, 'Files')
        w.addTab(self.label_editor, 'labels')
        self.left_dock = QtWidgets.QDockWidget()
        self.left_dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        #  central widget
        self.central_widget = Canvas(self.tool_bar)
        self.setCentralWidget(self.central_widget)

    def connect(self):
        self.label_editor.zoom_btn.clicked.connect(self.central_widget.disp1.zoom_mode)
        self.label_editor.crosshair_btn.clicked.connect(self.central_widget.disp1.crosshair_mode)

    def open_files(self):
        self.filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'select file', r'.',
                                                                   'Nii Files (*.nii *.nii.gz)')

        for filename in self.filenames:
            self.fnames_dict[osp.basename(filename)] = [filename]

        self.file_tree.clear()
        self.file_tree.addData(self.fnames_dict)

        self.change_current_file(self.filenames[0])

    def file_selection_changed(self):
        items = self.file_tree.selectedItems()

        if not items:
            return

        self.change_current_file(items[0].text(0))

    def change_current_file(self, f):
        self.current_file = image_process.file_to_arr(f)
        self.clear_overlay()
        self.label_editor.load_labels(self.current_file)
        self.central_widget.disp1.set_image(self.current_file)
        self.statusBar().showMessage(f'Opened: {f}')

    def select_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder', r'.', options=options)
        self.output_dir = folder_path

    # overlay
    def add_overlay(self):
        if self.current_file is not None:
            fname_overlay, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'select file', r'.', 'Nii Files (*.nii *.nii.gz)')
            print(fname_overlay)
            self.overlay = image_process.file_to_arr(fname_overlay)
            self.central_widget.disp1.overlay = self.overlay
            self.label_editor.load_labels(self.overlay)
            self.central_widget.disp1.update_image()

    def clear_overlay(self):
        self.overlay = None
        self.label_editor.load_labels(self.current_file)
        self.central_widget.disp1.overlay = None
        self.central_widget.disp1.update_image()

    def setTransparencyBG(self, action):
        self.central_widget.disp1.alpha = float(action.text().replace('%', '')) / 100
        self.central_widget.disp1.update_image()

    def update_coronal(self, layer):
        self.central_widget.disp1.set_layer(layer, 1)

    def update_sagittal(self, layer):
        self.central_widget.disp1.set_layer(layer, 0)

    def update_axial(self, layer):
        self.central_widget.disp1.set_layer(layer, 2)

    def change_min_max(self, value):
        minv = self.tool_bar.minv.value()
        maxv = self.tool_bar.maxv.value()
        self.central_widget.disp1.minv = minv
        self.central_widget.disp1.maxv = maxv
        self.central_widget.disp1.update_image()

    def change_cmap(self, cmap):
        self.central_widget.disp1.cmap = cmap
        self.central_widget.disp1.update_image()

    def change_overlay_cmap(self, cmap):
        self.central_widget.disp1.overlay_cmap = cmap
        self.central_widget.disp1.update_image()

    def run(self):
        if self.filenames is not None:
            models = self.models

            args = ''
            args = args + 'm' if models.brain_mask.isChecked() else args
            args = args + 'a' if models.aseg.isChecked() else args
            args = args + 'b' if models.extracted_brain.isChecked() else args
            args = args + 'B' if models.brain_age_mapping.isChecked() else args
            args = args + 'd' if models.dgm.isChecked() else args
            args = args + 'k' if models.dkt.isChecked() else args
            args = args + 'c' if models.cortical_thickness.isChecked() else args
            args = args + 'C' if models.fsl_style.isChecked() else args
            args = args + 'S' if models.synthseg_like.isChecked() else args
            args = args + 't' if models.tumor.isChecked() else args
            args = args + 'w' if models.wm_parcellation.isChecked() else args
            args = args + 'W' if models.wm_hyperintensity.isChecked() else args
            args = args + 'q' if models.save_qc.isChecked() else args
            args = args + 'z' if models.force_gz.isChecked() else args

            dialog = RunningDialog(self)
            dialog.show()
            self.thread = RunTigerBx(args, self.filenames, self.output_dir, models.output_csv.isChecked())
            self.thread.creating_csv.connect(dialog.creating_csv)
            self.thread.finished.connect(dialog.close)
            self.thread.finished.connect(self.load_outputs_to_file_tree)
            self.thread.start()

    def load_outputs_to_file_tree(self):
        for key in self.fnames_dict.keys():
            outputs = glob(osp.join(self.output_dir, key.split('.')[0] + '*.nii*'))
            for output in outputs:
                self.fnames_dict[key].append(output)

        self.file_tree.clear()
        self.file_tree.addData(self.fnames_dict)

    def exit(self):
        self.app.quit()


class RunTigerBx(QThread):
    creating_csv = Signal()

    def __init__(self, args, filenames, output_dir, output_csv) -> None:
        self.args = args
        self.filenames = filenames
        self.output_dir = output_dir
        self.output_csv = output_csv
        super().__init__()

    def run(self):
        tigerbx.run(self.args, self.filenames, self.output_dir)

        if self.output_csv:
            self.creating_csv.emit()
            model_names = {
                "a": "aseg",
                "B": "bam",
                "d": "dgm",
                "k": "dkt",
                "c": "ct",
                "C": "pve",
                "S": "syn",
                "w": "wmp",
                "W": "wmh"
            }
            mds = list()
            for a in self.args:
                model_name = model_names.get(a)
                if model_name is not None:
                    mds.append(model_name)

            for f in self.filenames:
                create_report_csv(os.path.join(self.output_dir, os.path.basename(f)), mds)