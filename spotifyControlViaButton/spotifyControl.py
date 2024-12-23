from machine import Pin, PWM
import urequests
import time

import network
import credentials


import lib.connectToWifi as connectToWifi
connectToWifi.connect()

from lib.spotify_auth import SpotifyAuth

# Spotify API Configuration
CLIENT_ID = credentials.CLIENT_ID
CLIENT_SECRET = credentials.CLIENT_SECRET
REDIRECT_URI = 'http://localhost:8888/callback'

TOKEN_URL = 'https://accounts.spotify.com/api/token'
# ACCESS_TOKEN = 'BQBZ3t589pLSIMSmwMtr1d_A6v1X4Pcq2yFCxfzJylTlUreDqoD7DjtgRmOHnhot-8c7Jh0iwZ-WhPIC8ZpvGgnXAoLZwgTCZUM9cggYtm9aDY5fepof7cm4u8No-Uc8HguQYfOhMdCjZYDZP2Xd_oOZqR6nqgbsphQKR03mN945GiybyIMZl2Rl23RkejEpkw'
global ACCESS_TOKEN
SPOTIFY_ME_URL = 'https://api.spotify.com/v1/me'

SPOTIFY_PAUSE_URL = 'https://api.spotify.com/v1/me/player/pause'
SPOTIFY_PLAY_URL = 'https://api.spotify.com/v1/me/player/play'
SPOTIFY_NEXT_URL = 'https://api.spotify.com/v1/me/player/next'
SPOTIFY_PREVIOUS_URL = 'https://api.spotify.com/v1/me/player/previous'
SPOTIFY_PLAYER_STATE_URL = 'https://api.spotify.com/v1/me/player'

def get_spotify_state():
    """Get the current playback state of the user's Spotify account."""
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    try:
        response = urequests.get(SPOTIFY_PLAYER_STATE_URL, headers=headers)
        
        if response.status_code == 200:
            # Successfully fetched the current playback state
            playback_data = response.json()
            is_playing = playback_data.get('is_playing', False)
            track_name = playback_data['item']['name']
            track_artist = playback_data['item']['artists'][0]['name']
            device_name = playback_data['device']['name']

            print(f"Playback state: {'Playing' if is_playing else 'Paused'}")
            print(f"Currently playing: {track_name} by {track_artist}")
            print(f"Device: {device_name}")
        elif response.status_code == 401:
            # print("Access token expired, refreshing...")
            print("Access token expired")

        else:
            print(f"Error: {response.status_code}, {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")


# def check_token_scopes():
#     """Check if the token has the required scopes."""
#     headers = {
#         'Authorization': f'Bearer {ACCESS_TOKEN}'
#     }
    
#     try:
#         response = urequests.get(SPOTIFY_ME_URL, headers=headers)
        
#         if response.status_code == 200:
#             user_data = response.json()
#             print(f"Authenticated user: {user_data['display_name']}")
#         else:
#             print(f"Error: {response.status_code}, {response.text}")
#     except Exception as e:
#         print(f"Error: {e}")

# check_token_scopes()

SPOTIFY_PLAYER_STATE_URL = 'https://api.spotify.com/v1/me/player'

# def get_spotify_state():
#     """Get the current playback state of the user's Spotify account."""
#     headers = {
#         'Authorization': f'Bearer {ACCESS_TOKEN}'
#     }

#     try:
#         response = urequests.get(SPOTIFY_PLAYER_STATE_URL, headers=headers)
        
#         if response.status_code == 200:
#             # Successfully fetched the current playback state
#             playback_data = response.json()
#             is_playing = playback_data.get('is_playing', False)
#             track_name = playback_data['item']['name']
#             track_artist = playback_data['item']['artists'][0]['name']
#             device_name = playback_data['device']['name']

#             print(f"Playback state: {'Playing' if is_playing else 'Paused'}")
#             print(f"Currently playing: {track_name} by {track_artist}")
#             print(f"Device: {device_name}")
#         elif response.status_code == 401:
#             print("Access token expired, refreshing...")
#             refresh_access_token()  # Refresh the token and try again
#             return get_spotify_state()

#         else:
#             print(f"Error: {response.status_code}, {response.text}")
    
#     except Exception as e:
#         print(f"Error: {e}")

# get_spotify_state()


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
    original_led_value = led.duty_u16()
    if original_led_value == 65535:
        print("LED is on")
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

def main():
    global ACCESS_TOKEN
    # Pin setup
    # led = Pin(9, Pin.OUT)  # GPIO pin connected to your LED
    led = PWM(Pin(9))
    led.freq(1000)
    set_brightness(led, 50)

    button = Pin(28, Pin.IN, Pin.PULL_UP)  # GPIO pin connected to your button

    # Variables
    led_state = False  # Initial LED state
    previous_button_state = True  # Initial button state

    press_count = 0  # Number of button presses
    press_time = 0  # Time of the last press

    spotify_auth = SpotifyAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    # If we don't have tokens, get initial authorization
    if not spotify_auth.access_token:
        print("Please input the Spotify authorization code:")
        print("Click here: https://accounts.spotify.com/authorize?response_type=code&client_id=fa4ef692cad24fe39530ca8c98178070&redirect_uri=http://localhost:8888/callback&scope=user-modify-playback-state%20user-read-playback-state")
        auth_code = input().strip()
        if not spotify_auth.get_initial_tokens(auth_code):
            print("Failed to get initial tokens")
            return

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
            print(response.json())
            if response.status_code == 401:
                print("Please input the Spotify authorization code:")
                print("Click here: https://accounts.spotify.com/authorize?response_type=code&client_id=fa4ef692cad24fe39530ca8c98178070&redirect_uri=http://localhost:8888/callback&scope=user-modify-playback-state%20user-read-playback-state")
                auth_code = input().strip()
                if not spotify_auth.get_initial_tokens(auth_code):
                    print("New access token failed")
                    return
            
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