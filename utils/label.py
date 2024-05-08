import numpy as np

LABEL_LUT = r'FreeSurferColorLUT.txt'

DGM_LABEL = {
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
}

label_all = dict()
label_all['aseg'] = (2,3,4,5,7,8,10,11,12,13,14,15,16,17,18,24,26,28,30,31,41,42,43,
                44,46,47,49,50,51,52,53,54,58,60,62,63,77,85,251,252,253,254,255)

label_all['dkt'] = ( 1002, 1003,
               1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015,
               1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026,
               1027, 1028, 1029, 1030, 1031, 1034, 1035, 2002, 2003, 2005, 2006,
               2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017,
               2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028,
               2029, 2030, 2031, 2034, 2035)

label_all['wmp'] = (  251,  252,  253,  254,  255, 3001, 3002, 3003, 3005, 3006, 3007,
                     3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018,
                     3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029,
                     3030, 3031, 3032, 3033, 3034, 3035, 4001, 4002, 4003, 4005, 4006,
                     4007, 4008, 4009, 4010, 4011, 4012, 4013, 4014, 4015, 4016, 4017,
                     4018, 4019, 4020, 4021, 4022, 4023, 4024, 4025, 4026, 4027, 4028,
                     4029, 4030, 4031, 4032, 4033, 4034, 4035)

label_all['synthseg'] = ( 2,  3,  4,  5,  7,  8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24,
                          26, 28, 41, 42, 43, 44, 46, 47, 49, 50, 51, 52, 53, 54, 58, 60)


class Label():
    def __init__(self, name, rgba):
        self.name = name
        self.rgba = np.array(rgba)


def load_labels():
    labels  = dict()
    with open(LABEL_LUT, 'r') as f:
        for line in f:
            parts = line.strip().split()

            if not parts or parts[0].startswith('#'):
                continue

            number = int(parts[0])
            name = parts[1]
            rgba = list(map(int, parts[2:]))

            labels[number] = Label(name, rgba)

    return labels
