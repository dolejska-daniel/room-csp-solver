from PyQt5.QtCore import Qt, QSortFilterProxyModel

from room_csp.ui.models import ParticipantModel


class ParticipantProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, source_model: ParticipantModel = None, **kwargs):
        super(ParticipantProxyModel, self).__init__(*args, **kwargs)
        self.setSourceModel(source_model)

        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(0)
