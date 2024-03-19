import RPi.GPIO as GPIO
import time
import signal
import datetime
import sys
import board
import busio
import adafruit_bh1750
from micropython import const
import os
import numpy as np

class LightController(object):
    """docstring for LightController"""
    def __init__(self, save_data = False, save_mins=1):
        self.save_data = save_data
        self.save_mins = save_mins
        self.last_save = datetime.datetime.now()
        self.current_time = datetime.datetime.now()
        self.filename = "lux.csv"
        self.savedir = "data"

    def __enter__(self):
        signal.signal(signal.SIGTERM, self.safe_exit)
        signal.signal(signal.SIGHUP, self.safe_exit)
        signal.signal(signal.SIGINT, self.safe_exit)
        self.red_pin = 9
        self.green_pin = 11
        # might be white pin if hooking up a white LED here
        self.blue_pin = 10
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.red_pin, GPIO.OUT)
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)

        self.pwm_red = GPIO.PWM(self.red_pin, 500)  # We need to activate PWM on LED so we can dim, use 1000 Hz 
        self.pwm_green = GPIO.PWM(self.green_pin, 500)  
        self.pwm_blue  = GPIO.PWM(self.blue_pin, 500)
        # Start PWM at 0% duty cycle (off)
        self.pwm_red.start(0)
        self.pwm_green.start(0)
        self.pwm_blue.start(0)

        self.pin_zip = zip([self.red_pin, self.green_pin, self.blue_pin], 
            [self.pwm_red, self.pwm_green, self.pwm_blue])

        # light lux target
        self.light_target = 50
        self.light_duty_cycle = 100

        # Config lights on-off cycle here
        # this range is [lights_on, lights_off)
        self.lights_on = 7
        self.lights_off = 19
        
        try:
        # Create library object using our Bus I2C port
            self.i2c_port = board.I2C()
            self.light_sensor = adafruit_bh1750.BH1750(self.i2c_port)
            print("Running light from BH1750 sensor")
        except ValueError:
            print("Light sensor not found")
            sys.exit(1)
        print(f"Initalizing LightController with lights_on: {self.lights_on}h & lights_off: {self.lights_off}h")
        print("------------------------------")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: cleanup GPIO
        print("\nLightController() terminated via __exit__().")

    def change_intensity(self, pwm_object, intensity):
        pwm_object.ChangeDutyCycle(intensity)

    def step(self):
        #for pin, pwm_object in self.pin_zip:
        #   pwm_object.ChangeDutyCycle(100)
        #   time.sleep(10)
        #   pwm_object.ChangeDutyCycle(20)
        #   time.sleep(10)
        #   pwm_object.ChangeDutyCycle(0)
        self.current_time = datetime.datetime.now()
        current_hour = self.current_time.hour
        self.lux = round(self.light_sensor.lux)
        print(f"[{self.current_time.isoformat(' ', timespec='seconds')}] -- {self.lux} lux", end="\r")
        # evaluate between
        # this range is [lights_on, lights_off)
        if self.lights_on <= current_hour < self.lights_off:
            self.pwm_blue.ChangeDutyCycle(self.light_duty_cycle)
            # TODO: implement light modulation to meet target here
        else:
            self.pwm_blue.ChangeDutyCycle(0)
        if self.save_data:    
            if (self.current_time - self.last_save).total_seconds() > self.save_mins * 60:
                    self.write_csv()
                    self.last_save = self.current_time
    def write_csv(self):
        # savedir/year/month/day
        directory = os.path.join(os.getcwd(), self.savedir,
                                 str(self.current_time.year),
                                 str(self.current_time.month).zfill(2),
                                 str(self.current_time.day).zfill(2))
        os.makedirs(directory, exist_ok=True)
        file = os.path.join(directory, self.filename)
        array_to_save = np.array([self.current_time.isoformat(), self.lux]).reshape(1,2)
        print(array_to_save)
        if not os.path.isfile(file):
         with open(file,'a') as csvfile:
             np.savetxt(csvfile, array_to_save,delimiter=',',header='datetime, lux',fmt='%s', comments='')
        else:
            with open(file,'a') as csvfile:
             np.savetxt(csvfile, array_to_save, delimiter=',',fmt='%s', comments='')

    # ------- Safe Exit ---------- #
    def safe_exit(self, signum, frame):
        print("\nLightController() terminated with Ctrl+C.")
        sys.exit(0)

if __name__ == '__main__':
    with LightController(save_data=True, save_mins=0.1) as lights:
        while True:
            lights.step()
            time.sleep(1)