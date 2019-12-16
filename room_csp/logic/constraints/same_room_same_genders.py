from constraint import Constraint, Unassigned, Domain

from room_csp.logic import Container


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
        print(type(room_slots), type(assignments))
        room_gender = {room_name: None for room_name in Container.rooms.keys()}

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
