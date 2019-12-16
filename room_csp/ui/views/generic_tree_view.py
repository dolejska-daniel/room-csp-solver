from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui import QKeyEvent, QMouseEvent

from .extended_item_view import ExtendedItemView


class GenericTreeView(QTreeView, ExtendedItemView):
    keyReleased = pyqtSignal(QKeyEvent)
    mouseReleased = pyqtSignal(QMouseEvent)
    mouseDoubleClick = pyqtSignal(QMouseEvent)

    def __init__(self, parent=None):
        super().__init__(parent)
