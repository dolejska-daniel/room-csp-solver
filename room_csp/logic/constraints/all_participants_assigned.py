from constraint import Constraint, Unassigned

from ..container import Container


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
        # validate, that for each room slot
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
