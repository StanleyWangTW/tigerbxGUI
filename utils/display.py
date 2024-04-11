import numpy as np


class Colormap:

    def __init__(self, name, points, type='2P'):
        self.name = name
        self.type = type

        self.points = list()
        for p in points:
            self.points.append(np.array(p))


Gray = Colormap('Gray', [(0, 0, 0), (255, 255, 255)], '2P')

Red = Colormap('Red', [(0, 0, 0), (255, 0, 0)], '2P')
Blue = Colormap('Blue', [(0, 0, 0), (0, 0, 255)], '2P')
Green = Colormap('Green', [(0, 0, 0), (0, 255, 0)], '2P')

Violet = Colormap('Violet', [(0, 0, 0), (255, 0, 255)], '2P')
Yellow = Colormap('Yellow', [(0, 0, 0), (255, 255, 0)], '2P')
Cyan = Colormap('Cyan', [(0, 0, 0), (0, 255, 255)], '2P')

CMAPS = [Gray, Red, Blue, Green, Violet, Yellow, Cyan]


def color_show(img, minv, maxv, cmap):
    for cm in CMAPS:
        if cm.name == cmap:
            cmap = cm
            break

    img = (img - minv) / (maxv - minv)
    img[img > 1] = 1
    img[img < 0] = 0

    points = cmap.points
    img_list = list()
    for i in range(3):  # through RGB 3 channels
        channel = img * (points[1][i] - points[0][i]) + points[0][i]
        img_list.append(channel)

    output = np.stack(img_list, axis=2)
    return output.astype(np.uint8)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import nibabel as nib
    data = nib.load(r'test_file\CANDI_BPDwoPsy_030.nii.gz').get_fdata()[100, :, :]
    data = color_show(data, 4, 112, Violet)
    plt.imshow(data)
    plt.axis('off')  # 关闭坐标轴
    plt.show()