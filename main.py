from PyQt5.QtWidgets import QApplication, QWidget, QLabel,  QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea, QCheckBox
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
        self.left_column.setObjectName("leftColumn")
        self.left_column.setStyleSheet("#leftColumn {border: 2px solid black;}")

        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setAlignment(Qt.AlignTop)

        self.create_buttons(self.sorted_calendar_data)
    

    def create_text_area(self):

        self.right_column = QWidget(self)
        self.right_column.setObjectName("rightColumn")
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

        # Add checkboxes
        self.show_past_checkbox = QCheckBox("Show Past Assignments")
        self.show_past_checkbox.setChecked(False)
        self.show_past_checkbox.stateChanged.connect(self.update_text_area)

        self.right_layout.addWidget(self.show_past_checkbox)
    

    def update_left_column(self, button_name): 
        """
        Called whenever a clickable label is selected. should update
        the styles of the buttons
        """
        button = self.left_column.findChild(ClickableLabel, button_name)
        button.setProperty("active", True)
        self.update_button_style(button)

        # Set all other buttons to inactive
        for name, other_button in self.class_buttons.items():
            if other_button != button:
                other_button.setProperty("active", False)
                self.update_button_style(other_button)


    def update_text_area(self):
        """
        updates the text area everytime a clickable label is 
        clicked. This includes clearing previous data, 
        setting up checkboxes, and adding new data.
        """

        class_name = self.get_active_list()

        # Clear previous data
        self.delete_elements(self.right_layout, keep_widgets=[self.show_past_checkbox])

        # get relevant class data (or all the data)
        if class_name != "All Reminders":
            data = self.sorted_calendar_data[class_name]
        else: 
            data = []
            for class_name in self.sorted_calendar_data.keys():
                for event in self.sorted_calendar_data[class_name]:
                    data.append(event)

        # Populate text area
        for index, event in enumerate(data):
            row_widget = self.create_row_widget(index, event)

            if (data[index]["past"] and not self.show_past_checkbox.isChecked()) or data[index]["completed"]:
                row_widget.setVisible(False)

            self.right_layout.addWidget(row_widget)


    def create_row_widget(self, index, event):
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

        return row_widget


    def create_buttons(self, sorted_calendar_data):
        self.clickable_labels = {}

        all_button = ClickableLabel("All Reminders", self.left_column)
        all_button.setFixedHeight(35)
        all_button.setObjectName("All_Reminders_button")
        all_button.setStyleSheet("""border: 1px solid lightblue;
                                 background-color: transparent""")

        all_button.clicked.connect(self.handle_label_click)
        all_button.clicked.connect(self.update_text_area)

        self.left_layout.addWidget(all_button)
        self.clickable_labels["all_reminders"] = all_button
        
        for class_name in sorted_calendar_data:
            button = self.create_clickable_label(class_name)
            button.clicked.connect(self.handle_label_click)
            button.clicked.connect(self.update_text_area)

            self.left_layout.addWidget(button)
            self.clickable_labels[button.objectName()] = button


    def create_circle_button(self, index, event):
        circle = CircleButton(self)
        if event["completed"] == True:
            circle.setChecked(True)
            circle.toggle_fill()
        
        circle.setProperty("event_index", index)
        circle.setProperty("event_class", event["class"])

        circle.toggled.connect(self.update_json_on_complete, circle.isChecked())
        circle.toggled.connect(self.update_text_area)
        return circle


    def handle_label_click(self):
        self.clear_all_label_highlights()
        self.highlight_label()


    def highlight_label(self):
        sender = self.sender()
        if sender:
            sender.setStyleSheet("""background-color: lightblue;
                                 border: 1px solid lightblue;""")
            sender.setProperty("active", True)


    def clear_all_label_highlights(self):
        for label in self.clickable_labels.values():
            label.setStyleSheet("border: 1px solid lightblue; background-color: transparent")
            label.setProperty("active", False)


    def create_clickable_label(self, class_name):
        button = ClickableLabel(class_name, self.left_column)
        button.setFixedHeight(35)
        button.setObjectName(f"{class_name.replace(' ' , '_')}_button")
        button.setStyleSheet("border: 1px solid lightblue;")
        button.setProperty("active", False)
        return button


    def delete_elements(self, layout, keep_widgets=None):
        """
        Clears all widgets from the given layout except those in keep_widgets.
        
        :param layout: QLayout to clear
        :param keep_widgets: list of widgets to keep (optional)
        """
        if keep_widgets is None:
            keep_widgets = []

        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()

            if widget is not None and widget not in keep_widgets:
                widget.setParent(None)
                widget.deleteLater()


    def update_button_style(self, button):
        if button.property("active") is True:
            button.setStyleSheet("border: 1px solid lightblue; background-color: lightgreen;")
        else:
            button.setStyleSheet("border: 1px solid lightblue; background-color: transparent;")


    def get_active_list(self):
        for label in self.clickable_labels.values():
            if label.property("active") == True:
                return label.text()


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