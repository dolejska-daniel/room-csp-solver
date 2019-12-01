from constraint import *

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QItemSelection, QModelIndex, QItemSelectionModel, QRegExp
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView

from room_csp import *
from room_csp.ui.models.constraint_model import ConstraintModel, ConstraintItem
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

    # -------------------------------------------------dd--
    #   actions variables
    # -------------------------------------------------dd--
    action_create_constraint: QtWidgets.QAction = None
    action_delete_constraint: QtWidgets.QAction = None

    action_delete_participant: QtWidgets.QAction = None

    action_delete_room: QtWidgets.QAction = None

    # -------------------------------------------------dd--
    #   current selection variables
    # -------------------------------------------------dd--
    selected_constraint: ConstraintItem = None
    selected_participant: str = None
    selected_room: str = None

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
        self.findChild(QtWidgets.QAction, "actionLoad").triggered.connect(self.load)
        self.findChild(QtWidgets.QAction, "actionLoadRooms").setEnabled(False)
        self.findChild(QtWidgets.QAction, "actionLoadParticipants").setEnabled(False)
        self.findChild(QtWidgets.QAction, "actionLoadConstraints").setEnabled(False)
        self.findChild(QtWidgets.QAction, "actionSave").triggered.connect(self.save)
        self.findChild(QtWidgets.QAction, "actionSaveSolution").triggered.connect(self.save_solution)
        self.findChild(QtWidgets.QAction, "actionExit").triggered.connect(lambda _: exit(0))

        self.findChild(QtWidgets.QMenu, "menuFocus").setTitle("")
        self.findChild(QtWidgets.QAction, "actionFocusParticipantSearch") \
            .triggered.connect(lambda _: self.participant_search.setFocus())
        self.findChild(QtWidgets.QAction, "actionFocusConstraintSearch") \
            .triggered.connect(lambda _: self.constraint_search.setFocus())

        self.findChild(QtWidgets.QAction, "actionCreateParticipant").triggered.connect(self.create_participant)
        self.action_delete_participant = self.findChild(QtWidgets.QAction, "actionDeleteParticipant")
        self.action_delete_participant.triggered.connect(self.delete_participant)
        self.action_delete_participant.setEnabled(False)

        self.action_create_constraint = self.findChild(QtWidgets.QAction, "actionCreateConstraintFromSelection")
        self.action_create_constraint.triggered.connect(self.create_constraint_from_selection)
        self.action_create_constraint.setEnabled(False)

        self.action_delete_constraint = self.findChild(QtWidgets.QAction, "actionDeleteConstraint")
        self.action_delete_constraint.triggered.connect(self.delete_constraint)
        self.action_delete_constraint.setEnabled(False)

        self.findChild(QtWidgets.QAction, "actionCreateRoom").triggered.connect(self.create_room)
        self.action_delete_room = self.findChild(QtWidgets.QAction, "actionDeleteRoom")
        self.action_delete_room.triggered.connect(self.delete_room)
        self.action_delete_room.setEnabled(False)

        self.findChild(QtWidgets.QAction, "actionSolve").triggered.connect(self.solve)

        self.findChild(QtWidgets.QAction, "actionAbout").triggered.connect(self.about)

    def about(self):
        pass

    def solve(self):
        # ---------------------------------------------dd--
        #   PROBLEM AND CONSTRAINT DEFINITION
        # ---------------------------------------------dd--
        # p = Problem(solver=RecursiveBacktrackingSolver())
        p = Problem()
        # variables are room slots, doman is participant list (with '_' as noone)
        p.addVariables(Container.room_slots, list(Container.participants.keys()) + ["_"])

        # all participants are assigned to single room slot
        p.addConstraint(UniquelyAssignedParticipants())
        # only one gender per room (either boys or girls)
        p.addConstraint(SameRoomSameGenders())
        # all participants have room
        p.addConstraint(FunctionConstraint(all_participants_assigned))
        # participants' are in rooms with their mates
        p.addConstraint(FunctionConstraint(custom_participant_requirements))

        # ---------------------------------------------dd--
        #   PROBLEM SOLUTION
        # ---------------------------------------------dd--
        print(p.getSolution())

    def delete_room(self):
        if self.selected_room is None:
            return

    def create_room(self):
        dialog = CreateRoomDialog(self.room_model, parent=self)
        dialog.exec_()

    def delete_constraint(self):
        if self.selected_constraint is None:
            return

    def create_constraint_from_selection(self):
        if self.selected_participant is None:
            return

        self.constraint_model.add_entry(
            self.selected_participant,
            self.selected_constraint.get_column(0) if self.selected_constraint is not None else None
        )

    def delete_participant(self):
        if self.selected_participant is None:
            return

    def create_participant(self):
        dialog = CreateParticipantDialog(self.participant_model, parent=self)
        dialog.exec_()

    def save_solution(self):
        pass

    def save(self):
        pass

    def load(self):
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
            self.participant_table.selectionModel().clear()
            self.action_create_constraint.setEnabled(False)
        elif event.key() == Qt.Key_Return:
            if self.participant_proxy_model.rowCount() == 1:
                index = self.participant_proxy_model.index(0, 0)
                self.participant_table.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)
                self.action_create_constraint.setEnabled(True)
            else:
                self.participant_table.selectionModel().clear()
                self.action_create_constraint.setEnabled(False)

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
            self.constraint_tree.selectionModel().clear()
        elif event.key() == Qt.Key_Return:
            # clear current selection
            self.constraint_tree.selectionModel().clear()

            for row in range(0, self.constraint_proxy_model.rowCount()):
                # create corresponding proxy index
                index = self.constraint_proxy_model.index(row, 0)
                # map selection from proxy model to source model
                source_index = self.constraint_proxy_model.mapToSource(index)

                # get selected item instance
                constraint_item = source_index.internalPointer()
                # get filter regular expression
                regexp: QRegExp = self.constraint_proxy_model.filterRegExp()
                # check whether current item matches the expression
                match = regexp.exactMatch(constraint_item.get_column(0))
                # if not
                if not match:
                    # then check all children for matches
                    for child in constraint_item.children:
                        # get child data
                        data = child.get_column(0)
                        # evaluate match
                        match = regexp.exactMatch(data)
                        # if child matches
                        if match:
                            # then get its row
                            child_row = child.get_row()
                            # build corresponding source index
                            child_source_index = self.constraint_model.index(child_row, 0, source_index)
                            # map source index to proxy index
                            index = self.constraint_proxy_model.mapFromSource(child_source_index)
                            # match has been found
                            break
                else:
                    # match has been found
                    break

            # if any match has been found
            if match:
                # use proxy index to create new selection
                self.constraint_tree.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)

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
        proxy_model.setDynamicSortFilter(True)
        proxy_model.setFilterKeyColumn(0)
        proxy_model.filterAcceptsRow = self.constraint_tree_accepts_row
        proxy_model.setSourceModel(model)

        constraint_tree.setModel(proxy_model)
        constraint_tree.selectionModel().selectionChanged.connect(self.constraint_tree_selection_changed)
        constraint_tree.expandAll()

        self.constraint_tree = constraint_tree
        self.constraint_model = model
        self.constraint_proxy_model = proxy_model

    def constraint_tree_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if len(selected.indexes()) > 0:
            proxy_index = selected.indexes()[0]
            source_index = self.constraint_proxy_model.mapToSource(proxy_index)
            self.selected_constraint = source_index.internalPointer()
        else:
            self.selected_constraint = None

        self.action_delete_constraint.setEnabled(self.selected_constraint is not None)

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
        room_table.selectionModel().selectionChanged.connect(self.room_table_selection_changed)
        room_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        room_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.room_table = room_table
        self.room_model = model
        self.room_proxy_model = proxy_model

    def room_table_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if len(selected.indexes()) > 0:
            proxy_index = selected.indexes()[0]
            self.selected_room = proxy_index.data()
        else:
            self.selected_room = None

        self.action_delete_room.setEnabled(self.selected_room is not None)

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
        participant_table.selectionModel().selectionChanged.connect(self.participant_table_selection_changed)
        participant_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        participant_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.participant_table = participant_table
        self.participant_model = model
        self.participant_proxy_model = proxy_model

    def participant_table_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if len(selected.indexes()) > 0:
            proxy_index = selected.indexes()[0]
            self.selected_participant = proxy_index.data()
        else:
            self.selected_participant = None

        self.action_delete_participant.setEnabled(self.selected_participant is not None)
        self.action_create_constraint.setEnabled(self.selected_participant is not None)

