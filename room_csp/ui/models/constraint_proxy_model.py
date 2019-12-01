import typing

from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QMimeData, QRegExp

from room_csp.ui.models import ConstraintModel


class ConstraintProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, source_model: ConstraintModel = None, **kwargs):
        super(ConstraintProxyModel, self).__init__(*args, **kwargs)
        self.setSourceModel(source_model)

        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(0)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        regexp: QRegExp = self.filterRegExp()
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        if source_index.parent().isValid():
            source_index = source_index.parent()

        data = self.sourceModel().data(source_index, Qt.DisplayRole)
        accepts = regexp.exactMatch(data)
        if not accepts:
            item = source_index.internalPointer()
            for child in item.children:
                data = child.get_column(0)
                accepts = regexp.exactMatch(data)
                if accepts:
                    break

        return accepts
