import numpy as np
import matplotlib
import matplotlib.colors
from matplotlib.colors import ListedColormap




def color_show(img, minv, maxv, cmap):
    data = img.astype(np.float32)

    if cmap == 'freesurfer':
        return freesurfer_cmap(img)
    
    data = (data - minv) / (maxv - minv)
    data[data > 1] = 1
    data[data < 0] = 0
    colormap = matplotlib.colormaps[cmap]
    return colormap(data)[..., :3] * 255


def freesurfer_cmap(img):
    labels = [
        0, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24, 26, 28,
        41, 42, 43, 44, 46, 47, 49, 50, 51, 52, 53, 54, 58, 60
    ]

    rgb_colors = [(0, 0, 0), (245, 245, 245), (205, 62, 78), (120, 18, 134), (196, 58, 250),
                  (220, 248, 164), (230, 148, 34), (0, 118, 14), (122, 186, 220), (236, 13, 176),
                  (12, 48, 255), (204, 182, 142), (42, 204, 164), (119, 159, 176), (220, 216, 20),
                  (103, 255, 255), (60, 60, 60), (255, 165, 0), (165, 42, 42), (245, 245, 245),
                  (205, 62, 78), (120, 18, 134), (196, 58, 250), (220, 248, 164), (230, 148, 34),
                  (0, 118, 14), (122, 186, 220), (236, 13, 176), (13, 48, 255), (220, 216, 20),
                  (103, 255, 255), (255, 165, 0), (165, 42, 42)]

    temp = np.stack([img,] * 3, axis=2)
    output = np.zeros(temp.shape)
    for i, label in enumerate(labels):
        mask = temp == label
        color_broadcasted = np.broadcast_to(np.array(rgb_colors[i]), mask.shape)
        output[mask] = color_broadcasted[mask]

    return output
