import RPi.GPIO as GPIO
import time

class Pulse_RPM:
    def __init__(self, pulse_rpm_pin):
        """
        Initialize the Pulse_RPM class.

        Args:
            pulse_rpm_pin (int): GPIO pin number connected to the pulse signal.
        """
        self.pulse_rpm_pin = pulse_rpm_pin  # GPIO pin used for pulse measurement
        self.rpm_count = 0  # Counter to track the number of pulses detected
        self.start_time = time.time()  # Record the start time for RPM calculation
        self.pulse_rpm = 0  # Variable to store the calculated RPM value

        # Set up GPIO pin for input and enable pull-down resistor
        GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
        GPIO.setup(self.pulse_rpm_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Set up an event detection for a rising edge on the pulse pin
        GPIO.add_event_detect(self.pulse_rpm_pin, GPIO.RISING, callback=self.count_pulses)

    def count_pulses(self, channel):
        """
        Callback function to increment the RPM count whenever a rising edge is detected.

        Args:
            channel (int): The GPIO channel where the pulse was detected.
        """
        self.rpm_count += 1  # Increment the pulse count

    def calculate_pulse_rpm(self):
        """
        Calculate the pulse-based RPM (Revolutions Per Minute).

        Formula:
            RPM = (Number of pulses / Pulses per revolution) / Time interval * 60

        The function resets the pulse count and time interval after each calculation.
        """
        current_time = time.time() - self.start_time  # Calculate the elapsed time since the last calculation
        current_count = self.rpm_count  # Store the current pulse count
        
        self.rpm_count = 0  # Reset the pulse count for the next interval
        self.start_time = time.time()  # Reset the start time for the next interval

        if current_time > 0:  # Avoid division by zero
            # Calculate RPM based on the pulses and elapsed time
            self.pulse_rpm = (current_count / 7.0) / current_time * 60.0
        else:
            self.pulse_rpm = 0  # If time is zero, RPM is set to zero

    def cleanup(self):
        """
        Clean up the GPIO settings to release resources.

        This function should be called when the program terminates to avoid GPIO warnings or conflicts.
        """
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    try:
        # Initialize the Pulse_RPM instance with GPIO pin 17
        pulse_rpm_sensor = Pulse_RPM(pulse_rpm_pin=17)
        
        while True:
            # Wait for a short interval before calculating RPM
            time.sleep(1)  # Adjust the sleep duration as needed
            pulse_rpm_sensor.calculate_pulse_rpm()
            print(f"Current RPM: {pulse_rpm_sensor.pulse_rpm:.2f}")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        # Clean up GPIO resources
        pulse_rpm_sensor.cleanup()
