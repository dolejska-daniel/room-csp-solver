from constraint import Constraint, Domain, Unassigned
from .container import Container


class AllParticipantsAssigned(Constraint):
    """ Ensures that all participants are assigned to at least one room. """

    def __call__(
        self,
        room_slots,
        participant_domains,
        assignments,
        forwardcheck=False,
        _unassigned=Unassigned,
    ):
        # check that each room slot
        for room_slot in room_slots:
            # has assigned participant
            if room_slot not in assignments:
                return True

        unassigned_participants = set(Container.participants.keys())
        # validate that for each room slot
        for room_slot in room_slots:
            # assigned participant of that slot
            participant = assignments.get(room_slot, _unassigned)
            if participant == '_':
                continue

            if participant not in unassigned_participants:
                continue

            # is marked as assigned
            unassigned_participants.remove(participant)

        # if there are unassigned participant even with all slots assigned
        # something is wrong
        if len(unassigned_participants) > 0:
            return False

        # everything is ok here
        return True


class UniquelyAssignedParticipants(Constraint):
    """ Ensures that participants are assigned to rooms' slots only once. """

    def __call__(
        self,
        room_slots,
        participant_domains,
        assignments,
        forwardcheck=False,
        _unassigned=Unassigned,
    ):
        seen = set()
        for room_slot in room_slots:
            # get current slot assignment
            participant = assignments.get(room_slot, _unassigned)
            if participant is _unassigned or participant == '_':
                continue

            if participant in seen:
                return False

            seen.add(participant)

        if forwardcheck:
            for room_slot in room_slots:
                if room_slot in assignments:
                    # for assigned slot get current participant
                    participant = assignments.get(room_slot, _unassigned)
                    if participant == '_':
                        continue

                    # now for each room slot participant domain
                    for target_room_slot, participant_domain in participant_domains.items():
                        if target_room_slot == room_slot:
                            continue

                        # which contains this participant
                        if participant in participant_domain:
                            # remove this participant as possible value
                            participant_domain.hideValue(participant)

        return True


class SameRoomSameGenders(Constraint):
    """ Ensures that there is only one gender per room. No gender mixed assignments. """

    def __call__(
        self,
        room_slots,
        participant_domains,
        assignments,
        forwardcheck=False,
        _unassigned=Unassigned,
    ):
        # print(variables, domains, assignments)
        room_gender = {room['name']: None for room in Container.rooms.values()}

        for room_slot in room_slots:
            # get current slot assignment
            participant = assignments.get(room_slot, _unassigned)
            if participant is _unassigned or participant == '_':
                continue

            # select room from slot name
            room = room_slot.split('_')[0]
            # get participant's gender
            gender = Container.participants[participant]["gender"]

            if room_gender[room] is None:
                # no master gender has been selected yet
                room_gender[room] = gender
            else:
                # master gender has been selected
                if room_gender[room] != gender:
                    # genders are not the same
                    return False

        # check whether forward check should be done
        if forwardcheck:
            for room_slot in room_slots:
                if room_slot in assignments:
                    # for assigned slot get current participant
                    participant = assignments.get(room_slot, _unassigned)
                    if participant == '_':
                        continue

                    # select room from slot name
                    room = room_slot.split('_')[0]
                    # get participant's gender
                    gender = Container.participants[participant]["gender"]

                    for slot in range(0, Container.rooms[room]["beds"]):
                        # for all other slots in this room
                        target_room_slot = f"{room}_{slot}"
                        # reduce available selection

                        # get current domain
                        participant_domain: Domain = participant_domains[target_room_slot]
                        # get same gender participants
                        same_gender_participants = Container.participants_by_gender[gender]
                        for domain_participant in participant_domain:
                            # and for each participant from that domain
                            # who is not of same gender
                            if domain_participant not in same_gender_participants:
                                # remove as possible value
                                participant_domain.hideValue(domain_participant)

        return True


def custom_participant_requirements(*args, **kwargs) -> bool:
    """ Ensures that all participant's requirements are met. """
    # variable for current status aggregation
    participant_rooms = {p: None for p in Container.participants.keys()}
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
    for constraint_participant, constraints in Container.constraints.items():
        constraints: list
        # select first room as master room
        master_room = participant_rooms[constraint_participant]
        # validate, that all participants are in the same room
        for constraint in constraints:
            if not constraint["enabled"]:
                continue

            # if not, discard this solution
            if participant_rooms[constraint["participant"]] != master_room:
                return False

    # everything is ok
    return True
