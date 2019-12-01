from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QComboBox

from room_csp.ui.models import ParticipantModel

qt_creator_file = "ui/create_participant_dialog.ui"
Ui_CreateParticipantDialog, QtBaseClass = uic.loadUiType(qt_creator_file)


class CreateParticipantDialog(QDialog, Ui_CreateParticipantDialog):

    def __init__(self, participant_model: ParticipantModel, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.findChild(QPushButton, "Create").clicked.connect(self.save)
        self.findChild(QPushButton, "Cancel").clicked.connect(self.reject)

        self.participant_model = participant_model

    def save(self):
        participant_name: QLineEdit = self.findChild(QLineEdit, "ParticipantName")
        participant_gender: QComboBox = self.findChild(QComboBox, "ParticipantGender")

        self.participant_model.add_entry(participant_name.text(), {
            "name": participant_name.text(),
            "gender": participant_gender.currentText()
        })
        self.accept()
