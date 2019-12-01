from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QItemSelection, QModelIndex, QItemSelectionModel, QRegExp
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView

from room_csp import Container
from room_csp.ui.models.constraint_model import ConstraintModel
from room_csp.ui.models.participant_model import ParticipantModel
from room_csp.ui.models.room_model import RoomModel
from room_csp.ui.windows.create_participant_dialog import CreateParticipantDialog
from room_csp.ui.windows.create_room_dialog import CreateRoomDialog

qt_creator_file = "ui/main_window.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    # -------------------------------------------------dd--
    #   participant_search variables
    # -------------------------------------------------dd--
    participant_search: QtWidgets.QLineEdit = None
    participant_search_completer: QtWidgets.QCompleter = None

    # -------------------------------------------------dd--
    #   constraint_search variables
    # -------------------------------------------------dd--
    constraint_search: QtWidgets.QLineEdit = None
    constraint_search_completer: QtWidgets.QCompleter = None

    # -------------------------------------------------dd--
    #   solution_tree variables
    # -------------------------------------------------dd--
    solution_tree: QtWidgets.QTreeView = None

    # -------------------------------------------------dd--
    #   constraint_tree variables
    # -------------------------------------------------dd--
    constraint_tree: QtWidgets.QTreeView = None
    constraint_model: ConstraintModel = None
    constraint_proxy_model: QtCore.QSortFilterProxyModel = None

    # -------------------------------------------------dd--
    #   participant_table variables
    # -------------------------------------------------dd--
    participant_table: QtWidgets.QTableView = None
    participant_model: ParticipantModel = None
    participant_proxy_model: QtCore.QSortFilterProxyModel = None

    # -------------------------------------------------dd--
    #   room_table variables
    # -------------------------------------------------dd--
    room_table: QtWidgets.QTableView = None
    room_model: RoomModel = None
    room_proxy_model: QtCore.QSortFilterProxyModel = None

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.setWindowTitle("ESC Room CSP Solver")
        # self.setMinimumSize(600 + 400, 400)

        self.setup_menu_actions()

        self.setup_participant_table()
        self.setup_room_table()
        self.setup_constraint_tree()
        self.setup_solution_tree()

        self.setup_participant_search()
        self.setup_constraint_search()

    # ---------------------------------------------------------------------dd--
    #   Menu action setup
    # ---------------------------------------------------------------------dd--
    def setup_menu_actions(self):
        self.findChild(QtWidgets.QAction, "actionLoad").triggered.connect(self.action_load)
        self.findChild(QtWidgets.QAction, "actionLoadRooms").setEnabled(False)
        self.findChild(QtWidgets.QAction, "actionLoadParticipants").setEnabled(False)
        self.findChild(QtWidgets.QAction, "actionLoadConstraints").setEnabled(False)
        self.findChild(QtWidgets.QAction, "actionSave").triggered.connect(self.action_save)
        self.findChild(QtWidgets.QAction, "actionSaveSolution").triggered.connect(self.action_save_solution)
        self.findChild(QtWidgets.QAction, "actionExit").triggered.connect(lambda _: exit(0))

        self.findChild(QtWidgets.QMenu, "menuFocus").setTitle("")
        self.findChild(QtWidgets.QAction, "actionFocusParticipantSearch") \
            .triggered.connect(lambda _: self.participant_search.setFocus())
        self.findChild(QtWidgets.QAction, "actionFocusConstraintSearch") \
            .triggered.connect(lambda _: self.constraint_search.setFocus())

        self.findChild(QtWidgets.QAction, "actionCreateParticipant").triggered.connect(self.action_create_participant)
        self.findChild(QtWidgets.QAction, "actionDeleteParticipant").triggered.connect(self.action_delete_participant)

        self.findChild(QtWidgets.QAction, "actionCreateConstraintFromSelection") \
            .triggered.connect(self.action_create_constraint_from_selection)
        self.findChild(QtWidgets.QAction, "actionDeleteConstraint").triggered.connect(self.action_delete_constraint)

        self.findChild(QtWidgets.QAction, "actionCreateRoom").triggered.connect(self.action_create_room)
        self.findChild(QtWidgets.QAction, "actionDeleteRoom").triggered.connect(self.action_delete_room)

        self.findChild(QtWidgets.QAction, "actionSolve").triggered.connect(self.action_solve)

        self.findChild(QtWidgets.QAction, "actionAbout").triggered.connect(self.action_about)

    def action_about(self):
        pass

    def action_solve(self):
        pass

    def action_delete_room(self):
        pass

    def action_create_room(self):
        dialog = CreateRoomDialog(self.room_model, parent=self)
        dialog.exec_()

    def action_delete_constraint(self):
        pass

    def action_create_constraint_from_selection(self):
        pass

    def action_delete_participant(self):
        pass

    def action_create_participant(self):
        dialog = CreateParticipantDialog(self.participant_model, parent=self)
        dialog.exec_()

    def action_save_solution(self):
        pass

    def action_save(self):
        pass

    def action_load(self):
        pass

    # ---------------------------------------------------------------------dd--
    #   Participant search field and proxy model setup
    # ---------------------------------------------------------------------dd--
    def setup_participant_search(self):
        participant_search: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, "ParticipantSearch")
        participant_search.textChanged.connect(self.participant_filter_update)
        participant_search.keyReleaseEvent = self.participant_search_keyup
        participant_search.setFocusPolicy(Qt.StrongFocus)

        self.participant_search = participant_search

        strings = self.participant_model.get_search_strings()
        self.setup_participant_search_completer(strings)

    def setup_participant_search_completer(self, strings: [str]):
        completer = QtWidgets.QCompleter(strings)
        completer.setCompletionMode(completer.PopupCompletion)

        self.participant_search.setCompleter(completer)

    def participant_filter_update(self, value: str):
        regexp = QtCore.QRegExp(f".*{value.replace(' ', '.*')}.*", Qt.CaseInsensitive)
        self.participant_proxy_model.setFilterRegExp(regexp)

    def participant_search_keyup(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.participant_search.setText("")
        elif event.key() == Qt.Key_Return:
            if self.participant_proxy_model.rowCount() == 1:
                index = self.participant_proxy_model.index(0, 0)
                self.participant_table.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)
            else:
                self.participant_table.selectionModel().clear()

    # ---------------------------------------------------------------------dd--
    #   Constraint search field and proxy model setup
    # ---------------------------------------------------------------------dd--
    def setup_constraint_search(self):
        constraint_search: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, "ConstraintSearch")
        constraint_search.textChanged.connect(self.constraint_filter_update)
        constraint_search.keyReleaseEvent = self.constraint_search_keyup
        constraint_search.setFocusPolicy(Qt.StrongFocus)

        self.constraint_search = constraint_search

        strings = self.constraint_model.get_search_strings()
        self.setup_constraint_search_completer(strings)

    def setup_constraint_search_completer(self, strings: [str]):
        completer = QtWidgets.QCompleter(strings)
        completer.setCompletionMode(completer.PopupCompletion)

        self.constraint_search.setCompleter(completer)

    def constraint_filter_update(self, value: str):
        regexp = QtCore.QRegExp(f".*{value.replace(' ', '.*')}.*", Qt.CaseInsensitive)
        self.constraint_proxy_model.setFilterRegExp(regexp)
        self.constraint_tree.expandAll()

    def constraint_search_keyup(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.constraint_search.setText("")
        elif event.key() == Qt.Key_Return:
            if self.constraint_proxy_model.rowCount() == 1:
                index = self.constraint_proxy_model.index(0, 0)
                self.constraint_tree.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)
            else:
                self.constraint_tree.selectionModel().clear()

    # ---------------------------------------------------------------------dd--
    #   Solution tree and model setup
    # ---------------------------------------------------------------------dd--
    def setup_solution_tree(self):
        solution_tree: QtWidgets.QTreeView = self.findChild(QtWidgets.QTreeView, "SolutionTree")

        solution_tree.expandAll()

        self.solution_tree = solution_tree

    # ---------------------------------------------------------------------dd--
    #   Constraint tree and model setup
    # ---------------------------------------------------------------------dd--
    def setup_constraint_tree(self):
        constraint_tree: QtWidgets.QTreeView = self.findChild(QtWidgets.QTreeView, "ConstraintsTree")

        model = ConstraintModel(constraints=Container.constraints)
        model.dataChanged.connect(lambda _: self.constraint_tree.expandAll())
        proxy_model = QtCore.QSortFilterProxyModel()
        proxy_model.setFilterKeyColumn(0)
        proxy_model.filterAcceptsRow = self.constraint_tree_accepts_row
        proxy_model.setSourceModel(model)

        constraint_tree.setModel(proxy_model)
        constraint_tree.expandAll()

        self.constraint_tree = constraint_tree
        self.constraint_model = model
        self.constraint_proxy_model = proxy_model

    def constraint_tree_accepts_row(self, row: int, parent: QModelIndex) -> bool:
        if not self.constraint_proxy_model:
            return True

        accepts = False
        regexp: QRegExp = self.constraint_proxy_model.filterRegExp()
        index = self.constraint_model.index(row, 0, parent)
        if index.parent().isValid():
            index = index.parent()

        data = self.constraint_model.data(index, Qt.DisplayRole)
        accepts = regexp.exactMatch(data)
        if not accepts:
            item = index.internalPointer()
            for child in item.children:
                data = child.get_column(0)
                accepts = regexp.exactMatch(data)
                if accepts:
                    break

        return accepts

    # ---------------------------------------------------------------------dd--
    #   Room table and model setup
    # ---------------------------------------------------------------------dd--
    def setup_room_table(self):
        room_table: QtWidgets.QTableView = self.findChild(QtWidgets.QTableView, "RoomTable")
        room_table.setSortingEnabled(True)

        model = RoomModel(rooms=Container.rooms)
        proxy_model = QtCore.QSortFilterProxyModel()
        proxy_model.setSourceModel(model)

        room_table.setModel(proxy_model)
        room_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        room_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.room_table = room_table
        self.room_model = model
        self.room_proxy_model = proxy_model

    # ---------------------------------------------------------------------dd--
    #   Participant table and model setup
    # ---------------------------------------------------------------------dd--
    def setup_participant_table(self):
        participant_table: QtWidgets.QTableView = self.findChild(QtWidgets.QTableView, "ParticipantTable")
        participant_table.setSortingEnabled(True)
        participant_table.setSelectionMode(QAbstractItemView.SingleSelection)

        model = ParticipantModel(participants=Container.participants)
        proxy_model = QtCore.QSortFilterProxyModel()
        proxy_model.setDynamicSortFilter(True)
        proxy_model.setSourceModel(model)

        participant_table.setModel(proxy_model)
        participant_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        participant_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.participant_table = participant_table
        self.participant_model = model
        self.participant_proxy_model = proxy_model

