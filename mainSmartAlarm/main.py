from phew import server  # Import Phew server
from picozero import Speaker
import _thread
import json
import network
import time
import machine
import spotifyControl
import _thread
import os
import lib.dataManager as dataManager
import lib.wifiConnection as wifiConnection
import json
import gpio
import credentials
import ssl
from ds3231 import DS3231
from machine import I2C, Pin

LED = gpio.yellowLED
LED.value(1)

# Global variable to track if alarms file was updated
file_modified_flag = False

# Variable to store last modified timestamp of alarms.json
last_modified_time = 0

pins = gpio.sevenSegmentPins
# Character mapping
chars = gpio.sevenSegmentChars

# button = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_UP)  # Button on GPIO pin 14 (active low)
button = gpio.alarmStopButton
# Function to check if the button is pressed

def is_button_pressed():
    return button.value() == 0  # Assuming the button is active low

def clear_7_segment():
    for pin in pins:
        pin.value(0)

def display_7_segment(char):
    clear_7_segment()
    char_pattern = chars.get(char, [])
    # Ensure pattern length matches pins
    if char_pattern is None:
        print(f"Error: Character pattern for '{char}' does not match pin count.")
        return
    
     # Set pin values based on the character pattern
    for pin, state in zip(pins, char_pattern):
        pin.value(state)

clear_7_segment()
display_7_segment('-')

successfullWifiConnection = False
ip = None
# Connect to WiFi and get IP address
try:
    ip = wifiConnection.connect()
    successfullWifiConnection = True
except Exception as e:
    print(e)
current_thread = None
auth_code = None

# Initialize I2C
i2c = I2C(1, scl=Pin(gpio.rtc_SCL_Pin), sda=Pin(gpio.rtc_SDA_Pin))  # I2C1 on GP27 (SCL) and GP26 (SDA)

# Initialize DS3231
rtc = DS3231(i2c)

rtc.set_initial_time(ip)

time.sleep(1)
rtc.turn_off_led()
import routes



@server.route("/authorize_spotify", methods=["GET", "POST"])
def authorize(request):
   global auth_code
   if request.method == "POST":
       try:
           # Get the authorization code from the form data
           auth_code = request.form.get("code", "").strip()

           if not auth_code:
               return "Error: No authorization code provided.", 400

           # Save the authorization code to a Python file
           save_auth_code_to_file(auth_code)

           return "Spotify re-authorization attempt made!", 200
       except Exception as e:
           return f"Error: {e}", 400
   else:
       # Provide instructions for re-authorization
       return """
       <form method="POST">
        <a href="https://accounts.spotify.com/authorize?response_type=code&client_id=fa4ef692cad24fe39530ca8c98178070&redirect_uri=http://localhost:8888/callback&scope=user-modify-playback-state%20user-read-playback-state">Click here to authorize Spotify</a>
        <p>After authorizing, submit the authorization code to /authorize.</p>    
         <label for="code">Enter Spotify Authorization Code:</label>
         <input type="text" id="code" name="code">
         <button type="submit">Submit</button>
       </form>
       """, 200

#Function to save the authorization code to a Python file
def save_auth_code_to_file(auth_code):
   try:
       """Save auth code to file"""
       auth_code_data = {
           'auth_code': auth_code,
       }
       with open('auth_code.json', 'w') as f:
           f.write(json.dumps(auth_code_data))

   except Exception as e:
       print(f"Error saving authorization code to file: {e}")

# Function to start the server
def start_server():
    print(f"Access API here: http://{ip}/api")
    server.run()  # Standard HTTPS port

def web_server_thread():
    print("Starting web server...")
    start_server()

def spotify_thread():
    print("Starting spotify...")
    spotifyControl.main()


# Function to check if the alarms file has been modified
def check_alarms_file():
    global last_modified_time, file_modified_flag
    try:
        current_time = os.stat("alarms.json")[8]  # Last modified time
        if current_time != last_modified_time:
            last_modified_time = current_time
            file_modified_flag = True
            print("Alarms file updated.")
            blinkLED()
    except Exception as e:
        print(f"Error checking alarms file: {e}")
        clear_7_segment()
        display_7_segment('E')

def get_current_time():
    """Get the current time from the RTC as a dictionary."""
    try:
        # Get time from DS3231 RTC
        year, month, day, weekday, hour, minute, second = rtc.get_time()
        return {
            # 'year': year,
            # 'month': month,
            # 'day': day,
            # 'weekday': weekday,
            'hour': hour,
            'minute': minute,
            'second': second
        }
    except Exception as e:
        print(f"Error getting time from RTC: {e}")
        # Fallback to local time if RTC fails
        local_time = time.localtime()
        return {'hour': local_time[3], 'minute': local_time[4], 'second': local_time[5]}

def time_to_seconds(time):
    """Convert a time dictionary to seconds since midnight."""
    return time['hour'] * 3600 + time['minute'] * 60 + time['second']

def seconds_until(alarm_time, current_time):
    """Calculate seconds until a given alarm time from the current time."""
    current_seconds = time_to_seconds(current_time)
    alarm_seconds = time_to_seconds(alarm_time)
    if alarm_seconds >= current_seconds:
        return alarm_seconds - current_seconds
    else:
        # If the alarm time is on the next day
        return (24 * 3600 - current_seconds) + alarm_seconds
    
def wait_until(hour, minute, second):
    """Wait until a specific time (hour, minute, second)."""
    global file_modified_flag
    print(f"Waiting until {hour}:{minute}:{second}...")
    while True:
        if file_modified_flag:
            print("Alarms file updated, stopping wait.")
            return "interrupted"
        
        current_time = get_current_time()
        if (current_time['hour'] == hour and
                current_time['minute'] == minute and
                abs(current_time['second'] - second) <= 5):
                # current_time['second'] == second):
            print("Time reached.")
            return "time reached"
        time.sleep(5)

