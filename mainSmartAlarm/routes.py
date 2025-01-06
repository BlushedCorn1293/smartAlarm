from phew import server # type: ignore
import machine
import json
import os
import gc
import time
import network
import lib.dataManager as dataManager
import lib.wifiConnection as wifiConnection
ip = wifiConnection.ip


# Load the data from the files
deadline_list = dataManager.load_deadlines()
alarm_list = dataManager.load_alarms()
# Data only loaded once at the start of the program,
# so changes made to the data will be saved to the files
# using the saveAlarms and saveDeadlines functions
# but not reloaded as the data is saved in alarm_list and deadline_list

# The functions to save the data to the files
def saveAlarms(alarm_list):
    dataManager.save_alarms(alarm_list)
def saveDeadlines(deadline_list):
    dataManager.save_deadlines(deadline_list)

# Print the loaded data
print("Loaded Alarms:", alarm_list)
print("Loaded Deadlines:", deadline_list)

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

@server.route("/api/alarms", methods=["GET", "POST"])
def get_alarms(request):
    if request.method == "GET":
        # Return the list of alarms
        return json.dumps({"alarms": alarm_list}), 200, {"Content-Type": "application/json"}

    elif request.method == "POST":
        try:
            # Parse the incoming data from the request (expecting raw data)
            data = request.data
            
            # Initialize the missing_fields list
            missing_fields = []

            # Check for required fields in the incoming data
            if "day" not in data:
                missing_fields.append("Alarm day")
            if "time" not in data or "hour" not in data["time"] or "minute" not in data["time"] or "second" not in data["time"]:
                missing_fields.append("Valid Alarm time with hour, minute, and second")

            # If any required fields are missing, return a 400 error with the missing fields
            if missing_fields:
                return json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400, {"Content-Type": "application/json"}

            # Extract the alarm fields from the request data
            
            alarm_day = data["day"]
            alarm_time = data["time"]
            # Default to True if not provided
            if "isOn" not in data:
                alarm_isOn = True
            else:
                alarm_isOn = data["isOn"]
                
            if "alarm_name" not in data:
                alarm_name = "Alarm"
            else:
                alarm_name = data["name"]
            
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
            saveAlarms(alarm_list)
            # Return the updated alarm list and success message
            return json.dumps({"message": "New alarm added successfully!", "new_alarm": new_alarm}), 200, {"Content-Type": "application/json"}
        
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}

    else:
            return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}
        
@server.route("/api/alarms/<id>", methods=["GET", "PUT","DELETE"])
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

        elif request.method == "PUT":
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
                saveAlarms(alarm_list)
                # Return a success message with the updated alarm
                return json.dumps({"message": "Alarm updated successfully!", "updated_alarm": alarm}), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Alarm not found!"}), 404, {"Content-Type": "application/json"}
        
        elif request.method == "DELETE":
            if alarm:
                # Remove the alarm from the list
                alarm_list.remove(alarm)
                saveAlarms(alarm_list)
                return json.dumps({"message": "Alarm deleted successfully!"}), 200, {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Alarm not found!"}), 404, {"Content-Type": "application/json"}
        
        else:
            return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}

# List all deadlines or create a new deadline
@server.route("/api/deadlines", methods=["GET", "POST"])
def get_deadlines(request):
    if request.method == "GET":
        # Return the list of deadlines
        return json.dumps({"deadlines": deadline_list}), 200, {"Content-Type": "application/json"}

    elif request.method == "POST":
        try:
            # Parse the incoming data from the request (expecting JSON)
            data = request.data

            # Get the deadline details
            deadline_name = data.get("name")
            deadline_type = data.get("type")
            deadline_date_time = data.get("dateTime")

            missing_fields = []

            if not deadline_name:
                missing_fields.append("Alarm name")
            if not deadline_type:
                missing_fields.append("Alarm day")
            if not deadline_date_time:
                missing_fields.append("Alarm time")

            if missing_fields:
                return json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400, {"Content-Type": "application/json"}

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
            saveDeadlines(deadline_list)
            # Return the updated deadline list and success message
            return json.dumps({"message": "New deadline added successfully!", "new_deadline": new_deadline}), 200, {"Content-Type": "application/json"}

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}
    
    else:
        return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}

# Get, update, or delete a specific deadline by id
@server.route("/api/deadlines/<id>", methods=["GET", "PUT", "DELETE"])
def get_deadline_by_id(request, id):
    try:
        # Loop through the deadline_list to find a matching deadline
        matched_deadlines = []
        for deadline in deadline_list:
            if deadline["id"] == id:
                matched_deadlines.append(deadline)

        # Get the first deadline that matches, or None if no match is found
        deadline = matched_deadlines[0] if matched_deadlines else None

        if not deadline:
            return json.dumps({"error": "Deadline not found!"}), 404, {"Content-Type": "application/json"}
        if request.method == "GET":
            return json.dumps(deadline), 200, {"Content-Type": "application/json"}

        elif request.method == "PUT":
            # Parse the JSON data from the request
            updated_data = request.data
            if "name" in updated_data:
                deadline["name"] = updated_data["name"]
            if "type" in updated_data:
                deadline["type"] = updated_data["type"]
            if "dateTime" in updated_data:
                deadline["dateTime"] = updated_data["dateTime"]
            saveDeadlines(deadline_list)
            # Return a success message with the updated deadline
            return json.dumps({"message": "Deadline updated successfully!", "updated_deadline": deadline}), 200, {"Content-Type": "application/json"}

        elif request.method == "DELETE":
            # Remove the deadline from the list
            deadline_list.remove(deadline)
            saveDeadlines(deadline_list)
            return json.dumps({"message": "Deadline deleted successfully!"}), 200, {"Content-Type": "application/json"}
        else:
            return json.dumps({"error": "Method not allowed!"}), 405, {"Content-Type": "application/json"}
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500, {"Content-Type": "application/json"}

@server.route("/api", methods=["GET"])
def get_api_routes(request):
     # Define all available routes and their descriptions
    api_routes = {
        "GET /authorize_spotify": f"http://{ip}/authorize_spotify",
        "POST /authorize_spotify": f"http://{ip}/authorize_spotify",
        "GET /api": f"http://{ip}/api",
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

