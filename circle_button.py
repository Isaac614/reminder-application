from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize

class CircleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(QSize(10, 10))
        self.setStyleSheet(self.style_empty())
        self.clicked.connect(self.toggle_fill)

    def style_empty(self):
        return """
            QPushButton {
                border: 1px solid black;
                border-radius: 5px;
                background-color: none;
            }
        """

    def style_filled(self):
        return """
            QPushButton {
                border: 1px solid black;
                border-radius: 5px;
                background-color: purple;
            }
        """

    def toggle_fill(self):
        if self.isChecked():
            self.setStyleSheet(self.style_filled())
        else:
            self.setStyleSheet(self.style_empty())