from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox

qt_creator_file = "ui/create_participant_dialog.ui"
Ui_CreateParticipantDialog, QCreateParticipantDialog = loadUiType(qt_creator_file)


class CreateParticipantDialog(QCreateParticipantDialog, Ui_CreateParticipantDialog):
    participant_data_sent = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.findChild(QPushButton, "Create").clicked.connect(self.save)
        self.findChild(QPushButton, "Cancel").clicked.connect(self.reject)

    def save(self):
        participant_name: QLineEdit = self.findChild(QLineEdit, "ParticipantName")
        participant_gender: QComboBox = self.findChild(QComboBox, "ParticipantGender")
        participant_type: QComboBox = self.findChild(QComboBox, "ParticipantType")

        self.send_participant_data.emit({
            "name": participant_name.text(),
            "gender": participant_gender.currentText(),
            "type": participant_type.currentText(),
        })
        self.accept()
