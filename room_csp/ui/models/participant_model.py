import typing

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex


class ParticipantModel(QAbstractTableModel):
    participants: dict = None

    def __init__(self, *args, participants: dict = None, **kwargs):
        super(ParticipantModel, self).__init__(*args, **kwargs)
        self.participants = participants or {}

    def add_entry(self, key: str, data: dict):
        self.participants[key] = data
        self.layoutChanged.emit()

    def get_search_strings(self) -> [str]:
        return list(self.participants.keys())

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            value: dict = list(self.participants.values())[index.row()]
            return list(value.values())[index.column()]

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == Qt.EditRole:
            if value == "":
                return False

            row_key = list(self.participants.keys())[index.row()]
            row: dict = self.participants[row_key]
            column_key = list(row.keys())[index.column()]

            self.participants[row_key][column_key] = value
            self.dataChanged.emit(index, index, [role])
            return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        participant_example = list(self.participants.values()).pop()
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            key = list(participant_example.keys())[section]
            return key.capitalize()

        return None

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.participants)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        participant_example: dict = list(self.participants.values()).pop()
        return len(participant_example.keys())

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = Qt.ItemIsEnabled | Qt.ItemIsEditable

        # name column
        if index.column() == 0:
            flags |= Qt.ItemIsSelectable

        return flags

