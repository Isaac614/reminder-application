from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt
from clickableLabel import ClickableLabel
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

        self.left_column.setStyleSheet("""#leftColumn {
                                       border: 2px solid black;}""")
        
        self.all_reminders_button = ClickableLabel("All Reminders", self.left_column)
        self.all_reminders_button.setFixedHeight(35)
        self.all_reminders_button.setObjectName("allReminders")
        self.all_reminders_button.setStyleSheet("""#allReminders{
                                                border: 1px solid lightblue;}""")
        
        self.wdd_reminders_button = ClickableLabel("WDD Reminders", self.left_column)
        self.wdd_reminders_button.setFixedHeight(35)
        self.wdd_reminders_button.setObjectName("wddReminders")
        self.wdd_reminders_button.setStyleSheet("""#wddReminders{
                                                border: 1px solid lightblue;}""")
        
        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setAlignment(Qt.AlignTop)
        self.left_layout.addWidget(self.all_reminders_button)
        self.left_layout.addWidget(self.wdd_reminders_button)

    
        
        self.right_layout = QVBoxLayout(self.right_column)
        self.right_column_label = QLabel("placeholer label", self.right_column)
        self.right_layout.addWidget(self.right_column_label)
        self.wdd_reminders_button.clicked.connect(lambda : self.update_text_area(sorted_calendar_data["WDD 131"]))

        scroll_area = QScrollArea(self)
        scroll_area.setWidget(self.right_column)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setObjectName("scroll")
        scroll_area.setStyleSheet("""#scroll {
                                  border: 2px solid red;}""")

        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QHBoxLayout(self)

        self.left_column.setFixedWidth(self.width() // 5)

        main_layout.addWidget(self.left_column)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def update_text_area(self, data):
        self.add_labels_to_text_area(data)
        for index, event in enumerate(data):
            self.right_column_label.setText(event["summary"])
    
    def add_labels_to_text_area(self, data):
        for i in reversed(range(self.right_layout.count())):
            item = self.right_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        for event in data:
            label = QLabel(event["summary"])
            self.right_layout.addWidget(label)


def main():
    app = QApplication([])

    calendar = script.get_ics()
    dictionary_data = script.parse_calendar_data(calendar)
    sorted_calendar_data = script.sort_data(dictionary_data)

    window = ReminderApp(sorted_calendar_data)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()