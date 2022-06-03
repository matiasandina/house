import RPi.GPIO as GPIO
import time
import signal
import datetime
import sys

class LightController(object):
	"""docstring for LightController"""
	def __init__(self):
		super(LightController, self).__init__()
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

		# Config lights on-off cycle here
		self.lights_on = 7
		self.lights_off = 19
		
		print(f"Initalizing LightController with lights_on: {self.lights_on}h & lights_off: {self.lights_off}h")
		print("------------------------------")

	def change_intensity(self, pwm_object, intensity):
		pwm_object.ChangeDutyCycle(intensity)

	def run(self):
		while True:
			#for pin, pwm_object in self.pin_zip:
			#	pwm_object.ChangeDutyCycle(100)
			#	time.sleep(10)
			#	pwm_object.ChangeDutyCycle(20)
			#	time.sleep(10)
			#	pwm_object.ChangeDutyCycle(0)
			current_hour = datetime.datetime.now().hour
			# evaluate between
			if self.lights_on <= current_hour <= self.lights_off:
				self.pwm_blue.ChangeDutyCycle(100)
			else:
				self.pwm_blue.ChangeDutyCycle(0)
			# run this once a second
			time.sleep(1)

	# ------- Safe Exit ---------- #
	def safe_exit(self, signum, frame):
		print("\nLightController() terminated with Ctrl+C.")
		sys.exit(0)

if __name__ == '__main__':
	controller = LightController()
	controller.run()

