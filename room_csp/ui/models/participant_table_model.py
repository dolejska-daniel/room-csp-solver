import typing

from PyQt5.QtCore import QModelIndex

from .generic_table_model import GenericTableModel
from .generic_tree_model import GenericTreeModel


class ParticipantTableModel(GenericTableModel):
    constraint_model: GenericTreeModel = None

    def __init__(self, constraint_model: GenericTreeModel, parent=None):
        super().__init__(parent)
        self.constraint_model = constraint_model

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        # TODO: Check whether data doesn't already exist and reject
        # TODO: Check whether data doesn't already exist in constraint model and update
        return super().setData(index, value, role)
