from phew import server # type: ignore
import machine
import json
import os
import gc
import time
import network

import lib.connectToWifi as connectToWifi
ip = connectToWifi.connect()

led_green = machine.Pin(0, machine.Pin.OUT)
led_red = machine.Pin(1, machine.Pin.OUT)

alarm_list = [
    { "id": '1', "name": 'Exam 1', "day": 1, "time": { "hour": 7, "minute": 0, "second": 0 }, "isOn": True },
    { "id": '2', "name": 'Meeting', "day": 2, "time": { "hour": 9, "minute": 0, "second": 0 }, "isOn": False },
    { "id": '3', "name": 'Lunch Break', "day": 3, "time": { "hour": 12, "minute": 30, "second": 0 }, "isOn": False },
    { "id": '4', "name": 'Gym', "day": 4, "time": { "hour": 18, "minute": 0, "second": 0 }, "isOn": False },
    { "id": '5', "name": 'Dinner', "day": 5, "time": { "hour": 20, "minute": 0, "second": 0 }, "isOn": True },
    { "id": '6', "name": 'Study', "day": 6, "time": { "hour": 21, "minute": 0, "second": 0 }, "isOn": False },
    { "id": '7', "name": 'Meditation', "day": 7, "time": { "hour": 22, "minute": 0, "second": 0 }, "isOn": True },
    { "id": '8', "name": 'Sleep', "day": 1, "time": { "hour": 23, "minute": 0, "second": 0 }, "isOn": True },
    { "id": '9', "name": 'Early Morning Walk', "day": 2, "time": { "hour": 5, "minute": 30, "second": 0 }, "isOn": False },
    { "id": '10', "name": 'Breakfast', "day": 3, "time": { "hour": 7, "minute": 30, "second": 0 }, "isOn": True }
]

deadline_list = [
    { "id": '1', "name": 'Algorithms Exam', "type": 'Exam', "dateTime": { "year": 2025, "month": 2, "day": 19, "hour": 9, "minute": 0, "second": 0 } },
    { "id": '2', "name": 'Database Project Submission', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 20, "hour": 23, "minute": 59, "second": 0 } },
    { "id": '3', "name": 'Operating Systems Exam', "type": 'Exam', "dateTime": { "year": 2025, "month": 2, "day": 21, "hour": 14, "minute": 0, "second": 0 } },
    { "id": '4', "name": 'AI Assignment Submission', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 22, "hour": 17, "minute": 0, "second": 0 } },
    { "id": '5', "name": 'Software Engineering Group Project', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 23, "hour": 12, "minute": 0, "second": 0 } },
    { "id": '6', "name": 'Computer Networks Exam', "type": 'Exam', "dateTime": { "year": 2025, "month": 2, "day": 24, "hour": 10, "minute": 0, "second": 0 } },
    { "id": '7', "name": 'Machine Learning Lab Submission', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 25, "hour": 16, "minute": 0, "second": 0 } },
    { "id": '8', "name": 'Cyber Security Exam', "type": 'Exam', "dateTime": { "year": 2025, "month": 2, "day": 26, "hour": 11, "minute": 0, "second": 0 } },
    { "id": '9', "name": 'Data Science Project Presentation', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 27, "hour": 13, "minute": 0, "second": 0 } },
    { "id": '10', "name": 'Final Year Project Report', "type": 'Coursework', "dateTime": { "year": 2025, "month": 2, "day": 28, "hour": 23, "minute": 59, "second": 0 } }
]

@server.route("/api/temperature", methods=["GET","POST"])
def get_temperature(request):
    adc = machine.ADC(4)  # Use ADC pin GP4
    conversion_factor = 3.3 / (65535)  # ADC conversion factor
    sensor_value = adc.read_u16() * conversion_factor
    temperature = 27 - (sensor_value - 0.706) / 0.001721  # Convert sensor value to temperature (formula may vary)
    
    return json.dumps({"temperature" : temperature}), 200, {"Content-Type": "application/json"}

@server.route("/api/voltage", methods=["GET"])
def get_voltage(request):
    # System voltage (using internal ADC to measure the 3.3V rail)
    adc = machine.ADC(28)  # GP28 pin tied to the 3.3V rail
    conversion_factor = 3.3 / 65535  # ADC conversion factor for 3.3V
    voltage = adc.read_u16() * conversion_factor  # Read the voltage

    system_info = {
        "voltage": voltage,
    }

    return json.dumps(system_info), 200, {"Content-Type": "application/json"}

@server.route("/api/memory_usage", methods=["GET"])
def get_memory_usage(request):
    gc.collect()  # Force garbage collection
    free_memory = gc.mem_free()  # Get free memory
    total_memory = gc.mem_alloc()  # Get total memory allocated
    memory_usage = {
        "free_memory": free_memory,
        "total_memory": total_memory,
    }
    return json.dumps(memory_usage), 200, {"Content-Type": "application/json"}

