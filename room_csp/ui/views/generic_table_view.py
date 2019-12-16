from PyQt5.QtWidgets import QTableView


class GenericTableView(QTableView):

    def __init__(self, parent=None):
        super().__init__(parent)
