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
        for key, values in file_dict.items():
            item = QTreeWidgetItem([key])
            for value in values:
                if basename(value) == key:
                    ftype = 'original'
                else:
                    ftype = basename(value).split('.')[0].split('_')[-1]

                child = QTreeWidgetItem([value, ftype])
                item.addChild(child)

            self.addTopLevelItem(item)

        self.expandAllItems()

    def expandAllItems(self):
        def recursive_expand(item):
            item.setExpanded(True)
            for i in range(item.childCount()):
                recursive_expand(item.child(i))

        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            recursive_expand(root.child(i))