import numpy as np
import nibabel as nib
from nilearn.image import reorder_img
import json
import csv
from os.path import basename

label_definition = {
    "dgm": {
        "Left-Thalamus-Proper": 1,
        "Right-Thalamus-Proper": 2,
        "Left-Caudate": 3,
        "Right-Caudate": 4,
        "Left-Putamen": 5,
        "Right-Putamen": 6,
        "Left-Pallidum": 7,
        "Right-Pallidum": 8,
        "Left-Hippocampus": 9,
        "Right-Hippocampus": 10,
        "Left-Amygdala": 11,
        "Right-Amygdala": 12
    },
    "aseg": {
        "Left Cerebral WM": 2,
        "Left Cerebral Cortex": 3,
        "Left Lateral Ventricle": 4,
        "Left Inf Lat Vent": 5,
        "Left Cerebellum WM": 7,
        "Left Cerebellum Cortex": 8,
        "Left Thalamus": 10,
        "Left Caudate": 11,
        "Left Putamen": 12,
        "Left Pallidum": 13,
        "3rd Ventricle": 14,
        "4rd Ventricle": 15,
        "Brain Stem": 16,
        "Left Hippocampus": 17,
        "Left Amygdala": 18,
        "CSF": 24,
        "Left Accumbens area": 26,
        "Left VentralDC": 28,
        "Left vessel": 30,
        "Left choroid plexus": 31,
        "Right Cerebral WM": 41,
        "Right Cerebral Cortex": 42,
        "Right Lateral Ventricle": 43,
        "Right Inf Lat Vent": 44,
        "Right Cerebellum WM": 46,
        "Right Cerebellum Cortex": 47,
        "Right Thalamus": 49,
        "Right Caudate": 50,
        "Right Putamen": 51,
        "Right Pallidum": 52,
        "Right Hippocampus": 53,
        "Right Amygdala": 54,
        "Right Accumbens area": 58,
        "RIght VentralDC": 60,
        "Right vessel": 62,
        "Right choroid plexus": 63,
        "WM hypointensities": 77,
        "Optic Chiasm": 85,
        "CC Posterior": 251,
        "CC Mid Posterior": 252,
        "CC Central": 253,
        "CC Mid Anterior": 254,
        "CC Anterior": 255
    },
    "synthseg": {
        "Left Cerebral WM": 2,
        "Left Cerebral Cortex": 3,
        "Left Lateral Ventricle": 4,
        "Left Inf Lat Vent": 5,
        "Left Cerebellum WM": 7,
        "Left Cerebellum Cortex": 8,
        "Left Thalamus": 10,
        "Left Caudate": 11,
        "Left Putamen": 12,
        "Left Pallidum": 13,
        "3rd Ventricle": 14,
        "4rd Ventricle": 15,
        "Brain Stem": 16,
        "Left Hippocampus": 17,
        "Left Amygdala": 18,
        "CSF": 24,
        "Left Accumbens area": 26,
        "Left VentralDC": 28,
        "Right Cerebral WM": 41,
        "Right Cerebral Cortex": 42,
        "Right Lateral Ventricle": 43,
        "Right Inf Lat Vent": 44,
        "Right Cerebellum WM": 46,
        "Right Cerebellum Cortex": 47,
        "Right Thalamus": 49,
        "Right Caudate": 50,
        "Right Putamen": 51,
        "Right Pallidum": 52,
        "Right Hippocampus": 53,
        "Right Amygdala": 54,
        "Right Accumbens area": 58,
        "RIght VentralDC": 60
    }
}


def file_to_arr(f):
    arr = reorder_img(nib.load(f), resample='nearest').get_fdata()
    # return arr.astype(np.uint8)
    return arr

def nii_to_arr(nii):
    return reorder_img(nii, resample='nearest').get_fdata()

def open_nii_file(f):
    return reorder_img(nib.load(f), resample='nearest')