from os.path import basename

from PySide6.QtWidgets import QListWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem


class FileList(QListWidget):
    def __init__(self):
        super(FileList, self).__init__()


class FileTree(QTreeWidget):
    def __init__(self):
        super(FileTree, self).__init__()
        self.setHeaderLabels(['Name', 'Seg. mode'])

    def loadData(self, file_dict):
        self.clear()
        items = list()
        for key, values in file_dict.items():
            item = QTreeWidgetItem([key])
            for value in values:
                if basename(value) == key:
                    ftype = 'original'
                else:
                    ftype = basename(value).split('.')[0].split('_')[-1]

                child = QTreeWidgetItem([value, ftype])
                item.addChild(child)

            items.append(item)

        self.addTopLevelItems(items)