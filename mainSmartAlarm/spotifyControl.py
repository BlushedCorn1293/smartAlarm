
import os
from machine import Pin, PWM
import urequests
import time
import network
import credentials
import json
from lib.spotify_auth import SpotifyAuth
import lib.wifiConnection as wifiConnection

# Connect to WiFi and get IP address
ip = wifiConnection.connect()
# Spotify API Configuration
CLIENT_ID = credentials.CLIENT_ID
CLIENT_SECRET = credentials.CLIENT_SECRET
REDIRECT_URI = 'http://localhost:8888/callback'

TOKEN_URL = 'https://accounts.spotify.com/api/token'
global ACCESS_TOKEN
SPOTIFY_ME_URL = 'https://api.spotify.com/v1/me'

SPOTIFY_PAUSE_URL = 'https://api.spotify.com/v1/me/player/pause'
SPOTIFY_PLAY_URL = 'https://api.spotify.com/v1/me/player/play'
SPOTIFY_NEXT_URL = 'https://api.spotify.com/v1/me/player/next'
SPOTIFY_PREVIOUS_URL = 'https://api.spotify.com/v1/me/player/previous'

class RequestType:
    PAUSE = 'PAUSE'
    PLAY = 'PLAY'
    NEXT = 'NEXT'
    PREVIOUS = 'PREVIOUS'

    @classmethod
    def values(cls):
        return [cls.PAUSE, cls.PLAY, cls.NEXT, cls.PREVIOUS]


def send_spotify_request(url):
    """Send a request to Spotify API."""
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'Content-Length': '0' 
    }
    if url == SPOTIFY_PLAY_URL or url == SPOTIFY_PAUSE_URL:
        try:
            response = urequests.put(url, headers=headers)
            print(f"Response: {response.status_code}")
            response.close()
        except Exception as e:
            print(f"Error: {e}")
    else:
        try:
            response = urequests.post(url, headers=headers)
            print(f"Response: {response.status_code}")
            response.close()
        except Exception as e:
            print(f"Error: {e}")

def led_blink(led, num_blinks=1):
    original_led_value = float(led.duty_u16())
    if original_led_value >= 65534:
        led_value = 100
        not_led_value = 0
    else:
        led_value = 0
        not_led_value = 100
    """Blink the LED."""
    for _ in range(num_blinks):
        set_brightness(led, led_value)
        time.sleep(0.2)
        set_brightness(led, not_led_value)
        time.sleep(0.2)
    set_brightness(led, original_led_value)

#input percentage of brightness output actual value
def set_brightness(led, percent):
    brightness = int((percent/100) * 65535)
    led.duty_u16(brightness)


spotify_auth = None
led = None
button = None

# Initialize globals
previous_button_state = True  # Initial button state
press_count = 0  # Number of button presses
press_time = 0  # Time of the last press
spotifyAuthorised = False
led_state = False  # Initial LED state

def set_auth_code(new_access_token):
    global ACCESS_TOKEN
    ACCESS_TOKEN = new_access_token

def reauthorize_spotify(auth_code):
    global spotify_auth
    global ACCESS_TOKEN

    # Get new tokens using the provided auth code
    if not spotify_auth.get_initial_tokens(auth_code):
        print("Failed to get new access tokens.")
        return False

    token = spotify_auth.get_valid_access_token()
    return
        
import os
import json


def load_auth_code():
    """Function to load the auth code from the 'auth_code.json' file."""
    try:
        # Check if the 'auth_code.json' file exists using os.listdir()
        if 'auth_code.json' in os.listdir():
            print("auth_code.json found, attempting to read")
            with open('auth_code.json', 'r') as f:
                # Read and parse the JSON content
                auth_code_data = json.load(f)
                auth_code = auth_code_data.get('auth_code')
                print("auth_code retrieved")
                print("auth code:",auth_code)
                # Return the auth_code if it exists, otherwise return None
                if auth_code:
                    return auth_code
                else:
                    print("No auth_code found in the file.")
                    return None
        else:
            print("'auth_code.json' file does not exist.")
            return None
    except Exception as e:
        # Catch any exceptions and print the error
        print(f"Error loading tokens: {e}")
        return None

spotify_auth

