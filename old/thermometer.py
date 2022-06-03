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


class Thermometer(object):
    """docstring for Thermometer"""
    def __init__(self):
        super(Thermometer, self).__init__()
        # TODO: Check for pixelmix.ttf in folder
        self.drawfont = "pixelmix.ttf"
        self.sleep_secs = 30
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            self.serial = i2c(port=1, address=0x3C)
            self.oled_device = ssd1306(self.serial, rotate=0)
        except DeviceNotFoundError:
            print("I2C mini OLED display not found.")
            sys.exit(1)
        try:
            # Create library object using our Bus I2C port
            #self.i2c_port = busio.I2C(board.SCL, board.SDA)
            #self.temp_sensor = HTU21D(self.i2c_port)
            print("Running temp in debug mode")
        except ValueError:
            print("Temperature sensor not found")
            sys.exit(1)

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def signal_handler(self, sig, frame):
            print("\nThermometer() terminated with Ctrl+C.")
            sys.exit(0)

    def run(self):
        try:
            while True:
                # Measure things
                temp_value = 25
                hum_value = 50
                #temp_value = round(self.temp_sensor.temperature, 1)
                #hum_value = round(self.temp_sensor.relative_humidity, 1)
                # Display results
                with canvas(self.oled_device) as draw:
                    draw.rectangle(self.oled_device.bounding_box, outline="white", fill="black")
                    font = ImageFont.truetype(self.drawfont, 10)
                    ip = self.getIP()
                    draw.text((5, 5), "IP: " + ip, fill="white", font=font)
                    font = ImageFont.truetype(self.drawfont, 12)
                    draw.text((5, 20), f"T: {temp_value} C", fill="white", font=font)
                    draw.text((5, 40), f"H: {hum_value}%", fill="white", font=font)
                # TODO ADD SAVING Here
                time.sleep(self.sleep_secs)
        except SystemExit:
            print("Exiting...")
            sys.exit(0)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit(2)

if __name__ == '__main__':
    thermo = Thermometer()
    thermo.run()
