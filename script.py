from ics import Calendar
import requests
import json
from datetime import datetime, date
from pathlib import Path


def get_url():
    return input("Please enter the ics url: ")


def get_ics():
    url = get_url()
    response = requests.get(url)
    calendar = Calendar(response.text)
    return calendar


def parse_calendar_data(file):

    calendar_data = []
    for event in file.events:
        classname = get_substring(event.name, "[", "]")
        summary = get_substring(event.name, end_char = "[")
        event_id = event.uid
        description = event.description
        due_date = event.end.date().isoformat()
        if datetime.strptime(due_date, "%Y-%m-%d").date() <  date.today():
            past = True
        else:
            past = False
        date_obj = datetime.strptime(due_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %-d")

        sub_dictionary = {
            "uid" : event_id,
            "class" : classname,
            "summary" : summary,
            "description" : description,
            "due_date" : formatted_date,
            "completed" : False,
            "past" : past
        }
        calendar_data.append(sub_dictionary)

    return calendar_data


def sort_data_by_class(data):

    classnames = []
    for event in data:
        if event["class"] not in classnames:
            classnames.append(event["class"])

    sorted_dictionary = {}
    for classname in classnames:
        sorted_dictionary[classname] = get_assignments_for_class(data, classname)
    
    return sorted_dictionary


def sort_data_by_date(data):
    
    sorted_data = {}
    for classname in data:
        for i in range(len(data[classname])):
            sorted_events = sorted(
            data[classname],
            key=lambda event: get_date_from_string(event["due_date"])
        )
            sorted_data[classname] = sorted_events
    return sorted_data


def get_date_from_string(date_str):
    return datetime.strptime(date_str, "%B %d")

def get_substring(string, start_char = None, end_char = None):

    if not start_char:
        end_index = string.find(end_char)
        return string[:end_index]

    elif not end_char:
        start_index = string.find(start_char) + 1
        return string[start_index:]

    else:
        start_index = string.find(start_char) + 1
        end_index = string.find(end_char)
        return string[start_index:end_index]


def get_assignments_for_class(data, classname):

    assignment_list = []
    for event in data:
        if event["class"] == classname:
            assignment_list.append(event)

    return assignment_list


def update_json(filename, data):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent = 4)


def main():
        
    file_path = Path("sorted_events.json")
    if file_path.exists():
        with open(file_path) as json_file:
            sorted_calendar_data = json.load(json_file)

    else:
        with open(file_path, 'w') as json_file:
            calendar = get_ics()
            dictionary_data = parse_calendar_data(calendar)
            sorted_calendar_data = sort_data_by_class(dictionary_data)
            sorted_calendar_data = sort_data_by_date(sorted_calendar_data)
            update_json("sorted_events.json", sorted_calendar_data)

if __name__ == "__main__":
    main()

# a = [ # after parse calendar
#     {"uid" : "12345",
#     "class" : "WDD",
#     "summary" : "lorem",
#     "description" : "lorem"},

#     {"uid" : "12345",
#     "class" : "CSE",
#     "summary" : "lorem",
#     "description" : "lorem"}
# ]

# b = {"WDD" : [ # after sort copmound dictionary
#     {"uid" : "12345",
#     "class" : "WDD",
#     "summary" : "lorem",
#     "description" : "lorem"},

#     {"uid" : "12345",
#     "class" : "WDD",
#     "summary" : "lorem",
#     "description" : "lorem"}
# ],
# "CSE" : [
#     {"uid" : "12345",
#     "class" : "CSE",
#     "summary" : "lorem",
#     "description" : "lorem"},
#     {"uid" : "12345",
#     "class" : "CSE",
#     "summary" : "lorem",
#     "description" : "lorem"}
# ]}