from PyQt5.QtWidgets import QApplication, QWidget, QLabel,  QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt
from clickable_label import ClickableLabel
from circle_button import CircleButton
import script

class ReminderApp(QWidget):
    def __init__(self, sorted_calendar_data):
        super().__init__()

        self.sorted_calendar_data = sorted_calendar_data

        self.setWindowTitle("reminder Application")
        self.setGeometry(100, 100, 825, 475)

        self.create_left_column()
        self.create_text_area()

        main_layout = QHBoxLayout(self)

        self.left_column.setFixedWidth(self.width() // 5)

        main_layout.addWidget(self.left_column)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)


    def create_left_column(self):
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

        self.create_buttons(self.sorted_calendar_data)
    

    def create_text_area(self):
        self.right_layout = QVBoxLayout(self.right_column)
        self.right_column_label = QLabel("placeholer label", self.right_column)
        self.right_layout.addWidget(self.right_column_label)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.right_column)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setObjectName("scroll")
        self.scroll_area.setStyleSheet("#scroll {border: 2px solid red;}")
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    

    def create_buttons(self, sorted_calendar_data):
        self.class_buttons = {}
        for classname in sorted_calendar_data:
            button = ClickableLabel(classname, self.left_column)
            button.setFixedHeight(35)
            button.setObjectName(f"{classname.replace(" ", "_")}_button")
            button.setStyleSheet("border: 1px solid lightblue;")
            button.clicked.connect(lambda name=classname: self.update_text_area(self.sorted_calendar_data[name]))


            self.left_layout.addWidget(button)
            self.class_buttons[classname] = button


    def update_text_area(self, data):
        self.delete_elements(self.right_layout)

        for index, event in enumerate(data):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 5, 0, 5)

            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(0)
            
            circle = self.create_circle_button(index, event)
                
            summary_label = QLabel(event["summary"])
            due_date_label = QLabel(event["due_date"])
            due_date_label.setStyleSheet("font-size: 12px;")

            text_layout.addWidget(summary_label)
            text_layout.addWidget(due_date_label)

            row_layout.addWidget(circle)
            row_layout.addWidget(text_widget)

            self.right_layout.addWidget(row_widget)


    def create_circle_button(self, index, event):
        circle = CircleButton(self)
        if event["completed"] == True:
            circle.setChecked(True)
            circle.toggle_fill()
        
        circle.setProperty("event_index", index)
        circle.setProperty("event_class", event["class"])

        circle.toggled.connect(self.update_json_on_complete, circle.isChecked())
        return circle


    def delete_elements(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()


    def update_json_on_complete(self, checked):
        button = self.sender()
        index = button.property("event_index")
        class_name = button.property("event_class")

        if class_name in self.sorted_calendar_data:
            self.sorted_calendar_data[class_name][index]["completed"] = checked
            script.update_json("sorted_events.json", self.sorted_calendar_data)


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