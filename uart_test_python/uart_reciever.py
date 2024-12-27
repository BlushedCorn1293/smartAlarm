from machine import UART

# Initialize UART (UART1: TX=Pin8, RX=Pin9, baudrate=9600)
uart = UART(0, baudrate=9600, tx=0, rx=1)

# Function to read a message
def read_message():
    if uart.any():  # Check if data is available
        message = uart.read().decode('utf-8').strip()  # Read and decode message
        return message
    return None



# Main loop
while True:
    message = read_message()
    if message:
        print(f"Received: {message}")  # Display the received message

