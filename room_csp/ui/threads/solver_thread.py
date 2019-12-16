from PyQt5.QtCore import QThread, pyqtSignal
from constraint import Problem, FunctionConstraint, MinConflictsSolver

from room_csp.logic import *


class SolverThread(QThread):
    status_changed = pyqtSignal(str)
    solution_found = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    def __del__(self):
        self.wait()

    def run(self) -> None:
        p = Problem(solver=MinConflictsSolver())
        # variables are room slots, doman is participant list (with '_' as noone)
        p.addVariables(Container.room_slots, list(Container.participants.keys()) + ["_"])

        # all participants are assigned to single room slot
        p.addConstraint(UniquelyAssignedParticipants())
        # only one gender per room (either boys or girls)
        p.addConstraint(SameRoomSameGenders())
        # participants' are in rooms with their mates
        p.addConstraint(FunctionConstraint(custom_participant_requirements))
        # all participants have room
        p.addConstraint(AllParticipantsAssigned())

        self.solution_found.emit(p.getSolution())
