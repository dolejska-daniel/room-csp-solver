from constraint import Constraint, Unassigned, Domain

from ..utils import Utils


class RespectRoomType(Constraint):
    """ Ensures that participants with given type are assigned to rooms with the same type. """

    def __call__(
            self,
            room_slots,
            participant_domains: dict,
            assignments,
            forwardcheck=False,
            _unassigned=Unassigned,
    ):
        # foreach assigned room slot
        for room_slot, participant_name in assignments.items():
            # which is not assigned to nobody
            if participant_name == '_':
                continue

            room = Utils.get_room_from_slot(room_slot)
            if Utils.get_room_type(room) != Utils.get_participant_type(participant_name):
                # room type does not match with participant type
                return False

        if forwardcheck:
            for room_slot, slot_domain in participant_domains.items():
                room = Utils.get_room_from_slot(room_slot)
                room_type = Utils.get_room_type(room)
                for participant_name in slot_domain:
                    slot_domain: Domain
                    if participant_name == '_':
                        continue

                    if Utils.get_participant_type(participant_name) != room_type:
                        slot_domain.hideValue(participant_name)

        return True
