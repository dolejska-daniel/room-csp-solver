import typing

from .container import Container


class Utils:

    @staticmethod
    def room_slot_assignment_to_room_participant_list(slots: list, assignments: dict) -> {list}:
        result = {room_name: [] for room_name in Container.rooms.keys()}
        for slot in slots:
            if slot not in assignments:
                continue

            room = Utils.get_room_from_slot(slot)
            result[room].append(assignments[slot])

        return result

    @staticmethod
    def get_room_from_slot(room_slot: str) -> str:
        return room_slot[:room_slot.index('_')]

    @staticmethod
    def get_room_slots(room_name: str) -> [str]:
        return [f"{room_name}_{slot}" for slot in range(Container.rooms[room_name]["beds"])]

    @staticmethod
    def get_room_slot_count(room_name: str) -> int:
        return Container.rooms[room_name]["beds"]

    @staticmethod
    def get_participant_names() -> set:
        return set(Container.participants.keys())

    @staticmethod
    def get_participant(participant_name: str) -> dict:
        return Container.participants[participant_name]

    @staticmethod
    def get_participant_type(participant_name: str) -> str:
        return Container.participants[participant_name]["type"]

    @staticmethod
    def get_participant_gender(participant_name: str) -> str:
        return Container.participants[participant_name]["gender"]

    @staticmethod
    def get_room_type(room_name: str) -> str:
        return Container.rooms[room_name]["type"]

    @staticmethod
    def is_participant_constrained(participant_name: str):
        return participant_name in Container.constraints_all

    @staticmethod
    def get_participant_constraints(participant_name: str) -> dict:
        return Container.constraints_all[participant_name]

    @staticmethod
    def all_participant_constraints_valid(participant_name: str, check_function: typing.Callable[..., bool],
                                          check_function_data: list) -> bool:
        constrained_participants = Utils.get_participant_constraints(participant_name)
        for constrained_participant_name in constrained_participants:
            if not check_function(participant_name, constrained_participant_name, *check_function_data):
                return False

        return True