def append_time_to_txt_file(time, triggerTime):
    try:
        """Append a variable to a text file"""
        file_path = 'times.txt'
        
        # Format the variable as a key=value pair
        entry = f"System time: {time}, What alarm trigger time should be: {triggerTime}\n"
        
        # Open the file in append mode and write the entry
        with open(file_path, 'a') as f:
            f.write(entry)
        
        print(f"Variable time entry added successfully.")
    
    except Exception as e:
        print(f"Error appending variable to file: {e}")



def pick_next_alarm(alarm_list):
    current_time = get_current_time()

    # Filter and sort alarms in the future where isOn is also true
    future_alarms = [
        alarm for alarm in alarm_list
        if seconds_until(alarm['time'], current_time) > 0 and alarm.get('isOn', False) == True
    ]
    future_alarms.sort(key=lambda alarm: seconds_until(alarm['time'], current_time))

    if not future_alarms:
        print("No upcoming alarms.")
        return None

    # Pick the closest future alarm
    next_alarm = future_alarms[0]
    next_alarm_time = next_alarm['time']
    print(f"Next alarm: {next_alarm['name']} at {next_alarm_time['hour']}:{next_alarm_time['minute']}:{next_alarm_time['second']}")
    return next_alarm

def alarm_thread(buzzer):
    global file_modified_flag
    # Load the alarms from the file
    alarm_list = dataManager.load_alarms()
    file_modified_flag = False  # Reset the flag
    while True:
         # If file has been updated, reload the alarms and check the next one
        if file_modified_flag:
            alarm_list = dataManager.load_alarms()
            file_modified_flag = False  # Reset the flag
            print("File updated, checking next alarm...")

        nextAlarm = pick_next_alarm(alarm_list)

        if nextAlarm is None:
            print("No upcoming alarms.")
            wait_until(0, 1, 0)  # Wait until one minute past midnight
            continue
        
        status = wait_until(nextAlarm['time']['hour'], nextAlarm['time']['minute'], nextAlarm['time']['second'])
        print("Wait status:", status)
        if status == "interrupted":
            continue
        
        print("Alarm time reached.")
        # Trigger the buzzer
        print(f"Triggering alarm: {nextAlarm['name']}")
        trigger_buzzer(buzzer)
        print("Alarm cycle completed")

def trigger_buzzer(buzzer):
    print("Starting alarm...")
    
    alarm_start_time = get_current_time()
    timeout_seconds = 2 * 60  # 5 minutes in seconds
    
        
    while not is_button_pressed():
        clear_7_segment()
        # Simple beep pattern
        buzzer.duty_u16(32768)  # 50% duty cycle
        buzzer.freq(262)  # 262 Hz = C4 note
        time.sleep(0.1)
        display_7_segment('8')
        time.sleep(0.1)
        buzzer.duty_u16(0)  # Turn off
        time.sleep(0.2)
        
        # Check timeout
        current_time = get_current_time()
        elapsed_seconds = (
            (current_time['hour'] * 3600 + current_time['minute'] * 60 + current_time['second']) -
            (alarm_start_time['hour'] * 3600 + alarm_start_time['minute'] * 60 + alarm_start_time['second'])
        )

        if elapsed_seconds >= timeout_seconds:
            print("Alarm timeout reached. Turning off automatically.")
            break
        
    print("Alarm turned off!")

def blinkLED(blink_count=5, delay=0.2):
    global LED
    print(f"Blinking LED {blink_count} times with {delay} seconds delay.")
    for _ in range(blink_count):
        LED.value(1)  # Turn LED on
        time.sleep(delay)
        LED.value(0)  # Turn LED off
        time.sleep(delay)

# Timer function to check the alarms file periodically
def file_check_timer(t):
    check_alarms_file()

def main():
    global ip
    global successfullWifiConnection
    global LED
    # Initialize the switch pin
    switch_pin = gpio.modeSwitch
    # Initialize the buzzer
    buzzer = gpio.buzzer
    check_alarms_file() # Check the alarms file initially
    # Set a timer to check the alarms file every 5 minutes
    timer = machine.Timer(-1)
    #timer.init(period=300000, mode=machine.Timer.PERIODIC, callback=file_check_timer)
    timer.init(period=30000, mode=machine.Timer.PERIODIC, callback=file_check_timer)

    LED.value(0)
    print("Alarm mode enabled")
    _thread.start_new_thread(alarm_thread, (buzzer,))


    # Function to check the switch state
    def is_switch_on():
        return switch_pin.value() == 0  # Assuming the switch is active low


    if successfullWifiConnection:
        # Check the switch state and print it
        if is_switch_on():
            # print("Alarm mode enabled")
            # _thread.start_new_thread(alarm_thread, (buzzer,))
            print("Switch is ON (WEB API Mode)")
            display_7_segment('A') # Display 'A' for API mode
            time.sleep(5)
            clear_7_segment()
            web_server_thread()

        else:
            print("Switch is OFF (SPOTIFY API Mode)")
            display_7_segment('S') # Display 'S' for Spotify mode
            time.sleep(5)
            clear_7_segment()
            #current_thread = _thread.start_new_thread(core1_thread, ())
            spotify_thread()
    else:
        display_7_segment('E') # Display 'E' for error
        time.sleep(5)
        clear_7_segment()
    
    # Keep the main thread running always
    while True:
        pass


    
if __name__ == "__main__":
    main()