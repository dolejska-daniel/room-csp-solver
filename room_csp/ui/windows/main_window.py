import json
import typing

from PyQt5.QtCore import pyqtSlot, QSortFilterProxyModel, QRegExp, Qt, pyqtSignal, QModelIndex, QAbstractItemModel
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QAction, QMenu, QLineEdit, QFileDialog, QHeaderView, QAbstractItemView, \
    QMessageBox, QStatusBar
from PyQt5.uic import loadUiType
from constraint import Problem, FunctionConstraint

from room_csp import *
from room_csp.ui.models import GenericTableModel, TreeSortFilterProxyModel
from room_csp.ui.models.generic_tree_model import GenericTreeModel
from .create_participant_dialog import CreateParticipantDialog
from .create_room_dialog import CreateRoomDialog
from ..views import GenericTreeView, GenericTableView, ExtendedItemView

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
    room_selection: typing.Union[QModelIndex, None] = None

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

            self.get_constraints_tree().expandAll()

    @pyqtSlot()
    def on_load_participants(self):
        pass

    @pyqtSlot()
    def on_save(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save file", filter="JSON File (*.json)")
        if filepath:
            with open(filepath, 'w') as fp:
                data = {
                    "rooms": self.room_model.get_dataset(),
                    "participants": self.participant_model.get_dataset(),
                    "constraints": self.constraint_model.get_dataset(),
                }
                json.dump(data, fp)

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

        self.participant_model.remove_item(self.participant_selection)

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
        if self.room_selection is None:
            return

        self.room_model.remove_item(self.room_selection)

    # ------------------------------------------------------dd--
    #   Category: Constraint
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_create_constraint(self):
        if self.participant_selection is None:
            return

        participant_name = self.participant_model.data(self.participant_selection, Qt.DisplayRole)
        data = {
            "name": participant_name,
            "enabled": True,
        }
        if self.constraint_selection is None:
            data["_items"] = []
            self.constraint_model.add_item(data)

        else:
            self.constraint_model.add_item(data, self.constraint_selection)

        self.get_constraints_tree().expandAll()

    @pyqtSlot()
    def on_delete_constraint(self):
        self.constraint_model.remove_item(self.constraint_selection)
        self.get_constraints_tree().expandAll()

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
        if solution_data is None:
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
            if participant_name == '_':
                continue

            room = room_slot.split("_")[0]
            if room not in solution:
                solution[room] = {
                    "name": room,
                    "_items": [],
                }

            solution[room]["_items"].append({
                "name": participant_name
            })

        solution_dataset = list(solution.values())
        self.solution_model.set_dataset(solution_dataset)

    # ------------------------------------------------------dd--
    #   Category: Solution
    # ------------------------------------------------------dd--

    @pyqtSlot(str)
    def on_status_change(self, message: str):
        self.findChild(QStatusBar, "statusbar").showMessage(message)

    # ==========================================================================dd==
    #   WIDGET GETTING FUNCTIONS
    # ==========================================================================dd==

    def get_participant_table(self) -> GenericTableView:
        return self.findChild(GenericTableView, "ParticipantTable")

    def get_room_table(self) -> GenericTableView:
        return self.findChild(GenericTableView, "RoomTable")

    def get_constraints_tree(self) -> GenericTreeView:
        return self.findChild(GenericTreeView, "ConstraintsTree")

    def get_solution_tree(self) -> GenericTreeView:
        return self.findChild(GenericTreeView, "SolutionTree")

    # ------------------------------------------------------dd--
    #   Helper widget manipulation functions
    # ------------------------------------------------------dd--

    def disable_action(self, identifier: str):
        self.findChild(QAction, identifier).setEnabled(False)

    def enable_action(self, identifier: str):
        self.findChild(QAction, identifier).setEnabled(True)

    # ==========================================================================dd==
    #   WIDGET MODEL SETUP
    # ==========================================================================dd==

    # ------------------------------------------------------dd--
    #   Generic utility functions
    # ------------------------------------------------------dd--

    def setup_item_view(self, view: ExtendedItemView, model: QAbstractItemModel, proxy: QAbstractItemModel = None,
                        on_data_change: pyqtSlot = None, on_selection_change: pyqtSlot = None,
                        on_mouse_release: pyqtSlot = None):
        # setup provided models accordingly
        self.setup_item_view_models(model, proxy, on_data_change)
        # set proxy as table source model
        view.setModel(model if proxy is None else proxy)

        # set single selection mode
        view.setSelectionMode(QAbstractItemView.SingleSelection)
        # connect selection signal
        if on_selection_change is not None:
            view.selectionModel().selectionChanged.connect(on_selection_change)
        # connect mouse signal
        if on_mouse_release is not None:
            view.mouseReleased.connect(on_mouse_release)

    def setup_item_view_models(self, model: QAbstractItemModel, proxy: QAbstractItemModel = None,
                               on_data_change: pyqtSlot = None):
        if on_data_change is not None:
            model.dataChanged.connect(on_data_change)
            model.layoutChanged.connect(on_data_change)
            self.resized.connect(on_data_change)

        if proxy is not None:
            proxy.setDynamicSortFilter(True)
            if model is not None:
                proxy.setSourceModel(model)

    # ------------------------------------------------------dd--
    #   Participant views
    # ------------------------------------------------------dd--

    def setup_participant_widgets(self):
        self.setup_participant_table()
        self.setup_participant_search()

    def setup_participant_table(self):
        # initialize source model
        self.participant_model = GenericTableModel(self)
        # initialize proxy model
        self.participant_proxy = QSortFilterProxyModel(self)

        table = self.get_participant_table()
        # setup general view properties
        self.setup_item_view(
            table, self.participant_model, self.participant_proxy,
            self.on_participant_model_changed, self.on_participant_selection_changed,
            self.on_participant_table_mouse_release
        )

    def setup_participant_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ParticipantSearch")
        field.textChanged.connect(self.on_participant_search)

    @pyqtSlot()
    def on_participant_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ParticipantSearch")

        search_string = field.text()
        search_string = search_string.replace(" ", ".*")
        search_string = ".*" + search_string + ".*"

        self.participant_proxy.setFilterRegExp(QRegExp(search_string, Qt.CaseInsensitive))

    @pyqtSlot()
    def on_participant_selection_changed(self):
        table = self.get_participant_table()
        indexes = table.selectionModel().selectedIndexes()
        if not len(indexes):
            self.disable_action("actionCreateConstraintFromSelection")
            self.disable_action("actionDeleteParticipant")
            self.participant_selection = None
            return

        self.enable_action("actionCreateConstraintFromSelection")
        self.enable_action("actionDeleteParticipant")
        self.participant_selection = self.participant_proxy.mapToSource(indexes[0])

    @pyqtSlot()
    def on_participant_model_changed(self):
        table = self.get_participant_table()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    @pyqtSlot(QMouseEvent)
    def on_participant_table_mouse_release(self, event: QMouseEvent):
        table = self.get_participant_table()
        if not table.indexAt(event.pos()).isValid():
            table.selectionModel().clearSelection()

    # ------------------------------------------------------dd--
    #   Constraint views
    # ------------------------------------------------------dd--

    def setup_constraint_widgets(self):
        self.setup_constraint_tree()
        self.setup_constraint_search()

    def setup_constraint_tree(self):
        # initialize source model
        self.constraint_model = GenericTreeModel(self)
        # initialize proxy model
        self.constraint_proxy = TreeSortFilterProxyModel(self)
        self.constraint_proxy.setRecursiveFilteringEnabled(True)

        tree = self.get_constraints_tree()
        # setup general view properties
        self.setup_item_view(
            tree, self.constraint_model, self.constraint_proxy,
            self.on_constraint_model_changed, self.on_constraint_selection_changed,
            self.on_constraint_tree_mouse_release
        )

    def setup_constraint_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ConstraintSearch")
        field.textChanged.connect(self.on_constraint_search)

    @pyqtSlot()
    def on_constraint_search(self):
        field: QLineEdit = self.findChild(QLineEdit, "ConstraintSearch")

        search_string = field.text()
        search_string = search_string.replace(" ", ".*")
        search_string = ".*" + search_string + ".*"

        self.constraint_proxy.setFilterRegExp(QRegExp(search_string, Qt.CaseInsensitive))
        self.get_constraints_tree().expandAll()

    @pyqtSlot()
    def on_constraint_selection_changed(self):
        tree = self.get_constraints_tree()
        indexes = tree.selectionModel().selectedIndexes()
        if not len(indexes):
            self.disable_action("actionDeleteConstraint")
            self.constraint_selection = None
            return

        self.enable_action("actionDeleteConstraint")
        self.constraint_selection = self.constraint_proxy.mapToSource(indexes[0])

    @pyqtSlot()
    def on_constraint_model_changed(self):
        tree = self.get_constraints_tree()
        tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        tree.expandAll()

    @pyqtSlot(QMouseEvent)
    def on_constraint_tree_mouse_release(self, event: QMouseEvent):
        tree = self.get_constraints_tree()
        if not tree.indexAt(event.pos()).isValid():
            tree.selectionModel().clearSelection()

    # ------------------------------------------------------dd--
    #   Room views
    # ------------------------------------------------------dd--

    def setup_room_widgets(self):
        # initialize source model
        self.room_model = GenericTableModel(self)
        # initialize proxy model
        self.room_proxy = QSortFilterProxyModel(self)

        table = self.get_room_table()
        # setup general view properties
        self.setup_item_view(
            table, self.room_model, self.room_proxy,
            self.on_room_model_changed, self.on_room_selection_changed,
            self.on_room_table_mouse_release
        )

    @pyqtSlot()
    def on_room_selection_changed(self):
        table = self.get_room_table()
        indexes = table.selectionModel().selectedIndexes()
        if not len(indexes):
            self.disable_action("actionDeleteRoom")
            self.room_selection = None
            return

        self.enable_action("actionDeleteRoom")
        self.room_selection = self.room_proxy.mapToSource(indexes[0])

    @pyqtSlot()
    def on_room_model_changed(self):
        table = self.get_room_table()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    @pyqtSlot(QMouseEvent)
    def on_room_table_mouse_release(self, event: QMouseEvent):
        table = self.get_room_table()
        if not table.indexAt(event.pos()).isValid():
            table.selectionModel().clearSelection()

    # ------------------------------------------------------dd--
    #   Solution views
    # ------------------------------------------------------dd--

    def setup_solution_widgets(self):
        # initialize source model
        self.solution_model = GenericTreeModel(self)

        tree = self.get_solution_tree()
        # setup general view properties
        self.setup_item_view(
            tree, self.solution_model, None,
            self.on_solution_model_changed, None,
            self.on_solution_tree_mouse_release
        )

    @pyqtSlot()
    def on_solution_model_changed(self):
        tree = self.get_solution_tree()
        tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        tree.expandAll()

    @pyqtSlot(QMouseEvent)
    def on_solution_tree_mouse_release(self, event: QMouseEvent):
        tree = self.get_solution_tree()
        if not tree.indexAt(event.pos()).isValid():
            tree.selectionModel().clearSelection()
