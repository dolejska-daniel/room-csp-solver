import typing

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal


class RoomModel(QAbstractTableModel):
    rooms: dict = None

    def __init__(self, *args, rooms: dict = None, **kwargs):
        super(RoomModel, self).__init__(*args, **kwargs)
        self.rooms = rooms or {}

    def add_entry(self, key: str, data: dict):
        self.rooms[key] = data
        self.layoutChanged.emit()

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            value: dict = list(self.rooms.values())[index.row()]
            return list(value.values())[index.column()]

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == Qt.EditRole:
            if value == "":
                return False

            row_key = list(self.rooms.keys())[index.row()]
            row: dict = self.rooms[row_key]
            column_key = list(row.keys())[index.column()]

            self.rooms[row_key][column_key] = value
            self.dataChanged.emit(index, index, [role])
            return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        example_room = list(self.rooms.values()).pop()
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            key = list(example_room.keys())[section]
            return key.capitalize()

        return None

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.rooms)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        room_example: dict = list(self.rooms.values()).pop()
        return len(room_example.keys())

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = Qt.ItemIsEnabled | Qt.ItemIsEditable

        if index.column() == 0:
            flags |= Qt.ItemIsSelectable

        return flags
