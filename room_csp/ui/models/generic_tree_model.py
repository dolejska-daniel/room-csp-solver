from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from room_csp.ui.models import GenericItem


class GenericTreeModel(QStandardItemModel):
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
        for entry in dataset:
            row = self.create_item_row(entry)
            parent.appendRow(row)

        self.dataset_keys = {key for key in dataset[0].keys() if key != "_items"}
        self.setHorizontalHeaderLabels([key.capitalize() for key in self.dataset_keys])

        self.changePersistentIndexList(self.persistentIndexList(), self.persistentIndexList())
        self.layoutChanged.emit()

        self.get_dataset()

    def get_dataset(self) -> [dict]:
        dataset = []
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            item_index = self.index(row, 0)
            item_data = {}
            for column in range(self.columnCount()):
                key, value = self.itemFromIndex(self.index(row, column)).data(GenericItem.SaveRole)
                item_data[key] = value

            for sub_row in range(item.rowCount()):
                if "_items" not in item_data:
                    item_data["_items"] = []

                sub_item_data = {}
                for sub_column in range(item.columnCount()):
                    sub_item = self.itemFromIndex(self.index(sub_row, sub_column, item_index))
                    key, value = sub_item.data(GenericItem.SaveRole)
                    sub_item_data[key] = value

                item_data["_items"].append(sub_item_data)

            dataset.append(item_data)

        return dataset

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
