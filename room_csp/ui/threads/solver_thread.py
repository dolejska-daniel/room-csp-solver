from PyQt5.QtCore import QThread, pyqtSignal
from constraint import Problem, FunctionConstraint

from room_csp import *


class SolverThread(QThread):
    status_changed = pyqtSignal(str)
    solution_found = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    def __del__(self):
        self.wait()

    def run(self) -> None:
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

        self.solution_found.emit(p.getSolution())
