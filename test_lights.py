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
        # Initial state check
        print(f"Starting test at {self.current_time.strftime('%Y-%m-%d %H:%M')}")

        # Simulate a day's cycle rapidly
        for _ in range(24):  # Simulate 24 hours in a loop
            self.fast_forward_time(1)  # Fast forward one hour at a time
            self.step()  # Invoke the step method to check and adjust light status
            time.sleep(2)  # Short delay to visually observe the light change

        print("Test completed.")

if __name__ == "__main__":
    # Initialize the test controller
    test_controller = TestLightController(save_data=False)

    # Modify the current_time to the start of the testing period
    test_controller.current_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Run the test
    test_controller.test_run()