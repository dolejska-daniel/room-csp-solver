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
            data = list(self.data.values())
            return data[column]
        except (IndexError, KeyError):
            return None

    def get_column_count(self):
        return len(self.data)


class ConstraintModel(QAbstractItemModel):
    constraint_root: ConstraintItem = None
    source_data: list = None

    def __init__(self, *args, constraints: list = None, **kwargs):
        super(ConstraintModel, self).__init__(*args, **kwargs)
        self.reload_data(constraints)

        self.layoutChanged.connect(self.update_source)
        self.dataChanged.connect(self.update_source)

    def reload_data(self, source_data: list):
        self.source_data = source_data
        self.source_to_tree()

    def add_entry(self, value: str, parent: str = None):
        if value == parent or value is None:
            return

        if parent is None:
            if value not in self.get_search_strings():
                self.source_data.append({
                    "participant": value,
                    "enabled": True,
                    "constraints": []
                })

        else:
            if parent not in self.get_search_strings():
                self.source_data.append({
                    "participant": value,
                    "enabled": True,
                    "constraints": []
                })

            index = self.get_search_strings().index(parent)
            self.source_data[index]["constraints"].append({
                "participant": value,
                "enabled": True,
                "constraints": []
            })

        self.source_to_tree()

    def toggle_entry(self, index: QModelIndex):
        index_item: ConstraintItem = index.internalPointer()
        index_item.toggle()

        self.dataChanged.emit(index, index, [])

    def get_search_strings(self) -> [str]:
        return [p["participant"] for p in self.source_data]

    def source_to_tree(self):
        self.beginResetModel()

        if self.constraint_root is None:
            self.constraint_root = ConstraintItem({"participant": "Participant name", "enabled": "Enabled"})
        else:
            self.constraint_root.children = []

        for source_participant in self.source_data:
            source_constraint = ConstraintItem({
                "participant": source_participant["participant"],
                "enabled": source_participant["enabled"],
            }, parent=self.constraint_root)
            for target_participant in source_participant["constraints"]:
                ConstraintItem({
                    "participant": target_participant["participant"],
                    "enabled": target_participant["enabled"],
                }, parent=source_constraint)

        self.endResetModel()
        self.layoutChanged.emit()

    def tree_to_source(self):
        return [
            {
                "participant": source_participant.get_column(0),
                "enabled": source_participant.get_column(1),
                "constraints": [
                    {
                        "participant": target_participant.get_column(0),
                        "enabled": target_participant.get_column(1),
                    }
                    for target_participant in source_participant.children
                ]
            }
            for source_participant in self.constraint_root.children
        ]

    def get_data_for_solver(self) -> dict:
        return {
            source_participant["participant"]: [
                target_participant["participant"]
                for target_participant in source_participant["constraints"]
                if target_participant["enabled"]
            ]
            for source_participant in self.source_data
            if source_participant["enabled"]
        }

    def update_source(self):
        self.source_data.clear()
        self.source_data = self.tree_to_source()

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