@server.route("/api/uptime", methods=["GET"])
def get_uptime(request):
    uptime_seconds = time.ticks_ms() // 1000  # Uptime in seconds
    uptime_info = {
        "uptime_seconds": uptime_seconds,
    }
    return json.dumps(uptime_info), 200, {"Content-Type": "application/json"}

@server.route("/api/environment", methods=["GET"])
def get_environment(request):
    adc = machine.ADC(machine.Pin(15))  # Use ADC pin GP15 for photoresistor
    conversion_factor = 3.3 / (65535)  # ADC conversion factor
    sensor_value = adc.read_u16() * conversion_factor
    light_intensity = sensor_value / 3.3 * 100  # Convert sensor value to light intensity percentage
    env_data = {
        "light_intensity": light_intensity,
    }
    return json.dumps(env_data), 200, {"Content-Type": "application/json"}

@server.route("/api/network_status", methods=["GET"])
def get_network_status(request):
    wlan = network.WLAN(network.STA_IF)  # For Wi-Fi interface
    wlan.active(True)
    if wlan.isconnected():
        network_info = {
            "status": "connected",
            "ip_address": wlan.ifconfig()[0],  # Get IP address
            "ssid": wlan.config('essid'),  # Get SSID
        }
    else:
        network_info = {
            "status": "disconnected",
        }
    return json.dumps(network_info), 200, {"Content-Type": "application/json"}

# @server.route("/api/control-led", methods=["POST"])
# def ledCommand(request):
#     led_red.value(request.data["ledRed"])
#     led_green.value(request.data["ledGreen"])
#     return json.dumps({"message" : "Command sent successfully!"}), 200, {"Content-Type": "application/json"}

@server.route("/api/alarms", methods=["GET", "PUT"])
def get_alarms(request):
    if request.method == "GET":
        # Return the list of alarms
        return json.dumps({"alarms": alarm_list}), 200, {"Content-Type": "application/json"}

    elif request.method == "PUT":
        try:
            # Parse the incoming data from the request (expecting JSON)
            data = request.data

            # Get the alarm to be updated
            alarm_name = data.get("name")
            alarm_day = data.get("day")
            alarm_time = data.get("time")
            alarm_isOn = data.get("isOn")

            if not alarm_name or not alarm_day or not alarm_time:
                return json.dumps({"error": "Alarm name, day, and time are required"}), 400, {"Content-Type": "application/json"}

            # Generate a new ID by incrementing the current max ID in the alarm_list
            # Assuming the id is a string of numbers, and they are sequential (1, 2, 3, etc.)
            new_id = str(max(int(alarm["id"]) for alarm in alarm_list) + 1)  # Generate a new unique id

            # Create a new alarm object
            new_alarm = {
                "id": new_id,
                "name": alarm_name,
                "day": alarm_day,
                "time": alarm_time,
                "isOn": alarm_isOn
            }

            # Add the new alarm to the list
            alarm_list.append(new_alarm)

            # Return the updated alarm list and success message
            return json.dumps({"message": "New alarm added successfully!", "new_alarm": new_alarm}), 200, {"Content-Type": "application/json"}

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}
    
    else:
            return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}
        
@server.route("/api/alarms/<id>", methods=["GET", "POST","DELETE"])
def get_alarm_by_id(request, id):
    try:
        # Loop through the alarm_list to find a matching alarm
        matched_alarms = []
        for alarm in alarm_list:
            if alarm["id"] == id:
                matched_alarms.append(alarm)

        # Get the first alarm that matches, or None if no match is found
        alarm = matched_alarms[0] if matched_alarms else None

        if request.method == "GET":
            if alarm:
                return json.dumps(alarm), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Alarm not found!"}), 404, {"Content-Type": "application/json"}

        elif request.method == "POST":
            if alarm:
                # Parse the JSON data from the request
                updated_data = request.data
                if "name" in updated_data:
                    alarm["name"] = updated_data["name"]
                if "day" in updated_data:
                    alarm["day"] = updated_data["day"]
                if "time" in updated_data:
                    alarm["time"] = updated_data["time"]
                if "isOn" in updated_data:
                    alarm["isOn"] = updated_data["isOn"]

                # Return a success message with the updated alarm
                return json.dumps({"message": "Alarm updated successfully!", "updated_alarm": alarm}), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Alarm not found!"}), 404, {"Content-Type": "application/json"}
        
        elif request.method == "DELETE":
            if alarm:
                # Remove the alarm from the list
                alarm_list.remove(alarm)
                return json.dumps({"message": "Alarm deleted successfully!"}), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Alarm not found!"}), 404, {"Content-Type": "application/json"}
        
        else:
            return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}

