import typing

from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal

from .generic_table_model import GenericTableModel


class ParticipantTableModel(GenericTableModel):
    participant_renamed = pyqtSignal(str, str)
    participant_removed = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

    # ------------------------------------------------------dd--
    #   Method overrides
    # ------------------------------------------------------dd--

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.column() == 0:
            # changing participant's name
            for row in self.dataset:
                row_value = list(row.values())[0]
                if row_value == value:
                    # forbid duplicate names
                    return False

        old_value = self.data(index, Qt.DisplayRole)
        self.participant_renamed.emit(old_value, value)
        return super().setData(index, value, role)

    def remove_item(self, index: QModelIndex = ...):
        # remove any related constraints
        participant_name = self.data(index, Qt.DisplayRole)
        self.participant_removed.emit(participant_name)

        # remove participant row
        super().remove_item(index)
