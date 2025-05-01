from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel

class ClickableLabel(QLabel):
    # Define a signal for the click event
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        # Emit the signal when the label is clicked
        self.clicked.emit()