import utime
import wifiConnection

class DS3231:
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.address = address

    def _bcd_to_dec(self, bcd):
        return (bcd & 0x0F) + ((bcd >> 4) * 10)

    def _dec_to_bcd(self, dec):
        return (dec // 10 << 4) | (dec % 10)

    def get_time(self):
        data = self.i2c.readfrom_mem(self.address, 0x00, 7)
        seconds = self._bcd_to_dec(data[0])
        minutes = self._bcd_to_dec(data[1])
        hours = self._bcd_to_dec(data[2])
        day = self._bcd_to_dec(data[3])
        date = self._bcd_to_dec(data[4])
        month = self._bcd_to_dec(data[5] & 0x1F)
        year = self._bcd_to_dec(data[6]) + 2000
        return year, month, date, day, hours, minutes, seconds

    def set_time(self, datetime_tuple):
        year, month, date, day, hours, minutes, seconds = datetime_tuple
        data = bytearray([
            self._dec_to_bcd(seconds),
            self._dec_to_bcd(minutes),
            self._dec_to_bcd(hours),
            self._dec_to_bcd(day),
            self._dec_to_bcd(date),
            self._dec_to_bcd(month),
            self._dec_to_bcd(year - 2000)
        ])
        self.i2c.writeto_mem(self.address, 0x00, data)

    # Fetch current time from WorldTimeAPI
    def set_initial_time(self):

        ip = wifiConnection.getIP()

        def get_time_from_api():
            import urequests
            try:
                url = "http://worldtimeapi.org/api/timezone/Etc/UTC"
                response = urequests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    datetime_str = data['datetime']
                    year, month, day = map(int, datetime_str[:10].split('-'))
                    hour, minute, second = map(int, datetime_str[11:19].split(':'))
                    response.close()  # Close the response to free memory
                    return (year, month, day, 0, hour, minute, second)
                else:
                    print(f"Error: API returned status code {response.status_code}")
                    response.close()
            except Exception as e:
                print(f"Error fetching time from API: {e}")
            return None  # Return None if an error occurred
        
        # Ensure the Pico is connected to WiFi before fetching the time
        if ip:
            print(f"Connected to WiFi, IP: {ip}")
            # Fetch current time from the API
            current_time = get_time_from_api()
            if current_time:
                print("Setting RTC to:", current_time)
                # Set the DS3231 time
                self.set_time(current_time)
            else:
                print("Failed to fetch time from API.")
        else:
            print("Error: Not connected to WiFi, cannot fetch time from API.")

    def turn_off_led(self):
        # Register address for the status register
        STATUS_REGISTER = 0x0F
        
        # Read current status register
        current_status = self.i2c.readfrom_mem(self.address, STATUS_REGISTER, 1)[0]
        print("Current status register:", bin(current_status))
        
        # Mask the bits related to the alarm output (A1 and A2)
        # Setting the A1 and A2 bits to 0 will turn off the LED
        new_status = current_status & 0x7F  # Clear the A1 and A2 bits
        print("New status register after masking:", bin(new_status))
        
        # Write the new status back to the DS3231
        self.i2c.writeto_mem(self.address, STATUS_REGISTER, bytes([new_status]))
        print("RTC LED turned off.")

    

        
