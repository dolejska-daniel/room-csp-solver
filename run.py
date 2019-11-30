import json

from constraint import *
from room_csp import *
from room_csp.ui import setup_and_run_ui

# =========================================================================dd==
#   PROGRAM INITIALIZATION, DATA LOADING
# =========================================================================dd==

with open("input.json", "r") as fd:
    data = json.load(fd)

Container.initialize(data)

setup_and_run_ui()

# =========================================================================dd==
#   PROBLEM DEFINITION
# =========================================================================dd==

# p = Problem(solver=RecursiveBacktrackingSolver())
p = Problem()

# variables are room slots
# doman is participant list (with '_' as noone)
p.addVariables(Container.room_slots, list(Container.participants.keys()) + ["_"])


# all participants are assigned to single room slot
p.addConstraint(UniquelyAssignedParticipants())

# only one gender per room (either boys or girls)
p.addConstraint(SameRoomSameGenders())


# all participants have room
p.addConstraint(FunctionConstraint(all_participants_assigned))

# participants' are in rooms with their mates
p.addConstraint(FunctionConstraint(custom_participant_requirements))

# =========================================================================dd==
#   PROBLEM SOLUTION
# =========================================================================dd==

print(p.getSolution())
