
class Container:
    rooms: dict = {}
    room_slots: list = []
    participants: dict = {}
    participants_by_gender: dict = {}
    constraints: list = []

    @staticmethod
    def initialize(data: dict):
        try:
            rooms = data["rooms"]
            participants = data["participants"]
            constraints = data["constraints"]

            Container.set_rooms({r["name"]: r for r in rooms})
            Container.set_participants({p["name"]: p for p in participants})
            Container.constraints = constraints
        except KeyError:
            raise RuntimeError("Invalid data object provided.")

    @staticmethod
    def set_participants(participants: dict):
        Container.participants = participants

        genders = {p["gender"] for p in participants.values()}
        Container.participants_by_gender = {
            gender: {p for p, pdata in participants.items() if pdata["gender"] == gender}
            for gender in genders
        }

        for data in Container.participants_by_gender.values():
            data.add('_')

    @staticmethod
    def set_rooms(rooms: dict):
        Container.rooms = rooms

        room_slots = []
        for room in rooms.values():
            for slot in range(0, room["beds"]):
                room_slots.append(f"{room['name']}_{slot}")

        Container.room_slots = room_slots
