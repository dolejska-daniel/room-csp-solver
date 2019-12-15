import json

from constraint import Problem, FunctionConstraint

from room_csp import *

from PyQt5.QtCore import pyqtSlot, QSortFilterProxyModel, QRegExp, Qt
from PyQt5.QtWidgets import QAction, QMenu, QTableView, QLineEdit, QFileDialog
from PyQt5.uic import loadUiType

from room_csp.ui.models import GenericTableModel

qt_creator_file = "ui/main_window.ui"
Ui_MainWindow, QMainWindow = loadUiType(qt_creator_file)


class MainWindow(QMainWindow, Ui_MainWindow):
    """ Main program window. """

    participant_model: GenericTableModel = None
    participant_proxy: QSortFilterProxyModel = None

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
        self.findChild(QAction, "actionLoad").triggered.connect(self.on_load_all)
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

    # ==========================================================================dd==
    #   MENU SLOT FUNCTIONS
    # ==========================================================================dd==

    # ------------------------------------------------------dd--
    #   Category: File
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_load_all(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open file", filter="JSON File (*.json)")
        if filepath:
            with open(filepath, 'r') as fp:
                data = json.load(fp)
                self.participant_model.set_dataset(data["participants"])

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
        self.close()

    # ------------------------------------------------------dd--
    #   Category: Participant
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_create_participant(self):
        pass

    @pyqtSlot()
    def on_delete_participant(self):
        pass

    # ------------------------------------------------------dd--
    #   Category: Room
    # ------------------------------------------------------dd--

    @pyqtSlot()
    def on_create_room(self):
        pass

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
        # TODO: Get data from models to Container

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
        print(solution_data)

    # ==========================================================================dd==
    #   WIDGET MODEL SETUP
    # ==========================================================================dd==

    # ------------------------------------------------------dd--
    #   Participant widgets
    # ------------------------------------------------------dd--

    def setup_participant_widgets(self):
        self.setup_participant_table()
        self.setup_participant_search()

    def setup_participant_table(self):
        table: QTableView = self.findChild(QTableView, "ParticipantTable")

        # initialize source model
        self.participant_model = GenericTableModel(self)
        # initialize proxy model
        self.participant_proxy = QSortFilterProxyModel(self)
        self.participant_proxy.setSourceModel(self.participant_model)
        self.participant_proxy.setDynamicSortFilter(True)

        # set proxy as table source model
        table.setModel(self.participant_proxy)

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

    # ------------------------------------------------------dd--
    #   Constraint widgets
    # ------------------------------------------------------dd--

    def setup_constraint_widgets(self):
        pass

    # ------------------------------------------------------dd--
    #   Room widgets
    # ------------------------------------------------------dd--

    def setup_room_widgets(self):
        pass

    # ------------------------------------------------------dd--
    #   Solution widgets
    # ------------------------------------------------------dd--

    def setup_solution_widgets(self):
        pass
