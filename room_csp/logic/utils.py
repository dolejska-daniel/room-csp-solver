from room_csp.logic import Container


def room_slot_assignment_to_room_participant_list(slots: list, assignments: dict) -> {list}:
    result = {room_name: [] for room_name in Container.rooms.keys()}
    for slot in slots:
        if slot not in assignments:
            continue

        room, _ = slot.index('_')
        result[room].append(assignments[slot])

    return result
