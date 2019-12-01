import typing

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt


class SolutionItem(object):
    parent = None
    children: list = None
    data: dict = None

    def __init__(self, data: dict, parent=None):
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


class SolutionModel(QAbstractItemModel):
    solution_root: SolutionItem = None
    source_data: dict = None

    def __init__(self, *args, **kwargs):
        super(SolutionModel, self).__init__(*args, **kwargs)
        self.reload_data({})

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

    def get_search_strings(self) -> [str]:
        return list(self.source_data.keys())

    def source_to_tree(self):
        self.beginResetModel()

        if self.solution_root is None:
            self.solution_root = SolutionItem({"participant": "Participant"})
        else:
            self.solution_root.children = []

        rooms = {}
        for room_slot, participant in self.source_data.items():
            room_name = room_slot.split('_')[0]
            if room_name not in rooms:
                rooms[room_name] = SolutionItem({"room_name": room_name}, parent=self.solution_root)

            SolutionItem({"participant": participant}, parent=rooms[room_name])

        self.endResetModel()
        self.layoutChanged.emit()

    def tree_to_source(self, output: dict = None):
        for participant_constraints in self.solution_root.children:
            participant_constraints: SolutionItem
            data = list(participant_constraints.data.values())

            participant = data[0]
            output[participant] = []
            for constraint in participant_constraints.children:
                output[participant].append(constraint.data)

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
            return self.solution_root.get_column(section)

        return None

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = self.solution_root
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

        if parent_item == self.solution_root:
            return QModelIndex()

        return self.createIndex(parent_item.get_row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0

        parent_item = self.solution_root
        if parent.isValid():
            parent_item = parent.internalPointer()

        return len(parent_item)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        parent_item = parent.internalPointer()
        if parent_item is not None:
            return parent_item.get_column_count()

        return self.solution_root.get_column_count()
