from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QCursor

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Make cursor a pointer on hover

    def mousePressEvent(self, event):
        self.clicked.emit()