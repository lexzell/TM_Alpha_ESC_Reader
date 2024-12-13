import serial

class ESC_Reader:
    def __init__(self, port, baudrate, timeout=1):
        # Initialize the serial connection to the ESC
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        
        # Define initial values for the telemetry data
        self.rx_throttle = 0
        self.actual_throttle = 0
        self.electric_rpm = 0
        self.busbar_voltage = 0
        self.busbar_current = 0
        self.phase_line_current = 0

    def bytes_to_signed_decimal(self, byte_data):
        # Convert bytes to a signed integer
        hex_value = byte_data.hex()
        num = int(hex_value, 16)
        if num >= 2**15:
            num -= 2**16
        return num

    def read_data(self):
        # Read the telemetry data from the ESC
        if self.ser.in_waiting > 0:  # The data package is of size 24
            data = self.ser.read(1)
            if data == b'\x9b':  # Read bytes until the start header 0x9b is found
                data = self.ser.read(23)  # Read the data package of size 24 - 1
                self.rx_throttle = int.from_bytes(data[5:7], 'big') * 100.0 / 1024.0
                self.actual_throttle = int.from_bytes(data[7:9], 'big') * 100.0 / 1024.0
                if round(int.from_bytes(data[9:11], 'big') * 10 / 7, 1) > 8800:
                    self.electric_rpm = 0
                else:
                    self.electric_rpm = round(int.from_bytes(data[9:11], 'big') * 10 / 7, 1)
                self.busbar_voltage = int.from_bytes(data[11:13], 'big') / 10.0
                self.busbar_current = self.bytes_to_signed_decimal(data[13:15]) / 64
                self.phase_line_current = self.bytes_to_signed_decimal(data[15:17]) / 64
                return True
            else:
                return False

    def output_data(self):
        # Output the ESC data to the console (for debugging purposes)
        print(f"RX Throttle: {self.rx_throttle}, Actual Throttle: {self.actual_throttle}, "
              f"RPM: {self.electric_rpm}, Voltage: {self.busbar_voltage}, "
              f"Busbar Current: {self.busbar_current}, Phase Line Current: {self.phase_line_current}")
