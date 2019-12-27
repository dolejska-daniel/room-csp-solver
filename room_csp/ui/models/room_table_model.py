import typing

from PyQt5.QtCore import QModelIndex

from .generic_table_model import GenericTableModel


class RoomTableModel(GenericTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)

    # ------------------------------------------------------dd--
    #   Method overrides
    # ------------------------------------------------------dd--

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.column() == 0:
            # changing room's name
            for row in self.dataset:
                row_value = list(row.values())[0]
                if row_value == value:
                    return False

        return super().setData(index, value, role)
