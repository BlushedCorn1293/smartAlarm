from machine import I2C, Pin
from ds3231 import DS3231
import time
import lib.wifiConnection as wifiConnection
import gpio

# Initialize I2C
i2c = I2C(1, scl=Pin(gpio.rtc_SCL_Pin), sda=Pin(gpio.rtc_SDA_Pin))  # I2C1 on GP27 (SCL) and GP26 (SDA)

# Initialize DS3231
rtc = DS3231(i2c)


def initialSetTime():
    # Connect to WiFi
    ip = wifiConnection.connect()

    # Fetch current time from an API
    current_time = get_current_time_from_API()
    print("Setting RTC to:", current_time)

    # Set the DS3231 time
    rtc.set_time(current_time)

# Fetch current time from WorldTimeAPI
def get_current_time_from_API():
    import urequests
    url = "http://worldtimeapi.org/api/timezone/Etc/UTC"
    response = urequests.get(url)
    data = response.json()
    datetime_str = data['datetime']
    year, month, day = map(int, datetime_str[:10].split('-'))
    hour, minute, second = map(int, datetime_str[11:19].split(':'))
    return (year, month, day, 0, hour, minute, second)

# Run to initially set RTC module
#initialSetTime()

# Print time continuously
while True:
    current_time = rtc.get_time()
    print("Current Time:", current_time)
    time.sleep(1)
