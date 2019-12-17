from constraint import Constraint, Unassigned


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
        # get current slot assignment
        for room_slot, participant in assignments.items():
            if participant == '_':
                continue

            if participant in seen:
                return False

            seen.add(participant)

        if forwardcheck:
            for room_slot, participant in assignments.items():
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
