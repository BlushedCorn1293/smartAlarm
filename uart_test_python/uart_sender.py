from machine import UART
import time

# Initialize UART (UART1: TX=Pin8, RX=Pin9, baudrate=9600)
uart = UART(0, baudrate=9600, tx=0, rx=1)

# Function to send a message
def send_message(message):
    uart.write(message + '\n')  # Send message with newline

# Main loop
while True:
    message = "Hello from UART Sender!"  # Message to send
    print(f"Sending: {message}")
    send_message(message)
    time.sleep(2)  # Wait 2 seconds before sending the next message
