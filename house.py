from light_controller import LightController
from thermometer import Thermometer
import signal
import time

def house():
    with LightController(save_data=True, save_mins=5) as lights, Thermometer(save_data=True, save_mins=5, sync_data=True, sync_key_path = 'secret_db_keys.yaml') as temp:
        while True:
            lights.step()
            temp.step()
            time.sleep(1)


if __name__ == '__main__':
    house()
