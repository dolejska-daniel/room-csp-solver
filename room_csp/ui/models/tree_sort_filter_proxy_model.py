from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex


class TreeSortFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not super().filterAcceptsRow(source_row, source_parent):
            if not source_parent.isValid():
                return False

            parent_row = source_parent.row()
            grandparent = source_parent.parent()
            return self.filterAcceptsRow(parent_row, grandparent)

        return True
