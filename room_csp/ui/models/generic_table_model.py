import copy
import typing

from PyQt5.QtCore import Qt, QModelIndex, QVariant, QAbstractTableModel, pyqtSignal


class GenericTableModel(QAbstractTableModel):
    WholeRowRole = 101

    layoutAboutToBeChanged: pyqtSignal
    layoutChanged: pyqtSignal

    header: list = None
    dataset: list = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.header = []
        self.dataset = []

    # ------------------------------------------------------dd--
    #   Custom methods
    # ------------------------------------------------------dd--

    def set_header(self, labels: list):
        self.header = [label.capitalize() for label in labels]

    def set_dataset(self, dataset: list):
        if not len(dataset):
            return

        self.layoutAboutToBeChanged.emit()

        self.set_header(list(dataset[0].keys()))
        self.dataset = dataset

        self.changePersistentIndexList(self.persistentIndexList(), self.persistentIndexList())
        self.layoutChanged.emit()

    def get_dataset(self) -> list:
        return copy.deepcopy(self.dataset)

    def add_item(self, item: dict):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        if not len(self.dataset):
            self.layoutAboutToBeChanged.emit()
            self.set_header(list(item.keys()))
            self.layoutChanged.emit()

        self.dataset.append(item)

        self.endInsertRows()

    def remove_item(self, index: QModelIndex = ...):
        self.layoutAboutToBeChanged.emit()
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())
        del self.dataset[index.row()]
        self.endRemoveRows()
        self.layoutChanged.emit()

    # ------------------------------------------------------dd--
    #   Header
    # ------------------------------------------------------dd--

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """ Returns the number of columns for the children of the given parent. """

        return len(self.header)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        """ Returns the data for the given role and section in the header with the specified orientation.

        For horizontal headers, the section number corresponds to the column number.
        Similarly, for vertical headers, the section number corresponds to the row number.
        """

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.header[section]

        return QVariant()

    # ------------------------------------------------------dd--
    #   Rows
    # ------------------------------------------------------dd--

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """ Returns the number of rows under the given parent.

        When the parent is valid it means that rowCount is returning the number of children of parent.
        """

        return len(self.dataset)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        """ Returns the data stored under the given role for the item referred to by the index. """
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            row_data = self.dataset[index.row()]
            row_data = list(row_data.values())
            return row_data[index.column()]

        if role == self.WholeRowRole:
            return self.dataset[index.row()]

        return QVariant()

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return False

        if role == Qt.EditRole:
            row: dict = self.dataset[index.row()]
            keys = list(row.keys())
            row[keys[index.column()]] = value

        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """ Returns the item flags for the given index. """

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
