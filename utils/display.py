import numpy as np
import matplotlib
import matplotlib.colors

from . import label


def color_show(img, minv, maxv, cmap):
    data = img.astype(np.float32)

    if cmap == 'freesurfer':
        return freesurfer_cmap(img)
    
    data = (data - minv) / (maxv - minv)
    data[data > 1] = 1
    data[data < 0] = 0
    colormap = matplotlib.colormaps[cmap]
    return colormap(data)[..., :3] * 255

def overlay_color_show(overlay, current_labels):
    output = np.zeros(overlay.shape + (4,))
    for value in np.unique(overlay):
        if value == 0 or value not in current_labels.keys():
            for c in range(4): # rgba channels
                (output[..., c])[overlay == value] = 0
        else:
            for c in range(4): # rgba channels
                (output[..., c])[overlay == value] = current_labels[value].rgba[c]

    return output.astype(np.uint8)

def freesurfer_cmap(img):
    output = np.zeros(img.shape + (3,))

    labels = label.load_labels()
    for value in np.unique(img):
        if value not in labels.keys():
            continue

        for c in range(3): # rgb channels
            (output[..., c])[img == value] = labels[value].rgba[c]

    return output