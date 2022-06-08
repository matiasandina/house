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
    """docstring for Thermometer"""
    def __init__(self, save_data = False, save_mins=1):
        self.save_data = save_data
        self.save_mins = save_mins
    def __enter__(self):
        self.drawfont = "pixelmix.ttf"
        self.sleep_secs = 30
        self.last_save = datetime.datetime.now()
        self.current_time = datetime.datetime.now()
        self.filename = "temp_hum.csv"
        self.savedir = "data"
        # Create library object using our Bus I2C port
        self.i2c_port = busio.I2C(board.SCL, board.SDA)
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            # screen connected to first of the first 3 slots on hat
            self.serial = i2c(port=1, address=0x3C)
            self.oled_device = ssd1306(self.serial, rotate=0)
        except DeviceNotFoundError:
            print("I2C mini OLED display not found.")
            sys.exit(1)
        try:
            self.temp_sensor = HTU21D(self.i2c_port)
            print("Running temp/hum from HTU21D sensor")
        except ValueError:
            print("Temperature sensor not found")
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Cleanup the i2c/ssd devices
        print("\nThermometer() via __exit__()")

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def signal_handler(self, sig, frame):
            print("\nThermometer() terminated with Ctrl+C.")
            sys.exit(0)

    def step(self):
        try:
            # Measure things
            self.temp_value = round(self.temp_sensor.temperature, 1)
            self.hum_value = round(self.temp_sensor.relative_humidity, 1)
            self.current_time = datetime.datetime.now()
            # Display results
            with canvas(self.oled_device) as draw:
                draw.rectangle(self.oled_device.bounding_box, outline="white", fill="black")
                font = ImageFont.truetype(self.drawfont, 10)
                ip = self.getIP()
                draw.text((5, 5), "IP: " + ip, fill="white", font=font)
                font = ImageFont.truetype(self.drawfont, 10)
                draw.text((5, 20), f"T: {self.temp_value} C", fill="white", font=font)
                draw.text((5, 40), f"H: {self.hum_value}%", fill="white", font=font)
            if self.save_data:
                if (self.current_time - self.last_save).total_seconds() > self.save_mins * 60:
                    self.write_csv()
                    self.last_save = self.current_time
        except SystemExit:
            print("Exiting...")
            sys.exit(0)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(sys.exc_info()[2])
            # do not exit!
            #sys.exit(2)
    
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

if __name__ == '__main__':
    with Thermometer(save_data=True, save_mins=0.1) as temp:
        while True:
            temp.step()
            time.sleep(1)
