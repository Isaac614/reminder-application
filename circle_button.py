from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor

class CircleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(QSize(12, 12))
        self.setStyleSheet(self.style_empty())
        self.toggled.connect(self.toggle_fill)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def style_empty(self):
        return """
            QPushButton {
                border: 1px solid black;
                border-radius: 6px;
                background-color: transparent;
            }
        """

    def style_filled(self):
        return """
            QPushButton {
                border: 1px solid black;
                border-radius: 6px;
                background-color: purple;
            }
        """

    def toggle_fill(self):
        if self.isChecked():
            self.setStyleSheet(self.style_filled())
        else:
            self.setStyleSheet(self.style_empty())