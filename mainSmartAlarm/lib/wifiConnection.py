import network
import time
import credentials

ip = None

def connect(timeout=60):
    global ip
    ssid = credentials.SSID
    password = credentials.PASSWORD

    # Set up WiFi connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for the connection
    start_time = time.time()
    while not wlan.isconnected():
        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout:
            raise Exception("WiFi connection failed: Timeout exceeded.")
        if int(elapsed_time) % 5 == 0:  # Output every 5 seconds
            print(f"Waiting for WiFi connection... {int(elapsed_time)}s elapsed")
        time.sleep(1)
        
    # Connected successfully
    ip = wlan.ifconfig()[0]
    print("Connected to WiFi")
    print("IP Address:", ip)
    return ip

def getIP():
    global ip
    return ip