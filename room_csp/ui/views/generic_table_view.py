from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableView
from PyQt5.QtGui import QKeyEvent, QMouseEvent

from .extended_item_view import ExtendedItemView


class GenericTableView(QTableView, ExtendedItemView):
    keyReleased = pyqtSignal(QKeyEvent)
    mouseReleased = pyqtSignal(QMouseEvent)
    mouseDoubleClick = pyqtSignal(QMouseEvent)

    def __init__(self, parent=None):
        super().__init__(parent)