# List all deadlines or create a new deadline
@server.route("/api/deadlines", methods=["GET", "PUT"])
def get_deadlines(request):
    if request.method == "GET":
        # Return the list of deadlines
        return json.dumps({"deadlines": deadline_list}), 200, {"Content-Type": "application/json"}

    elif request.method == "PUT":
        try:
            # Parse the incoming data from the request (expecting JSON)
            data = request.data

            # Get the deadline details
            deadline_name = data.get("name")
            deadline_type = data.get("type")
            deadline_date_time = data.get("dateTime")

            if not deadline_name or not deadline_type or not deadline_date_time:
                return json.dumps({"error": "Deadline name, type, and dateTime are required"}), 400, {"Content-Type": "application/json"}

            # Generate a new ID by incrementing the current max ID in the deadline_list
            new_id = str(max(int(deadline["id"]) for deadline in deadline_list) + 1)  # Generate a new unique id

            # Create a new deadline object
            new_deadline = {
                "id": new_id,
                "name": deadline_name,
                "type": deadline_type,
                "dateTime": deadline_date_time
            }

            # Add the new deadline to the list
            deadline_list.append(new_deadline)

            # Return the updated deadline list and success message
            return json.dumps({"message": "New deadline added successfully!", "new_deadline": new_deadline}), 200, {"Content-Type": "application/json"}

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}
    
    else:
        return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}

# Get, update, or delete a specific deadline by id
@server.route("/api/deadlines/<id>", methods=["GET", "POST", "DELETE"])
def get_deadline_by_id(request, id):
    try:
        # Loop through the deadline_list to find a matching deadline
        matched_deadlines = []
        for deadline in deadline_list:
            if deadline["id"] == id:
                matched_deadlines.append(deadline)

        # Get the first deadline that matches, or None if no match is found
        deadline = matched_deadlines[0] if matched_deadlines else None

        if request.method == "GET":
            if deadline:
                return json.dumps(deadline), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Deadline not found!"}), 404, {"Content-Type": "application/json"}

        elif request.method == "POST":
            if deadline:
                # Parse the JSON data from the request
                updated_data = request.data
                if "name" in updated_data:
                    deadline["name"] = updated_data["name"]
                if "type" in updated_data:
                    deadline["type"] = updated_data["type"]
                if "dateTime" in updated_data:
                    deadline["dateTime"] = updated_data["dateTime"]

                # Return a success message with the updated deadline
                return json.dumps({"message": "Deadline updated successfully!", "updated_deadline": deadline}), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Deadline not found!"}), 404, {"Content-Type": "application/json"}
        
        elif request.method == "DELETE":
            if deadline:
                # Remove the deadline from the list
                deadline_list.remove(deadline)
                return json.dumps({"message": "Deadline deleted successfully!"}), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Deadline not found!"}), 404, {"Content-Type": "application/json"}
            
        else:
            return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}

@server.route("/api/", methods=["GET"])
def get_api_routes(request):
     # Define all available routes and their descriptions
    api_routes = {
        "GET /api/": f"http://{ip}/api/",
        "GET /api/temperature": f"http://{ip}/api/temperature",
        "GET /api/voltage": f"http://{ip}/api/voltage",
        "GET /api/memory_usage": f"http://{ip}/api/memory_usage",
        "GET /api/uptime": f"http://{ip}/api/uptime",
        "GET /api/environment": f"http://{ip}/api/environment",
        "GET /api/network_status": f"http://{ip}/api/network_status",
        "GET /api/alarms": f"http://{ip}/api/alarms",
        "PUT /api/alarms": f"http://{ip}/api/alarms",
        "GET /api/alarms/<id>": f"http://{ip}/api/alarms/{{id}}",
        "POST /api/alarms/<id>": f"http://{ip}/api/alarms/{{id}}",
        "DELETE /api/alarms/<id>": f"http://{ip}/api/alarms/{{id}}",
        "GET /api/deadlines": f"http://{ip}/api/deadlines",
        "PUT /api/deadlines": f"http://{ip}/api/deadlines",
        "GET /api/deadlines/<id>": f"http://{ip}/api/deadlines/{{id}}",
        "POST /api/deadlines/<id>": f"http://{ip}/api/deadlines/{{id}}",
        "DELETE /api/deadlines/<id>": f"http://{ip}/api/deadlines/{{id}}"
    }

    # Add system voltage to the response
    system_info = {
        "api_routes": api_routes
    }

    return json.dumps(system_info), 200, {"Content-Type": "application/json"}

@server.catchall()
def catchall(request):
    return json.dumps({"message" : "URL not found!"}), 404, {"Content-Type": "application/json"}


print(f"Access api here: http://{ip}/api/")
server.run()
