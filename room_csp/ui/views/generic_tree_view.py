from PyQt5.QtWidgets import QTreeView


class GenericTreeView(QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent)
