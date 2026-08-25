import serial
import struct
import time

MAX_SENSOR_VALUE = 1023


def is_valid_readings(readings, max_value=MAX_SENSOR_VALUE):
    """Return True when a reading packet has 7 integers and the first 6 are in ADC range."""
    if len(readings) != 7:
        return False
    # Check only the first 6 values for the 1023 bounds.
    sensors_valid = all(isinstance(val, int) and 0 <= val <= max_value for val in readings[:6])
    # The Arduino label may be 0 (rotating), 1-3 (material labels), or 4 (record point).
    label_valid = readings[6] in (0, 1, 2, 3, 4)

    return sensors_valid and label_valid

def read_arduino_binary(port, baudrate=115200, frame_marker=b'\xAA\xBB'):
    """
    Connects to the COM port and yields only sane 7-channel readings.
    Corrupt or misaligned frames are skipped so bogus spikes do not propagate.
    """
    ser = serial.Serial(port, baudrate, timeout=0.2)
    print(f"Connected to {port} at {baudrate} baud.")
    ser.reset_input_buffer()

    try:
        while True:
            # 1. Frame Alignment
            if ser.read(1) == frame_marker[0:1]:
                if ser.read(1) == frame_marker[1:2]:
                    # 2. Read Payload
                    data_bytes = ser.read(14)  # 6 channels * 2 bytes each + 2 bytes for label
                    if len(data_bytes) == 14:
                        readings = struct.unpack('<7H', data_bytes)
                        if is_valid_readings(readings):
                            # 3. Yield only sane packets
                            yield readings

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

def measure_sampling_rate(port, baudrate=115200, samples_to_measure=500):
    print(f"Connecting to {port} to benchmark speed...")
    sensor_stream = read_arduino_binary(port, baudrate)
    
    # Burn the first 20 readings to clear any old buffered serial data
    print("Clearing buffer...")
    for _ in range(20):
        next(sensor_stream)
        
    print(f"Timing the next {samples_to_measure} samples. Please wait...")
    
    # Start the stopwatch
    start_time = time.time()
    
    # Collect the exact number of required samples
    for _ in range(samples_to_measure):
        next(sensor_stream)
        
    # Stop the stopwatch
    end_time = time.time()
    
    elapsed = end_time - start_time
    actual_fs = samples_to_measure / elapsed
    
    print(f"\n--- Results ---")
    print(f"Time elapsed: {elapsed:.3f} seconds")
    print(f"Actual Sampling Rate (FS): {actual_fs:.2f} Hz")
    
    return actual_fs

# --- Main Execution Block ---
if __name__ == "__main__":
    COM_PORT = 'COM8'
    BAUD_RATE = 115200

    sensor_stream = read_arduino_binary(COM_PORT, BAUD_RATE)

    print("Waiting for data...")

    for readings in sensor_stream:
        print(f"Readings: {readings}")