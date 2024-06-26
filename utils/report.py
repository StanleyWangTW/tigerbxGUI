import csv  
from os.path import basename

import numpy as np
import nibabel as nib

from .label import label_all, LABEL_DATA, DGM_LABEL
# from label import label_all, LABEL_DATA, DGM_LABEL

def get_volume(nii, label):
    zoom = nii.header.get_zooms()
    voxel_size = zoom[0] * zoom[1] * zoom[2]
    data = nii.get_fdata()
    return np.sum(data == label) * voxel_size


def aseg_report(fname):
    nii = nib.load(fname)
    report = [['Structure Name', 'Volume(mm^3)']]
    for number in label_all['aseg']:
        report.append([LABEL_DATA[number].name, round(get_volume(nii, number))])

    return report

def bam_report(fname_bam, fname_seg):
    bam = nib.load(fname_bam).get_fdata()
    seg = nib.load(fname_seg).get_fdata()
    report =  [['Structure Name', 'Average Brain Age(year)']]
    for number in np.unique(seg)[1:]:
        average_brain_age = round(np.sum(bam[seg == number])  / np.sum(seg == number), 3)
        report.append([LABEL_DATA[number].name, average_brain_age])

    return report


def dgm_report(fname):
    nii = nib.load(fname)
    report = [['Structure Name', 'Volume(mm^3)']]
    for name, number in DGM_LABEL.items():
        report.append([name, round(get_volume(nii, number))])

    return report


def dkt_report(fname):
    nii = nib.load(fname)
    report = [['Structure Name', 'Volume(mm^3)']]
    for number in label_all['dkt']:
        report.append([LABEL_DATA[number].name, round(get_volume(nii, number))])

    return report

def ct_report(fname_ct, fname_dkt):
    ct = nib.load(fname_ct).get_fdata()
    dkt = nib.load(fname_dkt).get_fdata()
    report = [['Structure Name', 'Average Cortical Thickness(mm)']]
    for number in label_all['dkt']:
        average_ct = round(np.sum(ct[dkt == number])  / np.sum(dkt == number), 3)
        report.append([LABEL_DATA[number].name, average_ct])

    return report


def pve_report(fname_pve: str, fname_seg: str) -> list:
    pve = nib.load(fname_pve).get_fdata()
    seg = nib.load(fname_seg).get_fdata()
    report = [['Structure Name', 'mean', 'std']]
    for number in np.unique(seg)[1:]:
        mean = round(np.mean(pve[seg == number]), 3)
        std = round(np.std(pve[seg == number]), 3)
        report.append([LABEL_DATA[number].name, mean, std])

    return report


def syn_report(fname):
    nii = nib.load(fname)
    report = [['Structure Name', 'Volume(mm^3)']]
    for number in label_all['synthseg']:
        report.append([LABEL_DATA[number].name, round(get_volume(nii, number))])

    return report


def wmp_report(fname):
    nii = nib.load(fname)
    report = [['Structure Name', 'Volume(mm^3)']]
    for number in label_all['wmp']:
        report.append([LABEL_DATA[number].name, round(get_volume(nii, number))])

    return report

def wmh_report(fname_wmh, fname_wmp):
    nii_wmh = nib.load(fname_wmh)
    zoom = nii_wmh.header.get_zooms()
    voxel_size = zoom[0] * zoom[1] * zoom[2]

    wmh = nii_wmh.get_fdata()
    wmp = nib.load(fname_wmp).get_fdata()

    report = [['Structure Name', 'Volume(mm^3)', 'Ratio(%)']]
    for number in label_all['wmp']:
        vol = round(np.sum(wmh[wmp == number]) * voxel_size, 3) 
        ratio = round(np.sum(wmh[wmp == number]) / np.sum(wmp == number) * 100, 3)
        report.append([LABEL_DATA[number].name, vol, ratio])

    return report


def create_report_dicts(fname, models):
    report_dicts = dict()
    if 'aseg' in models:
        f_aseg = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_aseg')
        report_dicts['aseg'] = aseg_report(f_aseg)

    if 'dgm' in models:
        f_dgm = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_dgm')
        report_dicts['dgm'] = dgm_report(f_dgm)

    if 'dkt' in models:
        f_dkt = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_dkt')
        report_dicts['dkt'] = dkt_report(f_dkt)

        if 'ct' in models:
            f_ct = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_ct')
            report_dicts['ct'] = ct_report(f_ct, f_dkt)
    
    if 'syn' in models:
        f_syn = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_syn')
        report_dicts['syn'] = syn_report(f_syn)

    if 'wmp' in models:
        f_wmp = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_wmp')
        report_dicts['wmp'] = wmp_report(f_wmp)

        if 'wmh' in models:
            f_wmh = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_wmh')
            report_dicts['wmh'] = wmh_report(f_wmh, f_wmp)

    if 'pve' in models:
        # # full brain labels
        # if 'aseg' in models:    
        #     report_dicts['bam'] = bam_report(f_bam, f_aseg)
        # elif 'syn' in models:
        #     report_dicts['bam'] = bam_report(f_bam, f_dgm)
        
        # else:
        if 'dkt' in models: # gray matter
            f_pve = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + f'_cgw_pve1')
            report_dicts['cgw_pve1'] = pve_report(f_pve, f_dkt)

        if 'wmp' in models: # white matter
            f_pve = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + f'_cgw_pve2')
            report_dicts['cgw_pve2'] = pve_report(f_pve, f_wmp)
            


    if 'bam' in models:
        f_bam = fname.replace(basename(fname).split('.')[0], basename(fname).split('.')[0] + '_bam')

        if 'aseg' in models:    
            report_dicts['bam'] = bam_report(f_bam, f_aseg)
        elif 'syn' in models:
            report_dicts['bam'] = bam_report(f_bam, f_syn)
        elif 'dgm' in models:
            report_dicts['bam'] = bam_report(f_bam, f_dgm)

    return report_dicts


def create_report_csv(fname, models):
    report_dicts = create_report_dicts(fname, models)

    for model, report in report_dicts.items():
        csv_f = fname.split('.')[0] + f'_{model}.csv'
        with open(csv_f, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(report)


if __name__ == '__main__':
    create_report_csv(r'output\CANDI_BPDwoPsy_030.nii.gz', ['bam', 'aseg', 'dgm', 'syn'])