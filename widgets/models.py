from PySide6 import QtWidgets, QtCore


class Models(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName(u"widget")
        self.setGeometry(QtCore.QRect(100, 140, 415, 421))

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)

        self.brain_age_mapping = QtWidgets.QCheckBox("brain_age_mapping")
        self.gridLayout.addWidget(self.brain_age_mapping, 1, 1, 1, 1)

        self.wm_parcellation = QtWidgets.QCheckBox("wm_parcellation")
        self.gridLayout.addWidget(self.wm_parcellation, 4, 1, 1, 1)

        self.cortical_thickness = QtWidgets.QCheckBox("cortical_thickness")
        self.gridLayout.addWidget(self.cortical_thickness, 3, 0, 1, 1)

        self.wm_hyperintensity = QtWidgets.QCheckBox("wm_hyperintensity")
        self.gridLayout.addWidget(self.wm_hyperintensity, 5, 0, 1, 1)

        self.brain_mask = QtWidgets.QCheckBox("brain_mask")
        self.brain_mask.setChecked(True)
        self.gridLayout.addWidget(self.brain_mask, 0, 0, 1, 1)

        self.tumor = QtWidgets.QCheckBox("tumor")
        self.gridLayout.addWidget(self.tumor, 4, 0, 1, 1)

        self.fsl_style = QtWidgets.QCheckBox("fsl_style")
        self.gridLayout.addWidget(self.fsl_style, 3, 1, 1, 1)

        self.dkt = QtWidgets.QCheckBox("dkt")
        self.gridLayout.addWidget(self.dkt, 2, 1, 1, 1)

        self.extracted_brain = QtWidgets.QCheckBox("extracted_brain")
        self.gridLayout.addWidget(self.extracted_brain, 1, 0, 1, 1)

        self.aseg = QtWidgets.QCheckBox("aseg")
        self.gridLayout.addWidget(self.aseg, 0, 1, 1, 1)

        self.dgm = QtWidgets.QCheckBox("dgm")
        self.gridLayout.addWidget(self.dgm, 2, 0, 1, 1)

        self.save_qc = QtWidgets.QCheckBox("save_qc")
        self.gridLayout.addWidget(self.save_qc, 6, 0, 1, 1)

        self.force_gz = QtWidgets.QCheckBox("force_gz")
        self.gridLayout.addWidget(self.force_gz, 6, 1, 1, 1)

        self.output_csv = QtWidgets.QCheckBox("output csv")
        self.gridLayout.addWidget(self.output_csv, 7, 0, 1, 1)

        self.seperate_csv = QtWidgets.QCheckBox("seperate csv")
        self.gridLayout.addWidget(self.seperate_csv, 7, 1, 1, 1)
