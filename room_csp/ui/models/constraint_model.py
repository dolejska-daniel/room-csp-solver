import typing

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QMimeData


class ConstraintItem(object):
    parent = None
    children: list = None
    data: dict = None

    def __init__(self, data: dict, parent=None):
        if "enabled" not in data:
            data["enabled"] = True

        self.data = data
        self.children = []

        self.set_parent(parent)

    def __len__(self):
        return len(self.children)

    def toggle(self):
        self.data["enabled"] = not self.data["enabled"]

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
        if self.parent is not None:
            return self.parent.children.index(self)

        return 0

    def get_column(self, column):
        try:
            return list(self.data.values())[column]
        except (IndexError, KeyError):
            return None

    def get_column_count(self):
        return len(self.data)


class ConstraintModel(QAbstractItemModel):
    constraint_root: ConstraintItem = None
    source_data: dict = None

    def __init__(self, *args, constraints: dict = None, **kwargs):
        super(ConstraintModel, self).__init__(*args, **kwargs)
        self.reload_data(constraints)

        self.layoutChanged.connect(self.update_source)
        self.dataChanged.connect(self.update_source)

    def reload_data(self, source_data: dict):
        self.source_data = source_data
        self.source_to_tree()

    def add_entry(self, value: str, parent: str = None):
        if value == parent or value is None:
            return

        if parent is None:
            if value not in self.source_data:
                self.source_data[value] = []

        else:
            if parent not in self.source_data:
                self.source_data[parent] = []
            self.source_data[parent].append(value)

        self.source_to_tree()

    def toggle_entry(self, index: QModelIndex):
        index_item: ConstraintItem = index.internalPointer()
        index_item.toggle()

        self.dataChanged.emit(index, index, [])

    def get_search_strings(self) -> [str]:
        return list(self.source_data.keys())

    def source_to_tree(self):
        self.beginResetModel()

        if self.constraint_root is None:
            self.constraint_root = ConstraintItem({"participant": "Participant", "enabled": "Enabled"})
        else:
            self.constraint_root.children = []

        for participant, target_participants in self.source_data.items():
            source_constraint = ConstraintItem({"participant": participant}, parent=self.constraint_root)
            for target_participant in target_participants:
                ConstraintItem({"participant": target_participant}, parent=source_constraint)

        self.endResetModel()
        self.layoutChanged.emit()

    def tree_to_source(self, output: dict = None):
        for participant_constraints in self.constraint_root.children:
            participant_constraints: ConstraintItem
            data = list(participant_constraints.data.values())

            participant = data[0]
            output[participant] = []
            for constraint in participant_constraints.children:
                output[participant].append(constraint.data)

    def get_data_for_solver(self) -> dict:
        # TODO: Fix creation of data for solver
        return {
            source_participant: [
                target_participant
                for target_participant in constraints
            ]
            for source_participant, constraints in self.source_data.items()
        }

    def update_source(self):
        self.source_data.clear()
        self.tree_to_source(self.source_data)

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
