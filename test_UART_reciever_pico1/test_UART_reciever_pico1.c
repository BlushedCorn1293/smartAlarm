#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

// UART defines
// By default the stdout UART is `uart0`, so we will use the second one
#define UART_ID uart0
#define BAUD_RATE 9600

// Use pins 4 and 5 for UART1
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define LED_PIN 14

// Function to read a message from UART
void read_message()
{

    char buffer[128]; // Buffer to store received message
    int index = 0;

    // Read characters from UART until a newline or buffer limit
    while (uart_is_readable(UART_ID))
    {
        char c = uart_getc(UART_ID);
        if (c == '\n' || index >= sizeof(buffer) - 1)
        {
            break;
        }
        buffer[index++] = c;
    }
    buffer[index] = '\0'; // Null-terminate the string

    // If a message was received, print it
    if (index > 0)
    {
        printf("Received: %s\n", buffer);

        gpio_put(LED_PIN, 1);
        sleep_ms(2000);
        gpio_put(LED_PIN, 0);
    }
}

int main()
{
    stdio_init_all();
    printf("Starting...");
    // Set up our UART
    uart_init(UART_ID, BAUD_RATE);
    // Set the TX and RX pins by using the function select on the GPIO
    // Set datasheet for more information on function select
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    // Use some the various UART functions to send out data
    // In a default system, printf will also output via the default UART

    // Send out a string, with CR/LF conversions
    uart_puts(UART_ID, " Hello, UART!\n");

    // For more examples of UART use see https://github.com/raspberrypi/pico-examples/tree/master/uart
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    while (true)
    {
        read_message();       // Read message from UART
        gpio_put(LED_PIN, 1); // Turn LED on
        sleep_ms(300);        // Wait for 500 milliseconds
        gpio_put(LED_PIN, 0); // Turn LED off
        sleep_ms(300);        // Wait for 500 milliseconds
    }
}
