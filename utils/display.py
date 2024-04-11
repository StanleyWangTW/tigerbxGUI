import numpy as np
import matplotlib
import matplotlib.colors
from matplotlib.colors import ListedColormap

labels = [
    0, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24, 26, 28, 41, 42, 43, 44, 46, 47, 49,
    50, 51, 52, 53, 54, 58, 60
]


def color_show(img, minv, maxv, cmap):
    data = img.astype(np.float32)
    data = (data - minv) / (maxv - minv)
    data[data > 1] = 1
    data[data < 0] = 0

    colormap = matplotlib.colormaps[cmap]
    output = colormap(data)[..., :3] * 255

    return output.astype(np.uint8)


def get_cmap():
    # custom cmap for labels plotting
    rgb_colors = [(0, 0, 0), (245, 245, 245), (205, 62, 78), (120, 18, 134), (196, 58, 250),
                  (220, 248, 164), (230, 148, 34), (0, 118, 14), (122, 186, 220), (236, 13, 176),
                  (12, 48, 255), (204, 182, 142), (42, 204, 164), (119, 159, 176), (220, 216, 20),
                  (103, 255, 255), (60, 60, 60), (255, 165, 0), (165, 42, 42), (245, 245, 245),
                  (205, 62, 78), (120, 18, 134), (196, 58, 250), (220, 248, 164), (230, 148, 34),
                  (0, 118, 14), (122, 186, 220), (236, 13, 176), (13, 48, 255), (220, 216, 20),
                  (103, 255, 255), (255, 165, 0), (165, 42, 42)]

    # Convert RGB colors to the range [0, 1]
    colors = np.array(rgb_colors) / 255.0
    colors = np.zeros([labels[-1] + 1, 3])
    for idx, l in enumerate(labels):
        colors[l] = rgb_colors[idx]
        colors[l] /= 255.0

    # Create a ListedColormap
    return ListedColormap(colors)


if __name__ == '__main__':    
    import nibabel as nib
    data = nib.load(r'CANDI_BPDwoPsy_030.nii.gz').get_fdata()[100, :, :]
    print(get_cmap()(np.unique(data)) * 255)
    data = color_show(data, 0, 60, 'freesurfer')
    print(data)
    import matplotlib.pyplot as plt
    plt.imshow(data)
    plt.colorbar()
    plt.axis('off')  # 关闭坐标轴
    plt.show()
