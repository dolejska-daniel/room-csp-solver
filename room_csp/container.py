class Container:
    """ Data holder for CSP solver. """

    rooms: dict = {}
    room_slots: list = []

    participants: dict = {}
    participants_by_gender: dict = {}

    constraints: dict = {}

    @staticmethod
    def set_participants(participants: list):
        """ Saves defined participants and creates helper lists. """
        if not len(participants):
            return

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

    @staticmethod
    def set_rooms(rooms: list):
        """ Saves defined rooms and generates corresponding number of room slots. """
        if not len(rooms):
            return

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

    @staticmethod
    def set_constraints(constraints: dict):
        """ Saves defined participant constraints. """
        if not len(constraints):
            return

        Container.constraints = {
            constraint["name"]: [
                participant["name"]
                for participant in constraint["_items"]
            ]
            for constraint in constraints
        }
