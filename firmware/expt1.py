"""
I have two orthogonally oriented NIR linear polarizing films. Between them I have a gear with 18 teeth. I want to measure the intensity of light passing through this setup as the gear rotates. I will read the values from 6 photodiodes (A0-A5) arranged in a pentagon shape around the gear. I will pass the readings through the median filter to reduce noise. The terminal will display the readings. I am rotatingthe gear by hand and writng down the readings. There is no visualization necessary.
"""

from utils.reader import read_arduino_binary
from utils.filters import median_filter
import numpy as np
def main():
    COM_PORT = 'COM8'  # Update this to your port
    BAUD_RATE = 115200
    BUFFER_SIZE = 2**5  # Number of samples to average for a stable reading

    # Initialize the sensor stream
    sensor_stream = read_arduino_binary(COM_PORT, BAUD_RATE)

    print("Waiting for data...")

    # Buffer to hold recent readings for median filtering
    readings_buffer = []

    for readings in sensor_stream:
        # Append the new readings to the buffer
        readings_buffer.append(readings)

        # If we have enough samples, apply the median filter
        if len(readings_buffer) >= BUFFER_SIZE:
            # Convert buffer to numpy array for filtering
            buffer_array = np.array(readings_buffer)
            filtered_readings = median_filter(buffer_array, window_size=3)

            # Print the filtered readings (last entry)
            print(f"Filtered Readings: {filtered_readings[-1]}")

            # Remove the oldest reading to maintain buffer size
            readings_buffer.pop(0)

if __name__ == "__main__":
    main()