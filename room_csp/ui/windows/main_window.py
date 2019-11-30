from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from room_csp import Container
from room_csp.ui.models.constraint_model import ConstraintModel
from room_csp.ui.models.participant_model import ParticipantModel
from room_csp.ui.models.room_model import RoomModel

qt_creator_file = "ui/main_window.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    # -------------------------------------------------dd--
    #   participant_search variables
    # -------------------------------------------------dd--
    participant_search: QtWidgets.QLineEdit = None
    participant_search_completer: QtWidgets.QCompleter = None

    # -------------------------------------------------dd--
    #   solution_tree variables
    # -------------------------------------------------dd--
    solution_tree: QtWidgets.QTreeView = None

    # -------------------------------------------------dd--
    #   constraint_tree variables
    # -------------------------------------------------dd--
    constraint_tree: QtWidgets.QTreeView = None

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

        self.setup_participant_table()
        self.setup_room_table()
        self.setup_constraint_tree()
        self.setup_solution_tree()

        self.setup_participant_search()

    # ---------------------------------------------------------------------dd--
    #   Participant search field and proxy model setup
    # ---------------------------------------------------------------------dd--
    def setup_participant_search(self):
        participant_search: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, "ParticipantSearch")
        participant_search.textChanged.connect(self.participant_filter_update)

        self.participant_search = participant_search

        strings = list(self.participant_model.participants.keys())
        self.setup_participant_search_completer(strings)

    def setup_participant_search_completer(self, strings: [str]):
        completer = QtWidgets.QCompleter(strings)
        completer.setCompletionMode(completer.PopupCompletion)

        self.participant_search.setCompleter(completer)

    def participant_filter_update(self, value: str):
        regexp = QtCore.QRegExp(f".*{value.replace(' ', '.*')}.*", Qt.CaseInsensitive)
        self.participant_proxy_model.setFilterRegExp(regexp)

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
        constraint_tree: QtWidgets.QTreeView = self.findChild(QtWidgets.QTreeView, "ParticipantConstraintsTree")

        model = ConstraintModel(constraints=Container.constraints)
        model.dataChanged.connect(lambda _: self.constraint_tree.expandAll())

        constraint_tree.setModel(model)
        constraint_tree.expandAll()

        self.constraint_tree = constraint_tree

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

        self.room_table = room_table
        self.room_model = model
        self.room_proxy_model = proxy_model

    # ---------------------------------------------------------------------dd--
    #   Participant table and model setup
    # ---------------------------------------------------------------------dd--
    def setup_participant_table(self):
        participant_table: QtWidgets.QTableView = self.findChild(QtWidgets.QTableView, "ParticipantTable")
        participant_table.setSortingEnabled(True)

        model = ParticipantModel(participants=Container.participants)
        proxy_model = QtCore.QSortFilterProxyModel()
        proxy_model.setSourceModel(model)

        participant_table.setModel(proxy_model)
        participant_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.participant_table = participant_table
        self.participant_model = model
        self.participant_proxy_model = proxy_model

