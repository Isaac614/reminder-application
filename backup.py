from PyQt5.QtWidgets import QApplication, QWidget, QLabel,  \
    QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea, \
    QCheckBox, QInputDialog
from PyQt5.QtCore import Qt
from clickable_label import ClickableLabel
from circle_button import CircleButton
from pathlib import Path
import script
import json
from datetime import datetime, timedelta

class ReminderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reminder Application")
        self.setGeometry(100, 100, 825, 475)
        
        # Set the main window background
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
            }
        """)
        
        # Layout setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

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
        
        # Dictionary to store all row widgets
        self.row_widgets = {}
        
        # Load data
        self.display_data()

    def is_within_month(self, event):
        """Check if an event is within a month from today"""
        try:
            # Parse the due date (assuming format like "June 6")
            event_date = datetime.strptime(event["due_date"], "%B %d")
            # Set the year to current year
            current_year = datetime.now().year
            event_date = event_date.replace(year=current_year)
            
            # If the event date is earlier in the year than current date, 
            # it's probably next year
            if event_date < datetime.now():
                event_date = event_date.replace(year=current_year + 1)
            
            # Check if the event is within a month
            one_month_from_now = datetime.now() + timedelta(days=30)
            return event_date <= one_month_from_now
        except ValueError:
            # If date parsing fails, don't show the event by default
            # This ensures we don't show events with invalid dates
            return False

    def should_show_event(self, event):
        """Determine if an event should be shown based on all filters"""
        # Check completion status
        completion_check = (not event["completed"] or self.show_completed_checkbox.isChecked())
        
        # Check past status
        past_check = (not event["past"] or self.show_past_checkbox.isChecked())
        
        # Check date range (only for future events)
        if not event["past"]:
            date_check = (self.is_within_month(event) or self.show_future_checkbox.isChecked())
        else:
            date_check = True  # Past events are not affected by the future events checkbox
        
        return completion_check and past_check and date_check

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
        main_layout.setSpacing(0)  # Remove spacing between left and right columns

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
        self.left_column.setStyleSheet("""
            #leftColumn {
                background-color: #1E1E1E;
                border-radius: 6px;
            }
        """)

        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setAlignment(Qt.AlignTop)
        self.left_layout.setContentsMargins(0, 10, 0, 10)
        self.left_layout.setSpacing(5)

        self.create_buttons(self.sorted_calendar_data)
    

    def create_text_area(self):
        self.right_column = QWidget(self)
        self.right_column.setObjectName("rightColumn")
        self.right_layout = QVBoxLayout(self.right_column)
        self.right_layout.setAlignment(Qt.AlignTop)
        self.right_layout.setContentsMargins(15, 0, 15, 15)
        self.right_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.right_column)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("scroll")
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E1E1E;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                min-height: 20px;
                border-radius: 4px;
                margin: 1px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add checkboxes
        self.checkbox_widget = QWidget(self)
        self.checkbox_widget.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 8px;
        """)
        self.checkbox_layout = QVBoxLayout(self.checkbox_widget)
        self.checkbox_layout.setAlignment(Qt.AlignLeft)
        self.checkbox_layout.setContentsMargins(10, 10, 10, 10)
        self.checkbox_layout.setSpacing(15)
        self.right_layout.addWidget(self.checkbox_widget)

        # Define checkbox stylesheet
        checkbox_style = """
            QCheckBox {
                spacing: 8px;
                color: #CCCCCC;
                font-size: 13px;
                min-width: 200px;
                padding: 5px 0px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 4px;
                border: 2px solid #5920E8;
                background-color: transparent;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #5920E8;
                background-color: transparent;
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid #7B4AFF;
                background-color: rgba(89, 32, 232, 0.1);
            }
            QCheckBox::indicator:checked {
                border: 2px solid #5920E8;
                background-color: #5920E8;
            }
            QCheckBox::indicator:checked:hover {
                border: 2px solid #7B4AFF;
                background-color: #7B4AFF;
            }
            QCheckBox:hover {
                color: #FFFFFF;
            }
        """

        self.show_past_checkbox = QCheckBox("Show Past Assignments")
        self.show_past_checkbox.setChecked(False)
        self.show_past_checkbox.stateChanged.connect(self.handle_show_past_checkbox_change)
        self.show_past_checkbox.setStyleSheet(checkbox_style)
        self.checkbox_layout.addWidget(self.show_past_checkbox)

        self.show_completed_checkbox = QCheckBox("Show Completed Assignments")
        self.show_completed_checkbox.setChecked(False)
        self.show_completed_checkbox.stateChanged.connect(self.handle_show_completed_checkbox_change)
        self.show_completed_checkbox.setStyleSheet(checkbox_style)
        self.checkbox_layout.addWidget(self.show_completed_checkbox)

        self.show_future_checkbox = QCheckBox("Show Events > 1 Month Out")
        self.show_future_checkbox.setChecked(False)
        self.show_future_checkbox.stateChanged.connect(self.handle_show_future_checkbox_change)
        self.show_future_checkbox.setStyleSheet(checkbox_style)
        self.checkbox_layout.addWidget(self.show_future_checkbox)

        # Create all row widgets upfront
        for class_name, events in self.sorted_calendar_data.items():
            for index, event in enumerate(events):
                row_widget = self.create_row_widget(index, event)
                self.row_widgets[f"{class_name}_{index}"] = row_widget
                self.right_layout.addWidget(row_widget)
                row_widget.setVisible(False)  # Initially hide all widgets

        # Show initial data
        self.update_text_area()
    

    def update_left_column(self, button_name): 
        """
        Called whenever a clickable label is selected. should update
        the styles of the buttons
        """
        button = self.left_column.findChild(ClickableLabel, button_name)
        
        # Set all buttons to inactive
        for label in self.clickable_labels.values():
            label.setProperty("active", False)
            label.style().unpolish(label)
            label.style().polish(label)
        
        # Set the selected button to active
        button.setProperty("active", True)
        button.style().unpolish(button)
        button.style().polish(button)


    def update_text_area(self):
        """
        Updates the text area by toggling visibility of existing widgets
        based on the selected class and checkbox states.
        """
        class_name = self.get_active_list()

        # First hide all widgets
        for widget in self.row_widgets.values():
            widget.setVisible(False)

        # Show relevant widgets based on selected class
        if class_name != "All Reminders":
            # Show widgets for selected class
            for index, event in enumerate(self.sorted_calendar_data[class_name]):
                widget_key = f"{class_name}_{index}"
                if widget_key in self.row_widgets:
                    widget = self.row_widgets[widget_key]
                    if self.should_show_event(event):
                        widget.setVisible(True)
        else:
            # Show all widgets that match the filter criteria
            for class_name, events in self.sorted_calendar_data.items():
                for index, event in enumerate(events):
                    widget_key = f"{class_name}_{index}"
                    if widget_key in self.row_widgets:
                        widget = self.row_widgets[widget_key]
                        # Only show the widget if it matches all filter criteria
                        if self.should_show_event(event):
                            widget.setVisible(True)
                        else:
                            widget.setVisible(False)


    def create_row_widget(self, index, event):
        row_widget = QWidget()
        row_widget.setObjectName("rowWidget")
        row_widget.setStyleSheet("""
            #rowWidget {
                background-color: #1E1E1E;
                border-radius: 6px;
                margin: 5px 0px;
            }
            #rowWidget:hover {
                background-color: #2A2A2A;
            }
        """)
        
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(15, 10, 15, 10)
        row_layout.setSpacing(15)

        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)   
        
        circle = self.create_circle_button(index, event)
            
        summary_label = QLabel(event["summary"])
        summary_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        
        due_date_label = QLabel(event["due_date"])
        due_date_label.setStyleSheet("color: #999999; font-size: 12px;")

        text_layout.addWidget(summary_label)
        text_layout.addWidget(due_date_label)

        row_layout.addWidget(circle)
        row_layout.addWidget(text_widget)

        return row_widget


    def create_buttons(self, sorted_calendar_data):
        self.clickable_labels = {}

        self.all_button = ClickableLabel("All Reminders", self.left_column)
        self.all_button.setFixedHeight(40)
        self.all_button.setObjectName("All_Reminders_button")
        self.all_button.setStyleSheet("""
            QLabel {
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px 10px;
                color: #CCCCCC;
            }
            QLabel[active="true"] {
                background-color: #5920E8;
                color: white;
            }
            QLabel[active="true"]:hover {
                background-color: #5920E8;
                color: white;
            }
            QLabel[active="false"] {
                background-color: transparent;
            }
            QLabel[active="false"]:hover {
                background-color: #333333;
                color: white;
            }
        """)
        self.all_button.setProperty("active", True)
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
        # This method handles toggling the state of the circle button and updating the JSON
        button = self.sender()
        self.update_json_on_complete(checked, button)  # Updates the JSON file with the new completion status

    def handle_label_click(self):
        sender = self.sender()
        
        # Set all buttons to inactive
        for label in self.clickable_labels.values():
            label.setProperty("active", False)
            label.style().unpolish(label)
            label.style().polish(label)
        
        # Set the clicked button to active
        sender.setProperty("active", True)
        sender.style().unpolish(sender)
        sender.style().polish(sender)
        
        # Update the text area
        self.update_text_area()


    def highlight_label(self, label=None):
        if not label:
            sender = self.sender()
            if sender:
                sender.setProperty("active", True)
                self.update_button_style(sender)
        else:
            label.setProperty("active", True)
            self.update_button_style(label)


    def clear_all_label_highlights(self):
        for label in self.clickable_labels.values():
            label.setProperty("active", False)
            self.update_button_style(label)


    def create_clickable_label(self, class_name):
        button = ClickableLabel(class_name, self.left_column)
        button.setFixedHeight(40)
        button.setObjectName(f"{class_name.replace(' ' , '_')}_button")
        button.setStyleSheet("""
            QLabel {
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px 10px;
                color: #CCCCCC;
            }
            QLabel[active="true"] {
                background-color: #5920E8;
                color: white;
            }
            QLabel[active="true"]:hover {
                background-color: #5920E8;
                color: white;
            }
            QLabel[active="false"] {
                background-color: transparent;
            }
            QLabel[active="false"]:hover {
                background-color: #333333;
                color: white;
            }
        """)
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
        # The styling is now handled by the QSS in create_clickable_label
        pass


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
        for class_name, events in self.sorted_calendar_data.items():
            for index, event in enumerate(events):
                widget_key = f"{class_name}_{index}"
                if widget_key in self.row_widgets:
                    widget = self.row_widgets[widget_key]
                    if event["past"]:
                        widget.setVisible(self.show_past_checkbox.isChecked() and self.should_show_event(event))


    def handle_show_completed_checkbox_change(self, checked):
        for class_name, events in self.sorted_calendar_data.items():
            for index, event in enumerate(events):
                widget_key = f"{class_name}_{index}"
                if widget_key in self.row_widgets:
                    widget = self.row_widgets[widget_key]
                    if self.should_show_event(event):
                        widget.setVisible(True)
                    else:
                        widget.setVisible(False)


    def update_json_on_complete(self, checked, button):
        # button = self.sender()
        index = button.property("event_index") # TODO - pulling wrong index :(
        class_name = button.property("event_class")

        if class_name in self.sorted_calendar_data:
            self.sorted_calendar_data[class_name][index]["completed"] = checked
            script.update_json("sorted_events.json", self.sorted_calendar_data)


    def handle_show_future_checkbox_change(self, checked):
        """Handle changes to the future events checkbox"""
        # Update the text area to reflect the new checkbox state
        self.update_text_area()


def main():
    app = QApplication([])  # QApplication must be created first
    window = ReminderApp()  # Create the ReminderApp window
    window.show()  # Show the window
    app.exec_()  # Start the event loop


if __name__ == "__main__":
    main()