def main():
    global ACCESS_TOKEN
    global spotify_auth
    global CLIENT_ID
    global CLIENT_SECRET
    # Pin setup
    led = PWM(Pin(9))
    led.freq(1000)
    set_brightness(led, 50)

    button = Pin(28, Pin.IN, Pin.PULL_UP)  # GPIO pin connected to your button

    # Variables
    led_state = False  # Initial LED state
    previous_button_state = True  # Initial button state

    press_count = 0  # Number of button presses
    press_time = 0  # Time of the last press

    def check_user_hold_button():
        global spotify_auth
        print("Wating for button hold to restart main()")
        global previous_button_state, press_count, press_time, led_state
        button = Pin(28, Pin.IN, Pin.PULL_UP)  # Configure the button on GPIO28 as input with pull-up

        validAuth=False
        while not validAuth:
            current_button_state = button.value()  # Read the current button state

            # Detect button press (transition from high to low)
            if not current_button_state and previous_button_state:
                press_count += 1  # Increment press count
                press_time = time.ticks_ms()  # Record the time of the press

            # Check for hold if the button is pressed
            if not current_button_state and press_count > 0:  # Only check for hold if the button is pressed
                # If the button is held for more than 300ms
                if time.ticks_diff(time.ticks_ms(), press_time) > 500:
                    led_state = not led_state  # Toggle LED state
                    print("Button held")
                    press_count = 0  # Reset press count after hold detection
                    print("Loading auth_code")
                    auth_code = load_auth_code()
                    spotify_auth.get_initial_tokens(auth_code)
                    if spotify_auth.get_valid_access_token():
                        print("Valid access token")
                        validAuth=True
                    else:
                        print("Invalid access token")

            previous_button_state = current_button_state  # Update previous state for the next iteration

            time.sleep_ms(1000)  # Delay to reduce CPU usage

    
    spotify_auth = SpotifyAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    print("Exisiting spotify access token:",spotify_auth.access_token)
    if not spotify_auth.access_token:
        print("Please input the Spotify authorization code:")
        print("Click here: https://accounts.spotify.com/authorize?response_type=code&client_id=fa4ef692cad24fe39530ca8c98178070&redirect_uri=http://localhost:8888/callback&scope=user-modify-playback-state%20user-read-playback-state")
        print("After authorizing, submit the authorization code to /authorize.")
       
        auth_code = load_auth_code()
        if not auth_code:
            print("No authorization code found.")
            check_user_hold_button()
        if not spotify_auth.get_initial_tokens(auth_code):
            print("Failed to get initial tokens")
            check_user_hold_button()
            
    token = spotify_auth.get_valid_access_token()
    if token:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        print("Getting current player state")
        try:
            response = urequests.get(
                'https://api.spotify.com/v1/me/player',
                headers=headers
            )
            print(f"Status code: {response.status_code}")
            if response.status_code == 204:
                print("No active player found")
            elif response.status_code == 401:
                print("Token expired or invalid")
            elif response.status_code == 429:
                print("Rate limited")
            
            if response.text:
                data = response.json()
                print("Player state:", data)
            # Check if Spotify is currently playing and set LED state
            if response.json().get('is_playing') == True:
                led_state = True
                set_brightness(led, 100)
            else:
                print("Spotify is paused")
                led_state = False
                set_brightness(led, 10)

        except Exception as e:
            print(f"API call error: {e}")
        finally:
            response.close()
    # Signal that the device is ready
    led_blink(led, 3)
    if not led_state:
        set_brightness(led, 10)
    # Main loop
    while True:
        # check token and refresh if needed
        ACCESS_TOKEN = spotify_auth.get_valid_access_token()
        current_button_state = button.value()
        
        if not current_button_state and previous_button_state:
            # Button press detected (button state goes from high to low)
            press_count += 1  # Increment press count
            press_time = time.ticks_ms()  # Record the time of the press

        previous_button_state = current_button_state
        
        # Check for press count after 300ms (to detect double or triple press)
        if time.ticks_diff(time.ticks_ms(), press_time) > 300:
            if press_count == 1:
                # Single press: Play/Pause
                led_state = not led_state  # Toggle LED state

                # Interact with Spotify API
                if led_state:
                    print("Playing Spotify")
                    send_spotify_request(SPOTIFY_PLAY_URL)
                    set_brightness(led, 100)
                else:
                    print("Pausing Spotify")
                    send_spotify_request(SPOTIFY_PAUSE_URL)
                    set_brightness(led, 10)
            elif press_count == 2:
                # Double press: Skip forward
                print("Skipping forward")
                led_blink(led,2)
                send_spotify_request(SPOTIFY_NEXT_URL)
                led_state = True # Spotify automatically plays after skipping forward
                set_brightness(led, 100)
            elif press_count == 3:
                # Triple press: Skip backward
                print("Skipping backward")
                led_blink(led,3)
                send_spotify_request(SPOTIFY_PREVIOUS_URL)
                led_state = True # Spotify automatically plays after skipping backward
                set_brightness(led, 100)

            # Reset press count
            press_count = 0
        
        time.sleep_ms(5)  # Small delay for stability

if __name__ == "__main__":
    main()