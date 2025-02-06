from light_controller import LightController
from thermometer import Thermometer
import signal
import time

def house():
    with LightController(save_data=True, save_mins=5) as lights, Thermometer(save_data=True, save_mins=5, sync_data=True, sync_key_path = 'secret_db_keys.yaml') as temp:
        while True:
        # Isolate each module call to prevent one module from crashing the whole program
            try:
                lights.step()
            except Exception as e:
                print("Error in LightController:", e)
            
            try:
                temp.step()
            except Exception as e:
                print("Error in Thermometer:", e)
            
            time.sleep(1)

if __name__ == '__main__':
    house()
