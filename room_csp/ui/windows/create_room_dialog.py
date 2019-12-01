from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QLineEdit, QSpinBox, QPushButton

from room_csp.ui.models import RoomModel

qt_creator_file = "ui/create_room_dialog.ui"
Ui_CreateRoomDialog, QtBaseClass = uic.loadUiType(qt_creator_file)


class CreateRoomDialog(QDialog, Ui_CreateRoomDialog):

    def __init__(self, room_model: RoomModel, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.findChild(QPushButton, "Create").clicked.connect(self.save)
        self.findChild(QPushButton, "Cancel").clicked.connect(self.reject)

        self.room_model = room_model

    def save(self):
        room_name: QLineEdit = self.findChild(QLineEdit, "RoomName")
        room_size: QSpinBox = self.findChild(QSpinBox, "RoomSize")

        self.room_model.add_entry(room_name.text(), {
            "name": room_name.text(),
            "beds": room_size.value()
        })
        self.accept()
