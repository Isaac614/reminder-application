from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt
from clickable_label import ClickableLabel
from circle_button import CircleButton
import script

class ReminderApp(QWidget):
    def __init__(self, sorted_calendar_data):
        super().__init__()

        self.setWindowTitle("reminder Application")
        self.setGeometry(100, 100, 825, 475)
       
        self.left_column = QWidget(self)
        self.right_column = QWidget(self)

        self.left_column.setObjectName("leftColumn")
        self.right_column.setObjectName("rightColumn")

        self.left_column.setStyleSheet("#leftColumn {border: 2px solid black;}")

        self.all_reminders_button = ClickableLabel("All Reminders", self.left_column)
        self.all_reminders_button.setFixedHeight(35)
        self.all_reminders_button.setObjectName("allReminders")
        self.all_reminders_button.setStyleSheet("#allReminders{border: 1px solid lightblue;}")

        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setAlignment(Qt.AlignTop)
        self.left_layout.addWidget(self.all_reminders_button)

        self.create_buttons(sorted_calendar_data)

        
        self.right_layout = QVBoxLayout(self.right_column)
        self.right_column_label = QLabel("placeholer label", self.right_column)
        self.right_layout.addWidget(self.right_column_label)

        scroll_area = QScrollArea(self)
        scroll_area.setWidget(self.right_column)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setObjectName("scroll")
        scroll_area.setStyleSheet("#scroll {border: 2px solid red;}")
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QHBoxLayout(self)

        self.left_column.setFixedWidth(self.width() // 5)

        main_layout.addWidget(self.left_column)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
    
    def update_text_area(self, data):
        for i in reversed(range(self.right_layout.count())):
            item = self.right_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        for event in data:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            circle = CircleButton(self)
            label = QLabel(event["summary"])

            row_layout.addWidget(circle)
            row_layout.addWidget(label)

            self.right_layout.addWidget(row_widget)
    

    def create_buttons(self, sorted_calendar_data):
        self.class_buttons = {}
        for classname in sorted_calendar_data:
            button = ClickableLabel(classname, self.left_column)
            button.setFixedHeight(35)
            button.setObjectName(f"{classname.replace(" ", "_")}_button")
            button.setStyleSheet("border: 1px solid lightblue;")
            button.clicked.connect(lambda name=classname: self.update_text_area(sorted_calendar_data[name]))


            self.left_layout.addWidget(button)
            self.class_buttons[classname] = button

def main():
    app = QApplication([])

    calendar = script.get_ics()
    dictionary_data = script.parse_calendar_data(calendar)
    sorted_calendar_data = script.sort_data_by_class(dictionary_data)
    sorted_calendar_data = script.sort_data_by_date(sorted_calendar_data)

    window = ReminderApp(sorted_calendar_data)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()