

class Container:
    rooms: dict = {}
    room_slots: list = []
    participants: dict = {}
    participants_by_gender: dict = {}
    constraints: list = []

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
