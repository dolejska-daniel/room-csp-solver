from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot

from .generic_tree_model import GenericTreeModel


class ConstraintTreeModel(GenericTreeModel):

    def __init__(self, parent=None):
        super().__init__(parent)

    # ------------------------------------------------------dd--
    #   Method overrides
    # ------------------------------------------------------dd--

    def add_item(self, data: dict, parent_index: QModelIndex = QModelIndex()):
        # forbid parent-child duplicates
        if parent_index.isValid():
            parent_data = self.data(parent_index, Qt.DisplayRole)
            if data["name"] == parent_data:
                return False

        # forbid duplicates in given sub-level
        matching_items = self.findItems(data["name"], Qt.MatchExactly | Qt.MatchRecursive)
        for matching_item in matching_items:
            if matching_item.index().parent() == parent_index:
                return False

        # forbid nesting items too deep
        level = 0
        temp_index = parent_index
        while temp_index.isValid():
            level += 1
            temp_index = temp_index.parent()

        # maximum nesting 1 level
        if level > 1:
            return False

        return super().add_item(data, parent_index)

    # ------------------------------------------------------dd--
    #   Custom methods
    # ------------------------------------------------------dd--

    def toggle_item(self, index: QModelIndex):
        item_enabled_index = self.index(index.row(), 1, index.parent())
        item = self.itemFromIndex(item_enabled_index)
        item.value = not item.value
        self.dataChanged.emit(item_enabled_index, item_enabled_index)

    @pyqtSlot(str, str)
    def on_participant_renamed(self, old_name: str, new_name: str):
        items = self.findItems(old_name, Qt.MatchExactly | Qt.MatchRecursive, 0)
        for item in items:
            item.value = new_name
            self.dataChanged.emit(item.index(), item.index())

    @pyqtSlot(str)
    def on_participant_removed(self, participant_name: str):
        items = self.findItems(participant_name, Qt.MatchExactly | Qt.MatchRecursive, 0)
        for item in items:
            self.removeRow(item.index().row(), item.index().parent())
