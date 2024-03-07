from light_controller import LightController
import time
from datetime import datetime, timedelta

class TestLightController(LightController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def fast_forward_time(self, hours=1):
        """Simulate time fast forward to test lights on and off logic."""
        self.current_time += timedelta(hours=hours)
        print(f"Simulated time: {self.current_time.strftime('%Y-%m-%d %H:%M')}")

    def test_run(self):
        """Run test sequence."""
        print(f"Starting test at {self.current_time.strftime('%Y-%m-%d %H:%M')}")

        # Simulate a day's cycle rapidly
        for _ in range(24):  # Simulate 24 hours in a loop
            self.fast_forward_time(1)  # Fast forward one hour at a time
            self.test_step()  # Invoke the overridden step method
            time.sleep(2)  # Short delay to visually observe the light change

        print("Test completed.")

    def test_step(self):
        """Custom step logic for testing using simulated current_time."""
        current_hour = self.current_time.hour
        self.lux = round(self.light_sensor.lux)
        print(f"{current_hour} h: {self.lux} lux")

        if self.lights_on <= current_hour < self.lights_off:
            self.pwm_blue.ChangeDutyCycle(self.light_duty_cycle)
            print("Lights should be ON based on simulated time.")
        else:
            self.pwm_blue.ChangeDutyCycle(0)
            print("Lights should be OFF based on simulated time.")

        if self.save_data:    
            if (self.current_time - self.last_save).total_seconds() > self.save_mins * 60:
                self.write_csv()
                self.last_save = self.current_time

if __name__ == "__main__":
    # Initialize the test controller with the desired start time for the test
    test_controller = TestLightController(save_data=False).__enter__()
    test_controller.current_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Run the test
    test_controller.test_run()

    # Ensure clean exit
    test_controller.__exit__(None, None, None)
