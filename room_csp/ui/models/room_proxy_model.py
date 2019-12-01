import typing

from PyQt5.QtCore import Qt, QSortFilterProxyModel

from room_csp.ui.models import RoomModel


class RoomProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, source_model: RoomModel = None, **kwargs):
        super(RoomProxyModel, self).__init__(*args, **kwargs)
        self.setSourceModel(source_model)

        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(0)
