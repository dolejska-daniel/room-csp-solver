import json
import typing

from constraint import Problem, FunctionConstraint

from room_csp import *

from PyQt5.QtCore import pyqtSlot, QSortFilterProxyModel, QRegExp, Qt, pyqtSignal, QModelIndex
from PyQt5.QtWidgets import QAction, QMenu, QTableView, QLineEdit, QFileDialog, QHeaderView, QTreeView, \
    QAbstractItemView, QMessageBox
from PyQt5.uic import loadUiType

from room_csp.ui.models import GenericTableModel
from room_csp.ui.models.generic_tree_model import GenericTreeModel

from .create_room_dialog import CreateRoomDialog
from .create_participant_dialog import CreateParticipantDialog

qt_creator_file = "ui/main_window.ui"
Ui_MainWindow, QMainWindow = loadUiType(qt_creator_file)


class MainWindow(QMainWindow, Ui_MainWindow):
    """ Main program window. """
    resized = pyqtSignal()

    participant_model: GenericTableModel = None
    participant_proxy: QSortFilterProxyModel = None
    participant_selection: typing.Union[QModelIndex, None] = None

    constraint_model: GenericTreeModel = None
    constraint_proxy: QSortFilterProxyModel = None
    constraint_selection: typing.Union[QModelIndex, None] = None

    room_model: GenericTableModel = None
    room_proxy: QSortFilterProxyModel = None

    solution_model: GenericTreeModel = None

    # ==========================================================================dd==
    #   WINDOW INITIALIZATION
    # ==========================================================================dd==

    def __init__(self):
        """ Initializes window UI, connects required signals and sets up other required classes. """

        super().__init__()
        self.setupUi(self)

        # configure window details
        self.setWindowTitle("ESC Room CSP Solver")

        # initialize custom ui elements
        self.setup_menu_buttons()
        self.setup_widgets()

    def setup_menu_buttons(self):
        """ Connects menu action signals to corresponding slot functions. """

        # category: file
        self.findChild(QAction, "actionLoad").triggered.connect(self.on_load)
        self.findChild(QAction, "actionLoadParticipants").triggered.connect(self.on_load_participants)
        self.findChild(QAction, "actionSave").triggered.connect(self.on_save)
        self.findChild(QAction, "actionSaveSolution").triggered.connect(self.on_save_solution)
        self.findChild(QAction, "actionExit").triggered.connect(self.on_exit)

        # category: focus
        self.findChild(QMenu, "menuFocus").setTitle("")
        self.findChild(QAction, "actionFocusParticipantSearch").triggered.connect(self.on_focus_participant_search)
        self.findChild(QAction, "actionFocusConstraintSearch").triggered.connect(self.on_focus_constraint_search)

        # category: participant
        self.findChild(QAction, "actionCreateParticipant").triggered.connect(self.on_create_participant)
        self.findChild(QAction, "actionDeleteParticipant").triggered.connect(self.on_delete_participant)

        # category: room
        self.findChild(QAction, "actionCreateRoom").triggered.connect(self.on_create_room)
        self.findChild(QAction, "actionDeleteRoom").triggered.connect(self.on_delete_room)

        # category: constraint
        self.findChild(QAction, "actionCreateConstraintFromSelection").triggered.connect(self.on_create_constraint)
        self.findChild(QAction, "actionDeleteConstraint").triggered.connect(self.on_delete_constraint)

        # category: solution
        self.findChild(QAction, "actionSolve").triggered.connect(self.on_solve)

        # category: options
        pass

    def setup_widgets(self):
        self.setup_participant_widgets()
        self.setup_constraint_widgets()
        self.setup_room_widgets()
        self.setup_solution_widgets()

    def resizeEvent(self, _):
        self.resized.emit()

    # ==========================================================================dd==
    #   MENU SLOT FUNCTIONS
    # ==========================================================================dd==

    # ------------------------------------------------------dd--
    #   Category: File
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_load(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open file", filter="JSON File (*.json)")
        if filepath:
            with open(filepath, 'r') as fp:
                data = json.load(fp)
                self.participant_model.set_dataset(data["participants"])
                self.room_model.set_dataset(data["rooms"])
                self.constraint_model.set_dataset(data["constraints"])

    @pyqtSlot()
    def on_load_participants(self):
        pass

    @pyqtSlot()
    def on_save(self):
        pass

    @pyqtSlot()
    def on_save_solution(self):
        pass

    @pyqtSlot()
    def on_exit(self):
        self.close()

    # ------------------------------------------------------dd--
    #   Category: Focus
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_focus_participant_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ParticipantSearch")
        field.setFocus()

    @pyqtSlot()
    def on_focus_constraint_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ConstraintSearch")
        field.setFocus()

    # ------------------------------------------------------dd--
    #   Category: Participant
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_create_participant(self):
        dialog = CreateParticipantDialog(self)
        dialog.participant_data_sent.connect(self.on_create_participant_data)
        dialog.exec_()

    @pyqtSlot(dict)
    def on_create_participant_data(self, data: dict):
        self.participant_model.add_item(data)

    @pyqtSlot()
    def on_delete_participant(self):
        if self.participant_selection is None:
            return

    # ------------------------------------------------------dd--
    #   Category: Room
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_create_room(self):
        dialog = CreateRoomDialog(self)
        dialog.room_data_sent.connect(self.on_create_room_data)
        dialog.exec_()

    @pyqtSlot(dict)
    def on_create_room_data(self, data: dict):
        self.room_model.add_item(data)

    @pyqtSlot()
    def on_delete_room(self):
        pass

    # ------------------------------------------------------dd--
    #   Category: Constraint
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_create_constraint(self):
        pass

    @pyqtSlot()
    def on_delete_constraint(self):
        pass

    # ------------------------------------------------------dd--
    #   Category: Solution
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_solve(self):
        Container.set_rooms(self.room_model.get_dataset())
        Container.set_participants(self.participant_model.get_dataset())
        Container.set_constraints(self.constraint_model.get_dataset())

        if not len(Container.rooms) or not len(Container.participants):
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Warning)
            message.setWindowTitle("Required data missing!")
            message.setText("No rooms or participants were defined!\nPlease add rooms and/or participants to continue.")
            message.setStandardButtons(QMessageBox.Ok)
            message.exec_()
            return

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
        solution = {}
        solution_data = p.getSolution()
        if not len(solution_data):
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Critical)
            message.setWindowTitle("No solution found!")
            message.setText(
                "Current problem definition does not have any solutions!\n"
                "Consider disabling constraints and check that there is enough room for all the participants."
            )
            message.setStandardButtons(QMessageBox.Ok)
            message.exec_()
            return

        for room_slot, participant_name in solution_data.items():
            room = room_slot.split("_")[0]
            if room not in solution:
                solution[room] = {
                    "name": room,
                    "_items": [],
                }

            solution[room]["_items"].append({
                "name": participant_name
            })

        print(solution_data)
        self.solution_model.set_dataset(list(solution.values()))

    # ==========================================================================dd==
    #   WIDGET MODEL SETUP
    # ==========================================================================dd==

    # ------------------------------------------------------dd--
    #   Generic utility functions
    # ------------------------------------------------------dd--

    def setup_table_models(self, model: GenericTableModel, proxy: typing.Union[QSortFilterProxyModel, None],
                           on_change_slot: pyqtSlot):
        model.dataChanged.connect(on_change_slot)
        model.layoutChanged.connect(on_change_slot)
        self.resized.connect(on_change_slot)

        if proxy is not None:
            proxy.setSourceModel(model)
            proxy.setDynamicSortFilter(True)

    def setup_tree_models(self, model: GenericTreeModel, proxy: typing.Union[QSortFilterProxyModel, None],
                          on_change_slot: pyqtSlot):
        model.dataChanged.connect(on_change_slot)
        model.layoutChanged.connect(on_change_slot)
        self.resized.connect(on_change_slot)

        if proxy is not None:
            proxy.setSourceModel(model)
            proxy.setDynamicSortFilter(True)

    # ------------------------------------------------------dd--
    #   Participant widgets
    # ------------------------------------------------------dd--

    def setup_participant_widgets(self):
        self.setup_participant_table()
        self.setup_participant_search()

    def setup_participant_table(self):
        # initialize source model
        self.participant_model = GenericTableModel(self)
        # initialize proxy model
        self.participant_proxy = QSortFilterProxyModel(self)
        # setup these models accordingly
        self.setup_table_models(self.participant_model, self.participant_proxy, self.on_participant_model_changed)

        table: QTableView = self.findChild(QTableView, "ParticipantTable")
        # set proxy as table source model
        table.setModel(self.participant_proxy)
        # set single selection mode
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        # connect selection signal
        table.selectionModel().selectionChanged.connect(self.on_participant_selection_changed)

    def setup_participant_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ParticipantSearch")
        field.textChanged.connect(self.on_participant_search)

    @pyqtSlot()
    def on_participant_selection_changed(self):
        table: QTableView = self.findChild(QTableView, "ParticipantTable")
        action: QAction = self.findChild(QAction, "actionCreateConstraintFromSelection")
        indexes = table.selectionModel().selectedIndexes()
        if not len(indexes):
            action.setEnabled(False)
            self.participant_selection = None
            return

        action.setEnabled(True)
        self.participant_selection = self.participant_proxy.mapToSource(indexes[0])

    @pyqtSlot()
    def on_participant_model_changed(self):
        table: QTableView = self.findChild(QTableView, "ParticipantTable")
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    @pyqtSlot()
    def on_participant_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ParticipantSearch")

        search_string = field.text()
        search_string = search_string.replace(" ", ".*")
        search_string = ".*" + search_string + ".*"

        self.participant_proxy.setFilterRegExp(QRegExp(search_string, Qt.CaseInsensitive))

    # ------------------------------------------------------dd--
    #   Constraint widgets
    # ------------------------------------------------------dd--

    def setup_constraint_widgets(self):
        # initialize source model
        self.constraint_model = GenericTreeModel(self)
        # initialize proxy model
        self.constraint_proxy = QSortFilterProxyModel(self)
        # setup these models accordingly
        self.setup_tree_models(self.constraint_model, self.constraint_proxy, self.on_constraint_model_changed)

        tree: QTreeView = self.findChild(QTreeView, "ConstraintsTree")
        # set proxy as table source model
        tree.setModel(self.constraint_model)
        # set single selection mode
        tree.setSelectionMode(QAbstractItemView.SingleSelection)
        # connect selection signal
        tree.selectionModel().selectionChanged.connect(self.on_constraint_selection_changed)

    @pyqtSlot()
    def on_constraint_selection_changed(self):
        tree: QTreeView = self.findChild(QTreeView, "ConstraintsTree")
        indexes = tree.selectionModel().selectedIndexes()
        if not len(indexes):
            self.constraint_selection = None
            return

        self.constraint_selection = self.constraint_proxy.mapToSource(indexes[0])

    @pyqtSlot()
    def on_constraint_model_changed(self):
        tree: QTreeView = self.findChild(QTreeView, "ConstraintsTree")
        # TODO: Resize tree columns to fit contents

        tree.expandAll()

    # ------------------------------------------------------dd--
    #   Room widgets
    # ------------------------------------------------------dd--

    def setup_room_widgets(self):
        # initialize source model
        self.room_model = GenericTableModel(self)
        # initialize proxy model
        self.room_proxy = QSortFilterProxyModel(self)
        # setup these models accordingly
        self.setup_table_models(self.room_model, self.room_proxy, self.on_room_model_changed)

        table: QTableView = self.findChild(QTableView, "RoomTable")
        # set proxy as table source model
        table.setModel(self.room_proxy)

    @pyqtSlot()
    def on_room_model_changed(self):
        table: QTableView = self.findChild(QTableView, "RoomTable")
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    # ------------------------------------------------------dd--
    #   Solution widgets
    # ------------------------------------------------------dd--

    def setup_solution_widgets(self):
        # initialize source model
        self.solution_model = GenericTreeModel(self)
        # setup these models accordingly
        self.setup_tree_models(self.solution_model, None, self.on_solution_model_changed)

        tree: QTreeView = self.findChild(QTreeView, "SolutionTree")
        tree.setModel(self.solution_model)

    @pyqtSlot()
    def on_solution_model_changed(self):
        tree: QTreeView = self.findChild(QTreeView, "SolutionTree")
        # TODO: Resize tree columns to fit contents

        tree.expandAll()
