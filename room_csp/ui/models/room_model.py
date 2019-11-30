import typing

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex


class RoomModel(QAbstractTableModel):
    rooms: dict = None

    def __init__(self, *args, rooms: dict = None, **kwargs):
        super(RoomModel, self).__init__(*args, **kwargs)
        self.rooms = rooms or {}

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            value: dict = list(self.rooms.values())[index.row()]
            return list(value.values())[index.column()]

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
        return Qt.ItemIsEnabled
