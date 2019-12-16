from constraint import Constraint, Unassigned

from room_csp.logic import Container


class CustomParticipantRequirements(Constraint):
    """ Ensures that all participant's requirements are met. """

    def __call__(
        self,
        room_slots,
        participant_domains,
        assignments,
        forwardcheck=False,
        _unassigned=Unassigned,
    ):
        for room_slot in room_slots:
            # get current slot assignment
            participant = assignments.get(room_slot, _unassigned)
            if participant is _unassigned or participant == '_':
                continue

        if forwardcheck:
            pass

        return True


def custom_participant_requirements(*args, **kwargs) -> bool:
    """ Ensures that all participant's requirements are met. """
    # variable for current status aggregation
    participant_rooms = {participant_name: None for participant_name in Container.participants.keys()}
    # map selected participants to assigned room slots
    for room_slot, participant in zip(Container.room_slots, args):
        # there is no need to validate room slots of "noone"
        if participant == "_":
            continue

        # get room name from slot
        participant_room = room_slot.split('_')[0]
        # add participant to assigned room
        participant_rooms[participant] = participant_room

    # go over all defined constraints
    for source_participant, constraints in Container.constraints.items():
        constraints: list
        # select first room as master room
        master_room = participant_rooms[source_participant]
        # validate, that all participants are in the same room
        for target_participant in constraints:
            # if not, discard this solution
            if participant_rooms[target_participant] != master_room:
                return False

    # everything is ok
    return True
