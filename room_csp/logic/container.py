import sys


class Container:
    """ Data holder for CSP solver. """

    rooms: dict = {}
    room_slots: list = []

    participants: dict = {}
    participants_by_gender: dict = {}
    participants_by_type: dict = {}

    constraints: dict = {}
    constraints_all: dict = {}

    @staticmethod
    def set_participants(participants: list):
        """ Saves defined participants and creates helper lists. """
        if not len(participants):
            return

        try:
            Container.participants = {
                p["name"]: p
                for p in participants
            }

            # create a set of existing genders
            genders = {p["gender"] for p in participants}
            # assign participants to given gender groups
            Container.participants_by_gender = {
                gender: {p["name"] for p in participants if p["gender"] == gender}
                for gender in genders
            }
            # add 'noone' to each gender group
            for data in Container.participants_by_gender.values():
                data.add('_')

            # create a set of existing genders
            types = {p["type"] for p in participants}
            # assign participants to given gender groups
            Container.participants_by_type = {
                _type: {p["name"] for p in participants if p["type"] == _type}
                for _type in types
            }
        except KeyError as err:
            print("Invalid participants format! Missing field: " + str(err), file=sys.stderr)

    @staticmethod
    def set_rooms(rooms: list):
        """ Saves defined rooms and generates corresponding number of room slots. """
        if not len(rooms):
            return

        try:
            Container.rooms = {
                r["name"]: r
                for r in rooms
            }

            room_slots = []
            # for each room
            for room in rooms:
                # based on its size
                for slot in range(0, room["beds"]):
                    # create slot
                    room_slots.append(f"{room['name']}_{slot}")

            Container.room_slots = room_slots
        except KeyError as err:
            print("Invalid rooms format! Missing field: " + str(err), file=sys.stderr)

    @staticmethod
    def set_constraints(constraints: dict):
        """ Saves defined participant constraints. """
        if not len(constraints):
            return

        try:
            Container.constraints = {
                constraint["name"]: [
                    participant["name"]
                    for participant in constraint["_items"]
                ]
                for constraint in constraints
            }

            for participant_name, subconstraints in Container.constraints.items():
                if participant_name in Container.constraints_all:
                    Container.constraints_all[participant_name] += set(subconstraints)
                    continue

                Container.constraints_all[participant_name] = set(subconstraints)

                for constrained_participant_name in subconstraints:
                    if constrained_participant_name in Container.constraints_all:
                        Container.constraints_all[constrained_participant_name] += participant_name
                        continue

                    Container.constraints_all[constrained_participant_name] = {participant_name}

        except KeyError as err:
            print("Invalid constraints format! Missing field: " + str(err), file=sys.stderr)
