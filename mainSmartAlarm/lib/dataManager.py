import ujson
import uos

# File name to store the data
DEADLINE_FILE_NAME = "deadlines.json"
ALARM_FILE_NAME = "alarms.json"

# Save the deadline list to a file
def save_deadlines(deadline_list):
    try:
        with open(DEADLINE_FILE_NAME, "w") as file:
            ujson.dump(deadline_list, file)
        print(f"Deadlines saved successfully to {DEADLINE_FILE_NAME}.")
    except Exception as e:
        print(f"Failed to save deadlines: {e}")

# Load the deadline list from a file
def load_deadlines():
    try:
        if DEADLINE_FILE_NAME in uos.listdir():
            with open(DEADLINE_FILE_NAME, "r") as file:
                deadline_list = ujson.load(file)
            print(f"Deadlines loaded successfully from {DEADLINE_FILE_NAME}.")
            return deadline_list
        else:
            print(f"{DEADLINE_FILE_NAME} not found. Returning an empty list.")
            return []
    except Exception as e:
        print(f"Failed to load deadlines: {e}")
        return []

# Save the alarm list to a file
def save_alarms(alarm_list):
    try:
        with open(ALARM_FILE_NAME, "w") as file:
            ujson.dump(alarm_list, file)
        print(f"Alarms saved successfully to {ALARM_FILE_NAME}.")
    except Exception as e:
        print(f"Failed to save alarms: {e}")

# Load the alarm list from a file
def load_alarms():
    try:
        if ALARM_FILE_NAME in uos.listdir():
            with open(ALARM_FILE_NAME, "r") as file:
                alarm_list = ujson.load(file)
            print(f"Alarms loaded successfully from {ALARM_FILE_NAME}.")
            return alarm_list
        else:
            print(f"{ALARM_FILE_NAME} not found. Returning an empty list.")
            return []
    except Exception as e:
        print(f"Failed to load alarms: {e}")
        return []

# Example deadline list
# deadline_list = [
#     { "id": '1', "name": 'Algorithms Exam', "type": 'Exam', "dateTime": { "year": 2025, "month": 2, "day": 19, "hour": 9, "minute": 0, "second": 0 } },
#     { "id": '2', "name": 'Database Project Submission', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 20, "hour": 23, "minute": 59, "second": 0 } },
#     # Add more items as needed
# ]


