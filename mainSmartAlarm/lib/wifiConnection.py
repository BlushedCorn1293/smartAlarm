import network
import time
import credentials

ip = None

def connect():
    global ip
    ssid = credentials.SSID
    password = credentials.PASSWORD

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
    return ip

