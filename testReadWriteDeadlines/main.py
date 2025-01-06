import ujson
import uos

# File name to store the data
FILE_NAME = "deadlines.json"

# Save the deadline list to a file
def save_deadlines(deadline_list):
    try:
        with open(FILE_NAME, "w") as file:
            ujson.dump(deadline_list, file)
        print(f"Deadlines saved successfully to {FILE_NAME}.")
    except Exception as e:
        print(f"Failed to save deadlines: {e}")

# Load the deadline list from a file
def load_deadlines():
    try:
        if FILE_NAME in uos.listdir():
            with open(FILE_NAME, "r") as file:
                deadline_list = ujson.load(file)
            print(f"Deadlines loaded successfully from {FILE_NAME}.")
            return deadline_list
        else:
            print(f"{FILE_NAME} not found. Returning an empty list.")
            return []
    except Exception as e:
        print(f"Failed to load deadlines: {e}")
        return []

# Example deadline list
deadline_list = [
    { "id": '1', "name": 'Algorithms Exam', "type": 'Exam', "dateTime": { "year": 2025, "month": 2, "day": 19, "hour": 9, "minute": 0, "second": 0 } },
    { "id": '2', "name": 'Database Project Submission', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 20, "hour": 23, "minute": 59, "second": 0 } },
    # Add more items as needed
]

# Save the deadlines to the file
save_deadlines(deadline_list)

# Load the deadlines from the file
loaded_deadlines = load_deadlines()

# Print the loaded deadlines
print("Loaded Deadlines:", loaded_deadlines)
