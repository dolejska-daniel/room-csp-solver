from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtGui import QKeyEvent, QMouseEvent


class ExtendedItemView(QAbstractItemView):
    keyReleased = pyqtSignal(QKeyEvent)
    mouseReleased = pyqtSignal(QMouseEvent)
    mouseDoubleClick = pyqtSignal(QMouseEvent)

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        super().keyReleaseEvent(event)
        self.keyReleased.emit(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.mouseReleased.emit(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        self.mouseDoubleClick.emit(event)
