import json

from constraint import *
from room_csp import *

# =========================================================================dd==
#   PROGRAM INITIALIZATION, DATA LOADING
# =========================================================================dd==

with open("input.json", "r") as fd:
    data = json.load(fd)

rooms = []
participants = []
constraints = []
try:
    rooms = data["rooms"]
    participants = data["participants"]
    constraints = data["constraints"]
except KeyError:
    print("Invalid input JSON.")
    exit(1)

room_slots = []
for room in rooms:
    for slot in range(0, room["beds"]):
        room_slots.append(f"{room['name']}_{slot}")

Container.rooms = {r["name"]: r for r in rooms}
Container.room_slots = room_slots
Container.set_participants({p["name"]: p for p in participants})
Container.constraints = constraints

# =========================================================================dd==
#   PROBLEM DEFINITION
# =========================================================================dd==

# p = Problem(solver=RecursiveBacktrackingSolver())
p = Problem()

# variables are room slots
# doman is participant list (with '_' as noone)
p.addVariables(room_slots, [p["name"] for p in participants] + ["_"])


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
