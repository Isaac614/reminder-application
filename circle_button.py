from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor

class CircleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(QSize(16, 16))
        self.setStyleSheet(self.style_empty())
        self.toggled.connect(self.toggle_fill)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def style_empty(self):
        return """
            QPushButton {
                border: 2px solid #5920E8;
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:hover {
                border: 2px solid #7A3DFF;
            }
        """

    def style_filled(self):
        return """
            QPushButton {
                border: 2px solid #5920E8;
                border-radius: 8px;
                background-color: #5920E8;
            }
            QPushButton:hover {
                border: 2px solid #7A3DFF;
                background-color: #7A3DFF;
            }
        """

    def toggle_fill(self):
        if self.isChecked():
            self.setStyleSheet(self.style_filled())
        else:
            self.setStyleSheet(self.style_empty())