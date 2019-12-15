from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QSpinBox, QPushButton, QComboBox

qt_creator_file = "ui/create_room_dialog.ui"
Ui_CreateRoomDialog, QCreateRoomDialog = loadUiType(qt_creator_file)


class CreateRoomDialog(QCreateRoomDialog, Ui_CreateRoomDialog):
    room_data_sent = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.findChild(QPushButton, "Create").clicked.connect(self.save)
        self.findChild(QPushButton, "Cancel").clicked.connect(self.reject)

    def save(self):
        room_name: QLineEdit = self.findChild(QLineEdit, "RoomName")
        room_size: QSpinBox = self.findChild(QSpinBox, "RoomSize")
        room_type: QComboBox = self.findChild(QComboBox, "RoomType")

        self.room_data_sent.emit({
            "name": room_name.text(),
            "beds": room_size.value(),
            "type": room_type.currentText()
        })
        self.accept()
