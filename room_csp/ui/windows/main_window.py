from constraint import *

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QItemSelection, QModelIndex, QItemSelectionModel, QRegExp
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView

from room_csp import *
from room_csp.ui.models import *
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
    solution_model: SolutionModel = None

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
        self.findChild(QtWidgets.QAction, "actionLoadParticipants").triggered.connect(self.load_participants)
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
        #   VARIABLES UPDATE
        # ---------------------------------------------dd--
        Container.set_rooms(self.room_model.get_data_for_solver())
        Container.set_participants(self.participant_model.get_data_for_solver())
        Container.constraints = self.constraint_model.get_data_for_solver()

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
        p.addConstraint(AllParticipantsAssigned())
        # participants' are in rooms with their mates
        p.addConstraint(FunctionConstraint(custom_participant_requirements))

        # ---------------------------------------------dd--
        #   PROBLEM SOLUTION
        # ---------------------------------------------dd--
        solution_data = p.getSolution()
        if solution_data is None:
            message = QMessageBox(
                QMessageBox.Critical, "No solution found",
                "Program could not find any solution for specified constraints."
            )
            message.exec_()

        else:
            for room_slot, participant in list(solution_data.items()):
                if participant == '_':
                    del solution_data[room_slot]

            self.solution_model.reload_data(solution_data)

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
        import json

        contents = {
            "rooms": list(Container.rooms.values()),
            "participants": list(Container.participants.values()),
            "constraints": Container.constraints,
        }

        filepath, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, "Save contents", filter="JSON file (*.json)")
        if filepath != "":
            with open(filepath, "w") as fp:
                json.dump(contents, fp, ensure_ascii=False)

    def load(self):
        import json

        filepath, file_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Load contents", filter="JSON file (*.json)")
        if filepath != "":
            with open(filepath, "r") as fp:
                data = json.load(fp)

            Container.initialize(data)
            self.constraint_model.reload_data(Container.constraints)
            self.participant_model.reload_data(Container.participants)
            self.room_model.reload_data(Container.rooms)

    def load_participants(self):
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
        self.participant_filter_update("")

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
        self.constraint_filter_update("")

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

            match = False
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

        model = SolutionModel()

        def expand_all():
            self.solution_tree.expandAll()

        model.dataChanged.connect(expand_all)
        model.layoutChanged.connect(expand_all)

        solution_tree.setModel(model)
        solution_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        solution_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        solution_tree.expandAll()

        self.solution_tree = solution_tree
        self.solution_model = model

    # ---------------------------------------------------------------------dd--
    #   Constraint tree and model setup
    # ---------------------------------------------------------------------dd--
    def setup_constraint_tree(self):
        constraint_tree: QtWidgets.QTreeView = self.findChild(QtWidgets.QTreeView, "ConstraintsTree")
        constraint_tree.doubleClicked.connect(self.constraint_tree_item_toggle)

        model = ConstraintModel(constraints=Container.constraints)
        proxy_model = ConstraintProxyModel(source_model=model)

        def expand_all():
            self.constraint_tree.expandAll()

        proxy_model.dataChanged.connect(expand_all)
        proxy_model.layoutChanged.connect(expand_all)

        constraint_tree.setModel(proxy_model)
        constraint_tree.selectionModel().selectionChanged.connect(self.constraint_tree_selection_changed)
        model.dataChanged.connect(self.constraint_tree_resize)
        model.layoutChanged.connect(self.constraint_tree_resize)
        constraint_tree.expandAll()

        self.constraint_tree = constraint_tree
        self.constraint_model = model
        self.constraint_proxy_model = proxy_model

        self.constraint_tree_resize()

    def constraint_tree_resize(self):
        for column in range(self.room_model.columnCount(QModelIndex())):
            resize_mode = QtWidgets.QHeaderView.Stretch if column == 0 else QtWidgets.QHeaderView.ResizeToContents
            self.constraint_tree.header().setSectionResizeMode(column, resize_mode)

    def constraint_tree_item_toggle(self, index: QModelIndex):
        source_index = self.constraint_proxy_model.mapToSource(index)
        self.constraint_model.toggle_entry(source_index)

    def constraint_tree_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if len(selected.indexes()) > 0:
            proxy_index = selected.indexes()[0]
            source_index = self.constraint_proxy_model.mapToSource(proxy_index)
            self.selected_constraint = source_index.internalPointer()
        else:
            self.selected_constraint = None

        self.action_delete_constraint.setEnabled(self.selected_constraint is not None)

    # ---------------------------------------------------------------------dd--
    #   Room table and model setup
    # ---------------------------------------------------------------------dd--
    def setup_room_table(self):
        room_table: QtWidgets.QTableView = self.findChild(QtWidgets.QTableView, "RoomTable")
        room_table.setSortingEnabled(True)

        model = RoomModel(rooms=Container.rooms)
        proxy_model = RoomProxyModel(source_model=model)

        room_table.setModel(proxy_model)
        room_table.selectionModel().selectionChanged.connect(self.room_table_selection_changed)
        model.dataChanged.connect(self.room_table_resize)
        model.layoutChanged.connect(self.room_table_resize)

        self.room_table = room_table
        self.room_model = model
        self.room_proxy_model = proxy_model

        self.room_table_resize()

    def room_table_resize(self):
        for column in range(self.room_model.columnCount(QModelIndex())):
            resize_mode = QtWidgets.QHeaderView.Stretch if column == 0 else QtWidgets.QHeaderView.ResizeToContents
            self.room_table.horizontalHeader().setSectionResizeMode(column, resize_mode)
        self.room_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

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
        proxy_model = ParticipantProxyModel(source_model=model)

        participant_table.setModel(proxy_model)
        participant_table.selectionModel().selectionChanged.connect(self.participant_table_selection_changed)
        model.dataChanged.connect(self.participant_table_resize)
        model.layoutChanged.connect(self.participant_table_resize)

        self.participant_table = participant_table
        self.participant_model = model
        self.participant_proxy_model = proxy_model

        self.participant_table_resize()

    def participant_table_resize(self):
        for column in range(self.participant_model.columnCount(QModelIndex())):
            resize_mode = QtWidgets.QHeaderView.Stretch if column == 0 else QtWidgets.QHeaderView.ResizeToContents
            self.participant_table.horizontalHeader().setSectionResizeMode(column, resize_mode)
        self.participant_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def participant_table_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if len(selected.indexes()) > 0:
            proxy_index = selected.indexes()[0]
            self.selected_participant = proxy_index.data()
        else:
            self.selected_participant = None

        self.action_delete_participant.setEnabled(self.selected_participant is not None)
        self.action_create_constraint.setEnabled(self.selected_participant is not None)
