import threading
from light_controller import LightController
from thermometer import Thermometer
import signal
import time
import cv2

def signal_handler():
    print("\nhouse.py terminated with Ctrl+C.")
    if l_thread.is_alive():
        l_thread.join()
    if t_thread.is_alive():
        t_thread.join()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

lights = LightController()
l_thread = threading.Thread(target = lights.run)
l_thread.daemon = True
l_thread.start()

temp = Thermometer()
t_thread = threading.Thread(target = temp.run)
t_thread.daemon = True
t_thread.start()

print("house.py is running")
while True:
    if l_thread.is_alive():
        pass
    if t_thread.is_alive():
        pass
    time.sleep(1)