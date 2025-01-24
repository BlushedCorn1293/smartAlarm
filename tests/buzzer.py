from picozero import Speaker
import time
import machine

buzzer = Speaker(22)
button = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_UP)  # Button on GPIO pin 14 (active low)

# Function to check if the button is pressed
def is_button_pressed():
    return button.value() == 0  # Assuming the button is active low

print("Starting alarm...")
while True:
    if is_button_pressed():  # If button is pressed, stop the alarm
        print("Button pressed! Turning off the alarm.")
        break  # Exit the alarm loop
    # Play buzzer sound
    buzzer.play(262, 0.1)  # 262 Hz = C4 note, 0.1 seconds
    time.sleep(0.1)  # Small pause between notes
    buzzer.play(262, 0.6)  # 262 Hz = C4 note, 0.6 seconds
    time.sleep(0.8)  # Pause between repetitions

print("Alarm turned off!")