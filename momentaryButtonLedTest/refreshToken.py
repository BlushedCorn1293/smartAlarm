import urequests
import ubinascii
import json
import time
import os
import network

def connectToWifi():
    ssid = 'BT-W9CK8N'
    password = 'yrVNQvM7mquCAq'

    # Set up WiFi connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for the connection
    while not wlan.isconnected():
        time.sleep(1)

    print("Connected to WiFi")
    ip = wlan.ifconfig()[0]
    print("IP Address:", ip)

connectToWifi()

from lib.spotify_auth import SpotifyAuth

def main():
    # Your Spotify app credentials
    CLIENT_ID = 'fa4ef692cad24fe39530ca8c98178070'
    CLIENT_SECRET = 'dc5f925f960245a1a46b0d4ad1d70842'
    REDIRECT_URI = 'http://localhost:8888/callback'
    
    # Create auth handler
    spotify_auth = SpotifyAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    # If we don't have tokens, get initial authorization
    if not spotify_auth.access_token:
        auth_code = "AQBClf6aasPIWu8cpH-HXmWPwI8s90-tZP7mfRsIQUGEClc3Wlj2oqJ1sN8srJEaNC3pJ5yESgA0bF-xUTV4H01BVQqBVcZtSWRt1x7FxSvKtjr9zYoDKZWnu2dWPFEUwaN5Mj8IweEMPKn-_H7YgVwCkn9kCcWhHJxxcHFoouFnXH9AtW0V-t9utpG3LGdTkOWSKia17ip3tCZZcxt_LABt3hwiCJ5LxJxW_HqlbtzRQNHkzljGbw"
        if not spotify_auth.get_initial_tokens(auth_code):
            print("Failed to get initial tokens")
            return
    
    while True:
        token = spotify_auth.get_valid_access_token()
        if token:
            headers = {
                'Authorization': f'Bearer {token}'
            }
            try:
                response = urequests.get(
                    'https://api.spotify.com/v1/me/player',
                    headers=headers
                )
                print(response.json())
            except Exception as e:
                print(f"API call error: {e}")
            finally:
                response.close()
        
        time.sleep(30)

if __name__ == "__main__":
    main()