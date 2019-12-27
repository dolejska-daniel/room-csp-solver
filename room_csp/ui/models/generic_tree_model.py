from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel

from .generic_item import GenericItem


class GenericTreeModel(QStandardItemModel):
    layoutAboutToBeChanged: pyqtSignal
    layoutChanged: pyqtSignal

    dataset_keys: set = None

    def __init__(self, parent=None):
        super().__init__(parent)

    # ------------------------------------------------------dd--
    #   Custom methods
    # ------------------------------------------------------dd--

    def set_dataset(self, dataset: list):
        if not len(dataset):
            return

        self.layoutAboutToBeChanged.emit()

        parent = self.invisibleRootItem()
        parent.removeRows(0, parent.rowCount())
        for entry in dataset:
            row = self.create_item_row(entry)
            parent.appendRow(row)

        self.dataset_keys = {key for key in dataset[0].keys() if key != "_items"}
        self.setHorizontalHeaderLabels([key.capitalize() for key in self.dataset_keys])

        self.changePersistentIndexList(self.persistentIndexList(), self.persistentIndexList())
        self.layoutChanged.emit()

    def get_dataset(self) -> [dict]:
        dataset = []
        for row in range(self.rowCount()):
            row_data = self.get_dataset_row(self.index(row, 0))
            dataset.append(row_data)

        return dataset

    def get_dataset_row(self, index: QModelIndex):
        row_data = {"_items": []}
        for column in range(self.columnCount()):
            item_column = self.itemFromIndex(self.index(index.row(), column, index.parent()))
            key, value = item_column.data(GenericItem.SaveRole)
            row_data[key] = value

        for sub_row in range(self.itemFromIndex(index).rowCount()):
            sub_item_data = self.get_dataset_row(self.index(sub_row, 0, index))
            row_data["_items"].append(sub_item_data)

        return row_data

    def create_item_row(self, data: dict) -> [GenericItem]:
        if not len(data):
            return []

        items = []
        sub_items = []
        for key, value in data.items():
            if key == "_items":
                sub_items = value
                continue

            item = GenericItem(key, value)
            items.append(item)

        for sub_data in sub_items:
            items[0].appendRow(self.create_item_row(sub_data))

        return items

    def add_item(self, data: dict, parent_index: QModelIndex = QModelIndex()):
        parent = self.invisibleRootItem()
        if parent_index.isValid():
            parent = self.itemFromIndex(parent_index)

        parent.appendRow(self.create_item_row(data))
        return True

    def remove_item(self, index: QModelIndex = ...):
        self.removeRow(index.row(), index.parent())

    # ------------------------------------------------------dd--
    #   Method overrides
    # ------------------------------------------------------dd--

    def flags(self, index: QtCore.QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
