from constraint import Problem, BacktrackingSolver

from room_csp.logic.constraints import *
from .container import Container


class RoomAssignmentProblem(Problem):

    def __init__(self, solver=BacktrackingSolver()):
        super().__init__(solver)

        # variables are room slots, doman is participant list (with '_' as noone)
        self.addVariables(Container.room_slots, ["_"] + list(Container.participants.keys()))

        # all participants have room
        self.addConstraint(RespectRoomType())
        # only one gender per room (either boys or girls)
        self.addConstraint(SameRoomSameGenders())
        # all participants are assigned to single room slot
        self.addConstraint(UniquelyAssignedParticipants())
        # participants' are in rooms with their mates
        self.addConstraint(CustomParticipantRequirements())
        # all participants have room
        self.addConstraint(AllParticipantsAssigned())

        # TODO: Add constraint on Room.Type x Participant.Type
