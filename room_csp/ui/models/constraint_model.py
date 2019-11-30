import typing

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex


class ConstraintItem(object):
    parent = None
    children: list = None
    data: dict = None

    def __init__(self, data, parent=None):
        self.data = data
        self.children = []

        self.set_parent(parent)

    def __len__(self):
        return len(self.children)

    def set_parent(self, parent):
        self.parent = parent
        if parent is not None:
            parent.add_child(self)

    def get_parent(self):
        return self.parent

    def add_child(self, child):
        self.children.append(child)

    def get_child(self, row):
        return self.children[row]

    def get_row(self):
        if self.parent:
            return self.parent.children.index(self)

        return 0

    def get_column(self, column):
        try:
            return self.data[column]
        except (IndexError, KeyError):
            return None

    def get_column_count(self):
        return len(self.data)


class ConstraintModel(QAbstractItemModel):
    constraint_root: ConstraintItem = None

    def __init__(self, *args, constraints: dict = None, **kwargs):
        super(ConstraintModel, self).__init__(*args, **kwargs)
        self.constraint_root = ConstraintItem(["Personal constraints"])
        for participant, target_participants in constraints.items():
            source_constraint = ConstraintItem([participant], parent=self.constraint_root)
            for target_participant in target_participants:
                ConstraintItem([target_participant], parent=source_constraint)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.get_column(index.column())

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.constraint_root.get_column(section)

        return None

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = self.constraint_root
        if parent.isValid():
            parent_item = parent.internalPointer()

        child_item = parent_item.get_child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()

        child_item = child.internalPointer()
        parent_item = child_item.get_parent()

        if parent_item == self.constraint_root:
            return QModelIndex()

        return self.createIndex(parent_item.get_row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0

        parent_item = self.constraint_root
        if parent.isValid():
            parent_item = parent.internalPointer()

        return len(parent_item)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        parent_item = parent.internalPointer()
        if parent_item is not None:
            return parent_item.get_column_count()

        return self.constraint_root.get_column_count()
