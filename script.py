from ics import Calendar
import requests

# https://byui.instructure.com/feeds/calendars/user_MW9zKHiVd9h9cuWWsZjt5i1zHLRYUrt3wzEo4xjC.ics


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
        sub_dictionary = {
            "uid" : event_id,
            "class" : classname,
            "summary" : summary,
            "description" : description,
            "due_date" : event.end.date().isoformat()
        }
        calendar_data.append(sub_dictionary)

    return calendar_data


def sort_data(data):

    classnames = []
    for event in data:
        if event["class"] not in classnames:
            classnames.append(event["class"])

    sorted_dictionary = {}
    for classname in classnames:
        sorted_dictionary[classname] = get_assignments_for_class(data, classname) #TODO - always makes dict[0] new val rather than adding to end of it
    
    return sorted_dictionary


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
        

def main():
    calendar = get_ics()
    dictionary_data = parse_calendar_data(calendar)
    sorted_calendar_data = sort_data(dictionary_data)


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