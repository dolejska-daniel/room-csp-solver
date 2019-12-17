import typing

from PyQt5.QtCore import QModelIndex, Qt

from .generic_table_model import GenericTableModel


class ParticipantTableModel(GenericTableModel):
    main_window = None

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.column() == 0:
            # changing participant's name
            for row in self.dataset:
                row_value = list(row.values())[0]
                if row_value == value:
                    return False

        old_value = self.data(index, Qt.DisplayRole)
        self.main_window.constraint_model.change_participant_name(old_value, value)
        return super().setData(index, value, role)
