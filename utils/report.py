import csv  
from os.path import basename

import numpy as np
import nibabel as nib

from .label import label_all, LABEL_DATA, DGM_LABEL

def get_volume(nii, label):
    zoom = nii.header.get_zooms()
    voxel_size = zoom[0] * zoom[1] * zoom[2]
    data = nii.get_fdata()
    return np.sum(data == label) * voxel_size


def brain_mask_report():
    pass


def aseg_report(fname):
    nii = nib.load(fname)
    aseg_labels = label_all['aseg']
    report = dict()
    for number in aseg_labels:
        report[LABEL_DATA[number].name] = round(get_volume(nii, number))

    return report


def dgm_report(fname):
    nii = nib.load(fname)
    report = dict()
    for name, number in DGM_LABEL.items():
        report[name] = round(get_volume(nii, number))

    return report


def dkt_report():
    pass

def ct_report():
    pass

def syn_report():
    pass


def create_report_dicts(fname, models):
    report_dicts = dict()
    if 'aseg' in models:
        f = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_aseg')
        report_dicts['aseg'] = aseg_report(f)

    if 'dgm' in models:
        f = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_dgm')
        report_dicts['dgm'] = dgm_report(f)

    if 'dkt' in models:
        f = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_dkt')
        report_dicts['dkt'] = dkt_report(f)

        if 'ct' in models:
            report_dicts['ct'] = ct_report(f)

    return report_dicts


def create_report_csv(fname, models):
    report_dicts = create_report_dicts(fname, models)

    for model, report_dict in report_dicts.items():
        csv_f = fname.split('.')[0] + f'_{model}.csv'
        with open(csv_f, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(report_dict.items())


if __name__ == '__main__':
    create_report_csv(r'output\CC0001_philips_15_55_M.nii.gz', ['aseg', 'dgm'])
    # print(aseg_report(r'test_file\CANDI_BPDwoPsy_030_aseg.nii.gz'))
    # def fname_to_arr(f):
    #     arr = reorder_img(nib.load(f), resample='nearest').get_fdata()
    #     # return arr.astype(np.uint8)
    #     return arr
    
    # dkt = nib.load('output\CANDI_BPDwoPsy_030_dkt.nii.gz').get_fdata()
    # ct = nib.load('output\CANDI_BPDwoPsy_030_ct.nii.gz').get_fdata()

    # # print(np.unique(dkt))
    # print(np.unique(ct))

    # for label in np.unique(dkt):
    #     if label in DKT_LABEL:
    #         average_thickness = np.sum(ct[dkt == label])  / np.sum(dkt == label)
    #         print(label, average_thickness)