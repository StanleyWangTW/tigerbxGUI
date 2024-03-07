import numpy as np
import nibabel as nib
from nilearn.image import reorder_img


def file_to_arr(f):
    arr = reorder_img(nib.load(f), resample='nearest').get_fdata()
    arr = (arr - arr.min()) / (arr.max() - arr.min()) * 255
    return arr.astype(np.uint8)
