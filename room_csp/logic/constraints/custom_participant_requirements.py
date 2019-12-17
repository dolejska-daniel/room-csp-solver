from constraint import Constraint, Unassigned, Domain

from ..utils import Utils


class CustomParticipantRequirements(Constraint):
    """ Ensures that all participant's requirements are met. """

    def __call__(
            self,
            room_slots,
            participant_domains: dict,
            assignments,
            forwardcheck=False,
            _unassigned=Unassigned,
    ):
        room_assignments = Utils.room_slot_assignment_to_room_participant_list(room_slots, assignments)
        # foreach assigned room slot
        for room_slot, participant_name in assignments.items():
            # which is not assigned to nobody
            if participant_name == '_':
                continue

            # if participant is actually constrained
            if not Utils.is_participant_constrained(participant_name):
                continue

            room = Utils.get_room_from_slot(room_slot)
            # list of participants constrained by this participant
            constrained_participants = Utils.get_participant_constraints(participant_name)
            # count of room slots which are already assigned
            assigned_room_slot_count = len(room_assignments[room])
            # count of currently unassigned room slots
            unassigned_room_slot_count = Utils.get_room_slot_count(room) - assigned_room_slot_count
            # count of room slots that have been assigned to constrained participants
            constraint_assigned_room_slots = len([
                1 for _participant_name in room_assignments[room]
                if _participant_name in constrained_participants
            ])

            # if count of yet unassigned room slots is smaller than
            # count of constrained participants yet to be assigned
            if unassigned_room_slot_count < len(constrained_participants) - constraint_assigned_room_slots:
                # then assignment is not possible
                return False

        if forwardcheck:
            for room_slot, participant_name in assignments.items():
                if participant_name == '_':
                    continue

                # for each assigned participant
                room = Utils.get_room_from_slot(room_slot)
                if Utils.is_participant_constrained(participant_name):
                    constrained_participants = Utils.get_participant_constraints(participant_name)
                    for constrained_participant_name in constrained_participants:
                        # for each their constraint
                        for slot in room_slots:
                            if slot.startswith(room):
                                # only for slots not in current room
                                continue

                            # remove it from domain of possible values
                            domain: Domain = participant_domains[slot]
                            if constrained_participant_name in domain:
                                domain.hideValue(constrained_participant_name)

        return True
