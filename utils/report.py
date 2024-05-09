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


def aseg_report(fname):
    nii = nib.load(fname)
    report = {'Structure Name': 'Volume(mm^3)'}
    for number in label_all['aseg']:
        report[LABEL_DATA[number].name] = round(get_volume(nii, number))

    return report


def dgm_report(fname):
    nii = nib.load(fname)
    report = {'Structure Name': 'Volume(mm^3)'}
    for name, number in DGM_LABEL.items():
        report[name] = round(get_volume(nii, number))

    return report


def dkt_report(fname):
    nii = nib.load(fname)
    report = {'Structure Name': 'Volume(mm^3)'}
    for number in label_all['dkt']:
        report[LABEL_DATA[number].name] = round(get_volume(nii, number))

    return report

def ct_report(fname_ct, fname_dkt):
    ct = nib.load(fname_ct).get_fdata()
    dkt = nib.load(fname_dkt).get_fdata()
    report = {'Structure Name': 'Average Cortical Thickness(mm)'}
    for number in label_all['dkt']:
        average_ct = round(np.sum(ct[dkt == number])  / np.sum(dkt == number), 3)
        report[LABEL_DATA[number].name] = average_ct

    return report


def syn_report(fname):
    nii = nib.load(fname)
    report = {'Structure Name': 'Volume(mm^3)'}
    for number in label_all['synthseg']:
        report[LABEL_DATA[number].name] = round(get_volume(nii, number))

    return report


def wmp_report(fname):
    nii = nib.load(fname)
    report = {'Structure Name': 'Volume(mm^3)'}
    for number in label_all['wmp']:
        report[LABEL_DATA[number].name] = round(get_volume(nii, number))

    return report

def create_report_dicts(fname, models):
    report_dicts = dict()
    if 'aseg' in models:
        f = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_aseg')
        report_dicts['aseg'] = aseg_report(f)

    if 'dgm' in models:
        f = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_dgm')
        report_dicts['dgm'] = dgm_report(f)

    if 'dkt' in models:
        f_dkt = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_dkt')
        report_dicts['dkt'] = dkt_report(f_dkt)

        if 'ct' in models:
            f_ct = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_ct')
            report_dicts['ct'] = ct_report(f_ct, f_dkt)
    
    if 'syn' in models:
        f_dkt = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_syn')
        report_dicts['syn'] = syn_report(f_dkt)

    if 'wmp' in models:
        f = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_wmp')
        report_dicts['wmp'] = wmp_report(f)

    return report_dicts


def create_report_csv(fname, models):
    report_dicts = create_report_dicts(fname, models)

    for model, report_dict in report_dicts.items():
        csv_f = fname.split('.')[0] + f'_{model}.csv'
        with open(csv_f, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(report_dict.items())


if __name__ == '__main__':
    create_report_csv(r'output\CANDI_BPDwoPsy_030.nii.gz', ['aseg', 'dgm', 'wmp'])