import machine
from picozero import Speaker

from machine import Pin, PWM

# Enter button GPIO pin values:
alarmStopButtonPin = 
buzzerPin = 
modeSwitchPin = 
yellowLED_Pin = 
spotifyControlButtonPin_LED = 
spotifyControlButtonPin = 
rtc_SCL_Pin = 
rtc_SDA_Pin = 

alarmStopButton = machine.Pin(alarmStopButtonPin, machine.Pin.IN, machine.Pin.PULL_UP)  # Button on GPIO pin 14 (active low)
buzzer = machine.PWM(buzzerPin)
buzzer.duty_u16(0) # Turn off buzzer
modeSwitch = machine.Pin(modeSwitchPin, machine.Pin.IN, machine.Pin.PULL_UP)
spotifyControlButton = Pin(spotifyControlButtonPin, Pin.IN, Pin.PULL_UP)  # GPIO pin connected to your button
spotifyControlButton_LED = PWM(Pin(spotifyControlButtonPin_LED))
yellowLED = machine.Pin(yellowLED_Pin, machine.Pin.OUT)

# Seven segment display pins
sevenSegmentPins = [
    Pin(16, Pin.OUT), # middle
    Pin(17, Pin.OUT), # top left
    Pin(18, Pin.OUT), # top
    Pin(19, Pin.OUT), # top right
    Pin(13, Pin.OUT), # bottom right
    Pin(14, Pin.OUT), # bottom
    Pin(15, Pin.OUT), # bottom left
    Pin(12, Pin.OUT), # dot
]
# Character mapping for seven segment display
sevenSegmentChars = {
    '0': [0, 1, 1, 1, 1, 1, 1, 0],  # Segments for 0
    'S': [1, 1, 1, 0, 1, 1, 0, 0],  # Segments for S
    'A': [1, 1, 1, 1, 1, 0, 1, 0],  # Segments for A
    '-': [1, 0, 0, 0, 0, 0, 0, 0],  # Segments for -
    '!': [0, 0, 0, 1, 1, 0, 0, 1],  # Segments for !
    '8': [1, 1, 1, 1, 1, 1, 1, 0],  # Segments for 8
    'E': [1, 1, 1, 0, 0, 1, 1, 0],  # Segments for E
}
