from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from luma.core.error import DeviceNotFoundError
import os
import time
import signal
import sys
import socket
from PIL import ImageFont, ImageDraw


# adafruit 
import board
import busio
from adafruit_htu21d import HTU21D

# data and saving
import os
import numpy as np
import datetime

class Thermometer(object):
    def __init__(self, save_data=False, save_mins=1):
        """Initialize the Thermometer with basic configuration."""
        self.save_data = save_data
        self.save_mins = save_mins
        self.filename = "temp_hum.csv"
        self.savedir = "data"
        self.drawfont = "pixelmix.ttf"
        self.sleep_secs = 30

        # Initial setup that does not involve hardware resources
        # can be done here.

    def __enter__(self):
        """Setup hardware resources and prepare the device."""
        self.i2c_port = busio.I2C(board.SCL, board.SDA)
        try:
            self.temp_sensor = HTU21D(self.i2c_port)
            print("HTU21D sensor initialized")
        except ValueError:
            print("Temperature sensor not found.")
            sys.exit(1)

        try:
            self.serial = i2c(port=1, address=0x3C)
            self.oled_device = ssd1306(self.serial, rotate=0)
            print("OLED display initialized")
        except DeviceNotFoundError:
            print("I2C mini OLED display not found.")
            sys.exit(1)

        self.last_save = datetime.datetime.now()
        self.current_time = datetime.datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)
        # Additional setup can be performed here.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources here."""
        print("\nThermometer() via __exit__()")
        print("Cleaning up resources.")
        # Cleanup for OLED display
        if hasattr(self, 'oled_device') and self.oled_device:
            self.oled_device.cleanup()
            print("OLED display cleaned up.")
        # Reset HTU21D sensor object
        if hasattr(self, 'temp_sensor'):
            self.temp_sensor = None
        # Reset any signal handlers to default behavior
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def signal_handler(self, sig, frame):
            print("\nThermometer() terminated with Ctrl+C.")
            sys.exit(0)

    def restart_oled(self):
        """Reinitialize the OLED display."""
        try:
            self.serial = i2c(port=1, address=0x3C)
            self.oled_device = ssd1306(self.serial, rotate=0)
            print("OLED display reinitialized.")
        except:
            print("Failed to reinitialize I2C mini OLED display.")
            print("Unexpected error:", sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(sys.exc_info()[2])
            # do not exit!
            #sys.exit(2)

    def measure(self):
        """Measure temperature and humidity."""
        try:
            self.temp_value = round(self.temp_sensor.temperature, 1)
            self.temp_value_f = round(self.temp_value * 9/5 + 32, 1)  # C to F conversion
            self.hum_value = round(self.temp_sensor.relative_humidity, 1)
        except Exception as e:
            print(f"Error measuring temperature/humidity: {e}")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(sys.exc_info()[2])

    def report(self):
        """Update the display with the latest measurements."""
        try:
            with canvas(self.oled_device) as draw:
                draw.rectangle(self.oled_device.bounding_box, outline="white", fill="black")
                font = ImageFont.truetype(self.drawfont, 10)
                ip = self.getIP()
                draw.text((5, 5), "IP: " + ip, fill="white", font=font)
                font = ImageFont.truetype(self.drawfont, 10)
                draw.text((5, 20), f"T: {self.temp_value} C -- {self.temp_value_f} F", fill="white", font=font)
                draw.text((5, 40), f"H: {self.hum_value}%", fill="white", font=font)
        except Exception as e:
            print(f"{self.current_time.isoformat(' ', timespec='seconds')} Error updating display: {e}")
            print(f"Trying to restart display")
            self.restart_oled()

    def write_csv(self):
        # savedir/year/month/day
        directory = os.path.join(os.getcwd(), self.savedir,
                                 str(self.current_time.year),
                                 str(self.current_time.month).zfill(2),
                                 str(self.current_time.day).zfill(2))
        os.makedirs(directory, exist_ok=True)
        file = os.path.join(directory, self.filename)
        array_to_save = np.array([self.current_time.isoformat(), self.temp_value, self.hum_value]).reshape(1,3)
        print(array_to_save)
        if not os.path.isfile(file):
         with open(file,'a') as csvfile:
             np.savetxt(csvfile, array_to_save,delimiter=',',header='datetime, temp, hum',fmt='%s', comments='')
        else:
            with open(file,'a') as csvfile:
             np.savetxt(csvfile, array_to_save, delimiter=',',fmt='%s', comments='')


    def save(self):
        """Save the data to a CSV file if required."""
        if (self.current_time - self.last_save).total_seconds() > self.save_mins * 60:
            self.write_csv()
            self.last_save = self.current_time

    def step(self):
        self.current_time = datetime.datetime.now()
        self.measure()
        self.report()
        if self.save_data:
            self.save()


if __name__ == '__main__':
    with Thermometer(save_data=True, save_mins=0.1) as temp:
        while True:
            temp.step()
            time.sleep(1)
