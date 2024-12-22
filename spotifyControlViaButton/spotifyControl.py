from machine import Pin
import urequests
import time

import network
import credentials


import lib.connectToWifi as connectToWifi
connectToWifi.connect()


# Spotify API Configuration
# TOKEN_URL = 'https://accounts.spotify.com/authorize?response_type=code&client_id=fa4ef692cad24fe39530ca8c98178070&redirect_uri=http://localhost:8888/callback&scope=user-modify-playback-state%20user-read-playback-state'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
ACCESS_TOKEN = 'BQBZ3t589pLSIMSmwMtr1d_A6v1X4Pcq2yFCxfzJylTlUreDqoD7DjtgRmOHnhot-8c7Jh0iwZ-WhPIC8ZpvGgnXAoLZwgTCZUM9cggYtm9aDY5fepof7cm4u8No-Uc8HguQYfOhMdCjZYDZP2Xd_oOZqR6nqgbsphQKR03mN945GiybyIMZl2Rl23RkejEpkw'
SPOTIFY_ME_URL = 'https://api.spotify.com/v1/me'


# Replace 'your_access_token_here' with the token obtained manually
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

# get_spotify_state()

def refresh_access_token():
    return None
    # """Request a new access token using the refresh token."""
    # global ACCESS_TOKEN
    
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded',
    # }
    
    # body = {
    #     'grant_type': 'refresh_token',
    #     'refresh_token': REFRESH_TOKEN,
    #     'client_id': credentials.CLIENT_ID,  # Replace with your Spotify client ID
    #     'client_secret': credentials.CLIENT_SECRET,  # Replace with your Spotify client secret
    # }
    
    # try:
    #     response = urequests.post(TOKEN_URL, headers=headers, data=body)
        
    #     if response.status_code == 200:
    #         data = response.json()
    #         ACCESS_TOKEN = data['access_token']
    #         print("Access token refreshed successfully!")
    #     else:
    #         print(f"Error refreshing token: {response.status_code}")
        
    #     response.close()

    # except Exception as e:
    #     print(f"Error refreshing token: {e}")

def check_token_scopes():
    """Check if the token has the required scopes."""
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    
    try:
        response = urequests.get(SPOTIFY_ME_URL, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Authenticated user: {user_data['display_name']}")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error: {e}")

check_token_scopes()

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
            print("Access token expired, refreshing...")
            refresh_access_token()  # Refresh the token and try again
            return get_spotify_state()

        else:
            print(f"Error: {response.status_code}, {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")

get_spotify_state()



# Spotify API Configuration
# Replace 'your_access_token_here' with the token obtained manually
ACCESS_TOKEN = 'BQB3WZqkdBaRQeWsKILk9CWUyOcfwPy8DpI123R3iLDLC67tNm55WJhscH0bmzYg29wIkexrOevMhKIXeobczrzg5WCWKRQRk-5sFvZDogHm9hGRt7zn_qhP4CQnVO3wqhbWuFa2ExVlU1gGzs1TFt8ADWobG6CEIUZpw1OYf0He6jcMHi99odre0aju0XIIFQ'
SPOTIFY_PAUSE_URL = 'https://api.spotify.com/v1/me/player/pause'
SPOTIFY_PLAY_URL = 'https://api.spotify.com/v1/me/player/play'
SPOTIFY_NEXT_URL = 'https://api.spotify.com/v1/me/player/next'
SPOTIFY_PREVIOUS_URL = 'https://api.spotify.com/v1/me/player/previous'


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

def led_blink(num_blinks=1):
    led_value = led.value()
    not_led_value = not led_value
    """Blink the LED."""
    for _ in range(num_blinks):
        led.value(not_led_value)
        time.sleep(0.2)
        led.value(led_value)
        time.sleep(0.2)
    led.value(led_value)


# Pin setup
led = Pin(9, Pin.OUT)  # GPIO pin connected to your LED
button = Pin(28, Pin.IN, Pin.PULL_UP)  # GPIO pin connected to your button

# Variables
led_state = False  # Initial LED state
previous_button_state = True  # Initial button state

press_count = 0  # Number of button presses
press_time = 0  # Time of the last press

while True:
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
            led.value(led_state)  # Update LED output

            # Interact with Spotify API
            if led_state:
                print("Playing Spotify")
                send_spotify_request(SPOTIFY_PLAY_URL)
            else:
                print("Pausing Spotify")
                send_spotify_request(SPOTIFY_PAUSE_URL)
        elif press_count == 2:
            # Double press: Skip forward
            print("Skipping forward")
            led_blink(2)
            send_spotify_request(SPOTIFY_NEXT_URL)
        elif press_count == 3:
            # Triple press: Skip backward
            print("Skipping backward")
            led_blink(3)
            send_spotify_request(SPOTIFY_PREVIOUS_URL)

        # Reset press count
        press_count = 0
    
    time.sleep_ms(5)  # Small delay for stability

