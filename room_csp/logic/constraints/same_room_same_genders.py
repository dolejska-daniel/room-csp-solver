from constraint import Constraint, Unassigned, Domain

from ..container import Container
from ..utils import Utils


class SameRoomSameGenders(Constraint):
    """ Ensures that there is only one gender per room. No gender mixed assignments. """

    def __call__(
            self,
            room_slots,
            participant_domains: dict,
            assignments,
            forwardcheck=False,
            _unassigned=Unassigned,
    ):
        room_gender = {room_name: None for room_name in Container.rooms.keys()}

        # get current slot assignment
        for room_slot, participant_name in assignments.items():
            if participant_name == '_':
                continue

            # select room from slot name
            room = Utils.get_room_from_slot(room_slot)
            # get participant's gender
            gender = Utils.get_participant_gender(participant_name)

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
            # for assigned slot get current participant
            for room_slot, participant_name in assignments.items():
                if participant_name == '_':
                    continue

                # select room from slot name
                room = room_slot.split('_')[0]
                # get participant's gender
                gender = Utils.get_participant_gender(participant_name)

                _room_slots = Utils.get_room_slots(room)
                for target_room_slot in _room_slots:
                    # for all other slots in this room
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
