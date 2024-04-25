import numpy as np
import nibabel as nib
from nilearn.image import reorder_img
import json
import csv
from os.path import basename

label_definition = r'label_definitions.json'


def file_to_arr(f):
    arr = reorder_img(nib.load(f), resample='nearest').get_fdata()
    return arr.astype(np.uint8)


def niif2csv(fname, models, seperate=True):
    for model in models:
        with open(label_definition) as f:
            labels = json.load(f)[model]

        file_name = basename(fname).split('.')[0]
        nii = nib.load(fname.replace(file_name, file_name + f'_{model}'))
        db = dict()
        for region, label in labels.items():
            db[region] = round(get_volume(nii, label))

        csv_f = file_name + f'_{model}.csv' if seperate else file_name + '.csv'
        csv_f = fname.replace(basename(fname), csv_f)

        with open(csv_f, 'a', newline='') as f:
            w = csv.writer(f)

            if not seperate:
                w.writerow([model])

            w.writerow(['Structure Name', 'Volume(mm^3)'])
            w.writerows(db.items())


def get_volume(nii, label):
    zoom = nii.header.get_zooms()
    vs = zoom[0] * zoom[1] * zoom[2]
    data = nii.get_fdata()
    return np.sum(data[data == label]) * vs
