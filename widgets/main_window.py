import os
import os.path as osp
from glob import glob
from functools import partial

from PySide6.QtCore import Qt
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt, QThread, Signal
import nibabel as nib
from nilearn.image import reorder_img
import tigerbx

from .tool_bar import ToolBar
from .models import Models
from .canvas import Canvas
from .file_list import FileTree
from .run_dialog import RunningDialog
from .label_editor import LeftWidget, LabelEditor
from utils import image_process, create_report_csv


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, app):
        # init GUI
        super().__init__()
        self.app = app
        self.initUI()

        self.fnames_dict = dict()   # dict of opened files
        self.current_nii = None     # current opened .nii
        self.overlay_nii = None     # overlay .nii
        self.output_dir = 'output'  # output_dir of tigerbx

    def initUI(self):
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
        select_output.triggered.connect(self.select_output_folder)
        exit_action.triggered.connect(self.exit)


        # overlay menu
        overlay_menu = menu_bar.addMenu('Overlay')
        addOverlay = overlay_menu.addAction('Open Overlay')
        saveOverlay = overlay_menu.addAction('Save Overlay Image')
        clearOverlay = overlay_menu.addAction('Clear Overlay')
        transOnBackground = overlay_menu.addMenu('Transparency on background')

        transparency_action_group = QtGui.QActionGroup(self) # transparencies of "Transparency on background" menu
        transparency_action_group.setExclusive(True)
        for i in range(0, 110, 10): # 0% ~ 100%
            action = QtGui.QAction(text=f'{i}%')
            action.setCheckable(True)
            transparency_action_group.addAction(action)
            transOnBackground.addAction(action)

        addOverlay.triggered.connect(self.add_overlay)
        saveOverlay.triggered.connect(self.save_overlay)
        clearOverlay.triggered.connect(self.clear_overlay)
        transparency_action_group.triggered.connect(self.setTransparencyBG)


        # window menu
        about_action = menu_bar.addAction('About')


        # tool bar
        self.tool_bar = ToolBar()
        self.addToolBar(self.tool_bar)

        self.tool_bar.overlay_cmap_cbb.currentTextChanged.connect(self.change_overlay_cmap)
        self.tool_bar.run_button.clicked.connect(self.run)


        # left dock widgets
        left_dock = QtWidgets.QDockWidget()
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock)
        left_widget = LeftWidget()
        left_dock.setWidget(left_widget)

        # left dock page1: tigerbx options
        left_dock_page1 = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        left_dock_page1.setLayout(layout)

        self.models = Models() # model selection checkboxs
        layout.addWidget(self.models)

        self.file_tree = FileTree() # filetree of opened files
        file_group = QtWidgets.QGroupBox()
        file_group.setTitle('Files')
        file_group_layout = QtWidgets.QVBoxLayout()
        file_group_layout.addWidget(self.file_tree)
        file_group.setLayout(file_group_layout)
        layout.addWidget(file_group)

        self.file_tree.itemSelectionChanged.connect(self.file_selection_changed)
        left_widget.addTab(left_dock_page1, 'Files')

        # left dock page2: label editor
        self.label_editor = LabelEditor()
        left_widget.addTab(self.label_editor, 'labels')


        #  central widget
        self.central_widget = Canvas(self.tool_bar, self.label_editor)
        self.setCentralWidget(self.central_widget)

    def open_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'select file', r'.', 'Nii Files (*.nii *.nii.gz)')
        self.fnames_dict.clear()
        for f in files:
            self.fnames_dict[osp.basename(f)] = [f]

        self.file_tree.loadData(self.fnames_dict)
        self.change_current_file(files[0])

    def file_selection_changed(self):
        items = self.file_tree.selectedItems()

        if items[0].text(1): # child selected
            f = items[0].text(0)
        else: # parent selected
            f = self.fnames_dict[items[0].text(0)][0]

        self.change_current_file(f)

    def change_current_file(self, f):
        self.current_nii = nib.load(f)
        self.clear_overlay()
        self.central_widget.set_image(image_process.nii_to_arr(self.current_nii))
        self.statusBar().showMessage(f'Opened: {f}')

    def select_output_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        self.output_dir = QFileDialog.getExistingDirectory(self, 'Select Folder', r'.', options=options)

    # overlay
    def add_overlay(self):
        if self.current_nii is not None:
            overlay_f, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'select file', r'.', 'Nii Files (*.nii *.nii.gz)')
            if overlay_f:
                self.overlay_nii = nib.load(overlay_f)
                overlay_arr = image_process.nii_to_arr(self.overlay_nii)
                self.central_widget.set_overlay(overlay_arr)
                self.label_editor.load_labels(overlay_arr)

    def save_overlay(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'save overlay image', r'.', 'Nii Files (*.nii *.nii.gz)')
        if file_name and self.current_nii is not None:
            self.central_widget.save_overlay(
                file_name,
                self.current_nii,
                reorder_img(self.current_nii, resample='nearest')
            )

    def clear_overlay(self):
        self.overlay_nii = None
        self.central_widget.clear_overlay()

    def setTransparencyBG(self, action):
        self.central_widget.alpha = float(action.text().replace('%', '')) / 100
        self.central_widget.update_image()

    def change_overlay_cmap(self, cmap):
        self.central_widget.overlay_cmap = cmap
        self.central_widget.update_image()

    def run(self):
        if self.fnames_dict:
            args = ''
            args = args + 'm' if self.models.brain_mask.isChecked() else args
            args = args + 'a' if self.models.aseg.isChecked() else args
            args = args + 'b' if self.models.extracted_brain.isChecked() else args
            args = args + 'B' if self.models.brain_age_mapping.isChecked() else args
            args = args + 'd' if self.models.dgm.isChecked() else args
            args = args + 'k' if self.models.dkt.isChecked() else args
            args = args + 'c' if self.models.cortical_thickness.isChecked() else args
            args = args + 'C' if self.models.fsl_style.isChecked() else args
            args = args + 'S' if self.models.synthseg_like.isChecked() else args
            args = args + 't' if self.models.tumor.isChecked() else args
            args = args + 'w' if self.models.wm_parcellation.isChecked() else args
            args = args + 'W' if self.models.wm_hyperintensity.isChecked() else args
            args = args + 'q' if self.models.save_qc.isChecked() else args
            args = args + 'z' if self.models.force_gz.isChecked() else args

            files = []
            for _, fnames in self.fnames_dict.items():
                files.append(fnames[0])

            dialog = RunningDialog(self)
            dialog.show()
            self.thread = RunTigerBx(args, files, self.output_dir, self.models.output_csv.isChecked())
            self.thread.creating_csv.connect(dialog.creating_csv)
            self.thread.finished.connect(dialog.close)
            self.thread.finished.connect(self.load_outputs_to_file_tree)
            self.thread.start()

    def load_outputs_to_file_tree(self):
        for key in self.fnames_dict.keys():
            outputs = glob(osp.join(self.output_dir, key.split('.')[0] + '*.nii*'))
            for output in outputs:
                self.fnames_dict[key].append(output)

        self.file_tree.loadData(self.fnames_dict)

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