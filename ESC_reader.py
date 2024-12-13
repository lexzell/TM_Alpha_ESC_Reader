import serial

class ESC_Reader:
    def __init__(self, port, baudrate, timeout=1):
        """
        Initialize the ESC_Reader class.

        Args:
            port (str): Serial port to connect to the ESC.
            baudrate (int): Communication speed for the serial connection.
            timeout (int, optional): Read timeout in seconds. Defaults to 1.
        """
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        
        # Define initial values for the telemetry data
        self.rx_throttle = 0  # Received throttle value in percentage
        self.actual_throttle = 0  # Actual throttle value in percentage
        self.electric_rpm = 0  # Electric RPM of the ESC
        self.busbar_voltage = 0  # Voltage across the busbar in volts
        self.busbar_current = 0  # Current through the busbar in amperes
        self.phase_line_current = 0  # Current through the phase line in amperes

    def bytes_to_signed_decimal(self, byte_data):
        """
        Convert a byte array to a signed decimal integer.

        Args:
            byte_data (bytes): The byte array to convert.

        Returns:
            int: The signed decimal integer value.
        """
        hex_value = byte_data.hex()  # Convert byte data to hexadecimal string
        num = int(hex_value, 16)  # Convert hexadecimal string to integer
        if num >= 2**15:  # Check if the value is negative in two's complement
            num -= 2**16  # Adjust to negative value
        return num

    def read_data(self):
        """
        Read and parse telemetry data from the ESC.

        Returns:
            bool: True if data was successfully read and parsed, False otherwise.
        """
        if self.ser.in_waiting > 0:  # Check if data is available in the serial buffer
            data = self.ser.read(1)  # Read one byte to check the start header
            if data == b'\x9b':  # Validate the start header byte
                data = self.ser.read(23)  # Read the remaining 23 bytes of the data package
                # Parse and scale telemetry values
                self.rx_throttle = int.from_bytes(data[5:7], 'big') * 100.0 / 1024.0
                self.actual_throttle = int.from_bytes(data[7:9], 'big') * 100.0 / 1024.0
                # Calculate electric RPM and handle invalid values
                if round(int.from_bytes(data[9:11], 'big') * 10 / 7, 1) > 8800:
                    self.electric_rpm = 0
                else:
                    self.electric_rpm = round(int.from_bytes(data[9:11], 'big') * 10 / 7, 1)
                # Parse and scale voltage and current values
                self.busbar_voltage = int.from_bytes(data[11:13], 'big') / 10.0
                self.busbar_current = self.bytes_to_signed_decimal(data[13:15]) / 64
                self.phase_line_current = self.bytes_to_signed_decimal(data[15:17]) / 64
                return True  # Indicate successful data reading
            else:
                return False  # Invalid start header

    def output_data(self):
        """
        Output the telemetry data to the console for debugging purposes.
        """
        print(f"RX Throttle: {self.rx_throttle:.2f}%, Actual Throttle: {self.actual_throttle:.2f}%, "
              f"RPM: {self.electric_rpm:.1f}, Voltage: {self.busbar_voltage:.1f}V, "
              f"Busbar Current: {self.busbar_current:.2f}A, Phase Line Current: {self.phase_line_current:.2f}A")

if __name__ == "__main__":
    """
    Main entry point for the script.
    
    Initializes the ESC reader and continuously reads and outputs data.
    """
    # Replace with the actual port and baudrate for your ESC
    port = "/dev/ttyUSB0"  # Adjust for your needs
    baudrate = 115200  # Baudrate for serial communication with the ESC

    try:
        # Initialize the ESC reader
        esc_reader = ESC_Reader(port, baudrate)
        print("Starting ESC Reader... Press Ctrl+C to stop.")

        while True:
            # Continuously read and output data
            if esc_reader.read_data():
                esc_reader.output_data()

    except KeyboardInterrupt:
        # Handle user interrupt (Ctrl+C)
        print("\nESC Reader stopped by user.")

    except serial.SerialException as e:
        # Handle serial communication errors
        print(f"Serial error: {e}")

    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}")
