import typing

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem


class GenericItem(QStandardItem):

    SaveRole = 101

    def __init__(self, key: str, value: typing.Any):
        super().__init__()

        self.key = key
        self.value = value

    def data(self, role: int = ...) -> typing.Any:
        if role == GenericItem.SaveRole:
            return self.key, self.value

        elif role == Qt.DisplayRole:
            return str(self.value)
