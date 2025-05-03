import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,  QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea, QCheckBox, QInputDialog
from PyQt5.QtCore import Qt, QTimer
from clickable_label import ClickableLabel
from circle_button import CircleButton
from pathlib import Path
import script
import json

class ReminderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reminder Application")
        self.setGeometry(100, 100, 825, 475)
        
        # Layout setup
        self.layout = QVBoxLayout(self)

        file_path = Path("sorted_events.json")
        if file_path.exists():
            with open(file_path) as json_file:
                self.sorted_calendar_data = json.load(json_file)

        else:
            self.ics_link = None
            self.get_user_input()
            with open(file_path, 'w') as json_file:
                calendar = script.get_ics(self.ics_link)
                dictionary_data = script.parse_calendar_data(calendar)
                self.sorted_calendar_data = script.sort_data_by_class(dictionary_data)
                self.sorted_calendar_data = script.sort_data_by_date(self.sorted_calendar_data)
                script.update_json("sorted_events.json", self.sorted_calendar_data)
        

        # Load data
        self.display_data()


    def get_user_input(self):
        # You can use QInputDialog to show a dialog asking for user input
        text, ok = QInputDialog.getText(self, "Enter ics", "Please enter the ics url\n(navigate to canvas, calendar, and select 'calendar feed' near the bottom)")
        if ok and text:
            self.ics_link = text
        else:
            pass  # or some default input


    def display_data(self):
        super().__init__()
        # Set window title and geometry
        self.setWindowTitle("Reminder Application")
        self.setGeometry(100, 100, 825, 475)

        # Initialize the layout for the window
        self.create_left_column()
        self.create_text_area()

        # Create a main layout (horizontal layout)
        main_layout = QHBoxLayout(self)

        # Set fixed width for left column
        self.left_column.setFixedWidth(self.width() // 5)

        # Add left column and scrollable right column to the main layout
        main_layout.addWidget(self.left_column)
        main_layout.addWidget(self.scroll_area)

        # Apply the main layout to the window
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
        self.right_layout.setAlignment(Qt.AlignTop)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.right_column)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setObjectName("scroll")
        self.scroll_area.setStyleSheet("#scroll {border: 2px solid red;}")
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add checkboxes
        self.checkbox_widget = QWidget(self)
        self.checkbox_layout = QHBoxLayout(self.checkbox_widget)
        self.checkbox_layout.setAlignment(Qt.AlignLeft)
        self.checkbox_layout.setContentsMargins(0, 5, 0, 5)
        self.checkbox_widget.setStyleSheet("margin-left: -1;")
        self.right_layout.addWidget(self.checkbox_widget)

        self.show_past_checkbox = QCheckBox("Show Past Assignments")
        self.show_past_checkbox.setChecked(False)
        self.show_past_checkbox.stateChanged.connect(self.handle_show_past_checkbox_change)
        self.checkbox_layout.addWidget(self.show_past_checkbox)

        self.show_completed_checkbox = QCheckBox("Show Completed Assignments")
        self.show_completed_checkbox.setChecked(False)
        self.show_completed_checkbox.stateChanged.connect(self.handle_show_completed_checkbox_change)
        self.checkbox_layout.addWidget(self.show_completed_checkbox)

        self.update_text_area()
    

    def update_left_column(self, button_name): 
        """
        Called whenever a clickable label is selected. should update
        the styles of the buttons
        """
        button = self.left_column.findChild(ClickableLabel, button_name)
        button.setProperty("active", True)
        self.update_button_style(button)

        # Set all other buttons to inactive
        for name, other_button in self.clickable_labels.items():
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
        self.delete_elements(self.right_layout, keep_widgets=[self.checkbox_widget])

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

            if (data[index]["past"] and not self.show_past_checkbox.isChecked()) or \
                (data[index]["completed"] and not self.show_completed_checkbox.isChecked()):
                row_widget.setVisible(False)

            self.right_layout.addWidget(row_widget)


    def should_show_event(self, event):
        return (not event["past"] or self.show_past_checkbox.isChecked()) and \
            (not event["completed"] or self.show_completed_checkbox.isChecked())


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

        self.all_button = ClickableLabel("All Reminders", self.left_column)
        self.all_button.setFixedHeight(35)
        self.all_button.setObjectName("All_Reminders_button")
        self.all_button.setStyleSheet("""border: 1px solid lightblue;
                                 background-color: transparent""")
        self.all_button.setProperty("active", True)
        self.highlight_label(label=self.all_button)

        self.all_button.clicked.connect(self.handle_label_click)

        self.left_layout.addWidget(self.all_button)
        self.clickable_labels["all_reminders"] = self.all_button
        
        for class_name in sorted_calendar_data:
            button = self.create_clickable_label(class_name)
            button.clicked.connect(self.handle_label_click)

            self.left_layout.addWidget(button)
            self.clickable_labels[button.objectName()] = button
            

    def create_circle_button(self, index, event):
        circle = CircleButton(self)
        if event["completed"] == True:
            circle.setChecked(True)
            circle.toggle_fill()
        
        circle.setProperty("event_data", event)
        circle.setProperty("event_index", index)
        circle.setProperty("event_class", event["class"])
        try:
            circle.toggled.disconnect(self.handle_circle_toggle)
        except TypeError:
            pass
        circle.toggled.connect(self.handle_circle_toggle)
        return circle
    

    def handle_circle_toggle(self, checked):
        # This method handles both toggling the state of the circle button and updating the text area
        button = self.sender()
        self.update_json_on_complete(checked, button)  # Updates the JSON file with the new completion status
        self.update_row_visibility_on_complete(checked, button)  # Updates the row visibility based on completion
        

    def handle_label_click(self):

        sender = self.sender()
        if sender.property("active") == True:
            return
        
        self.clear_all_label_highlights()
        self.highlight_label()
        self.update_text_area()


    def highlight_label(self, label = None):
        if not label:
            sender = self.sender()
            if sender:
                sender.setStyleSheet("""background-color: lightblue;
                                    border: 1px solid lightblue;""")
                sender.setProperty("active", True)
        
        else:
            label.setStyleSheet("""background-color: lightblue;
                                    border: 1px solid lightblue;""")
            label.setProperty("active", True)


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


    def update_row_visibility_on_complete(self, checked, button):
        # button = self.sender()
        row_widget = button.parent()

        if not self.show_completed_checkbox.isChecked() and checked:
            row_widget.setVisible(False)
        else:
            row_widget.setVisible(True)


    def handle_show_past_checkbox_change(self):
        for i in range(self.right_layout.count()):
            row = self.right_layout.itemAt(i).widget()
            if not row or row == self.checkbox_widget:
                continue

            circle = row.findChild(CircleButton)
            if not circle:
                continue

            index = circle.property("event_index")
            class_name = circle.property("event_class")

            if class_name not in self.sorted_calendar_data:
                continue

            event_list = self.sorted_calendar_data[class_name]
            if not (0 <= index < len(event_list)):
                continue

            event = event_list[index]

            if event["past"]:
                row.setVisible(self.show_past_checkbox.isChecked())


    def handle_show_completed_checkbox_change(self, checked):
        for i in range(self.right_layout.count()):
            row = self.right_layout.itemAt(i).widget()
            if not row or row == self.checkbox_widget:
                continue  # Skip the checkbox widget itself

            circle = row.findChild(CircleButton)
            if not circle:
                continue  # Skip rows that don't contain a circle button

            event = circle.property("event_data")
            is_completed = circle.isChecked()  # Whether the event is marked as completed
            is_past = event["past"]  # Whether the event is past

            # Determine if the row should be visible
            if (is_completed and not checked) or (is_past and not self.show_past_checkbox.isChecked()):
                row.setVisible(False)
            else:
                row.setVisible(True)


    def update_json_on_complete(self, checked, button):
        # button = self.sender()
        index = button.property("event_index") # TODO - pulling wrong index :(
        class_name = button.property("event_class")

        if class_name in self.sorted_calendar_data:
            self.sorted_calendar_data[class_name][index]["completed"] = checked
            script.update_json("sorted_events.json", self.sorted_calendar_data)


def main():
    app = QApplication([])  # QApplication must be created first
    window = ReminderApp()  # Create the ReminderApp window
    window.show()  # Show the window
    app.exec_()  # Start the event loop


if __name__ == "__main__":
    main()