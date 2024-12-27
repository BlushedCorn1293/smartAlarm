from phew import server  # Import Phew server
import _thread
import json
import network
import time
import machine
import spotifyControl
import _thread
import os
import lib.wifiConnection as wifiConnection
import utime
from machine import Pin

pins = [
    Pin(16, Pin.OUT), # middle
    Pin(17, Pin.OUT), # top left
    Pin(18, Pin.OUT), # top
    Pin(19, Pin.OUT), # top right
    Pin(13, Pin.OUT), # bottom right
    Pin(14, Pin.OUT), # bottom
    Pin(15, Pin.OUT), # bottom left
    Pin(12, Pin.OUT), # dot
]

# Character mapping
chars = {
    '0': [0, 1, 1, 1, 1, 1, 1, 0],  # Correct segments for 0
    'S': [1, 1, 1, 0, 1, 1, 0, 0],  # Correct segments for S
    'A': [1, 1, 1, 1, 1, 0, 1, 0],  # Correct segments for A
    '-': [1, 0, 0, 0, 0, 0, 0, 0],
}


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

# Connect to WiFi and get IP address
ip = wifiConnection.connect()
current_thread = None
auth_code = None



#while True:
#    display_7_segment('-')
#    time.sleep(2)
#    clear_7_segment()
#    time.sleep(2)

import routes

# This function will be used to kill the existing thread if needed
def kill_current_thread():
    global current_thread
    if current_thread is not None:
        # Not a great way to kill the thread, but we can stop it via global variable
        print("Stopping the existing spotifyControl thread.")
        current_thread = None

# Function to start the Spotify control logic, passing the auth code
def start_spotify_control(auth_code):
    global current_thread
    # Kill any existing spotifyControl thread
    kill_current_thread()
    
    def run_spotify_control():
        # Start the spotifyControl logic, passing the authorization code
        spotifyControl.main(auth_code)  # Continue normal operation after reauthorization
    
    # Start the new spotifyControl thread
    current_thread = _thread.start_new_thread(run_spotify_control, ())

@server.route("/authorize", methods=["GET", "POST"])
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
    print(f"Access API here: http://{ip}/api/")
    server.run()  # Blocking call to run the server

def core0_thread():
    print("Starting web server...")
    start_server()

def core1_thread():
    print("Starting spotify...")
    spotifyControl.main()



def main():
    # Initialize the switch pin
    switch_pin = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP)

    # Function to check the switch state
    def is_switch_on():
        return switch_pin.value() == 0  # Assuming the switch is active low

    # Check the switch state and print it
    if is_switch_on():
        print("Switch is ON (WEB API Mode)")
        display_7_segment('A') # Display 'A' for API mode
        core0_thread()

    else:
        print("Switch is OFF (SPOTIFY API Mode)")
        display_7_segment('S') # Display 'S' for Spotify mode
        #current_thread = _thread.start_new_thread(core1_thread, ())
        core1_thread()

    
if __name__ == "__main__":
    main()