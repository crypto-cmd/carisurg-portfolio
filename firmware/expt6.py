"""
I have 5 photodiodes in a circular arrangement (A0-A4 from top left counterclockwise with A3 at the bottom). 
A sixth photodiode (A5) is placed in the center of the circle. 
The photodiodes are connected to an Arduino, which reads their values and sends them to a computer via serial.

Experiment 6:
- Stream the readings from the Arduino
- Buffer 5 seconds of data, apply a zero-phase low-pass filter
- Calculate optical contrast and ring variance
- Save the calculated data to a CSV if a hardware button was held during the rotation
"""
import numpy as np
import csv
import time
from collections import Counter
from utils.filters import apply_lowpass_filter
from utils.reader import read_arduino_binary

FS = 843.06  # Sampling frequency in Hz
CUTOFF_FREQUENCY = 5.0  # Cutoff frequency for low-pass filter in Hz
TIME_WINDOW = 5.0  # Time window for data collection in seconds
BUFFER_SIZE = int(FS * TIME_WINDOW)  # Buffer size for the specified time window

SYMMETRY_THRESHOLD = 0.1  # Threshold for symmetry detection (adjust as needed)


def resolve_label_info(label_id):
    """Return the Arduino's label ID and the material name for the window."""
    if label_id == 1:
        return 1, "Ecoflex"
    if label_id == 2:
        return 2, "Cellophane"
    if label_id == 3:
        return 3, "Cellophane"
    return 0, "No Button"


if __name__ == "__main__":
    COMP_PORT = 'COM8'
    BAUD_RATE = 115200  # Baud rate for serial communication

    # Create a unique filename based on the current time
    filename = f"calculated_polarizer_data_{int(time.time())}.csv"

    # Open the CSV file and write the headers once
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "A0_Contrast", "A1_Contrast", "A2_Contrast", "A3_Contrast", "A4_Contrast", 
            "Center_Contrast", "Ring_Variance", "Label_ID", "Material"
        ])

        print(f"Data collection ready. Saving calculated results to {filename}")
        print("Hold Button 1 (Ecoflex) or Button 2 (Cellophane) while rotating.")

        sensor_stream = read_arduino_binary(COMP_PORT, BAUD_RATE)

        data_buffer = {i: [] for i in range(6)}  # Buffer for 6 photodiodes
        label_buffer = []                        # Buffer for the button label
        sample_collected = 0
        
        print(f"\nWaiting for data... Please rotate the polarizer for {BUFFER_SIZE / FS} seconds.")

        for readings in sensor_stream:
            # Append the 6 sensor readings
            for i in range(6):
                data_buffer[i].append(readings[i])
            
            # Append the 7th value (the button label)
            label_buffer.append(readings[6])

            sample_collected += 1

            # Check if the buffer is full
            if sample_collected >= BUFFER_SIZE:
                print("\nBuffer full. Processing data...")

                contrasts = []

                # Mathematical processing
                for i in range(6):
                    channel_data = np.array(data_buffer[i])
                    smoothed_data = apply_lowpass_filter(channel_data, FS, cutoff=5.0, order=4)
                    I_max = np.max(smoothed_data)
                    I_min = np.min(smoothed_data)

                    contrast = (I_max - I_min) / ((I_max + I_min) + 1e-6)
                    contrasts.append(contrast)

                center_contrast = contrasts[5]
                ring_contrasts = contrasts[:5]
                variance = np.var(ring_contrasts)

                print(f"Center PD Contrast: {center_contrast:.4f}")
                print(f"Ring PD Contrasts: {[round(c, 4) for c in ring_contrasts]}")
                print(f"Ring Variance (Symmetry Score): {variance:.6f}")

                # --- NEW LOGIC: Determine the label and save to CSV ---

                # Find the most common button state during this 5-second window
                dominant_label = Counter(label_buffer).most_common(1)[0][0]
                label_id, material = resolve_label_info(dominant_label)

                if label_id > 0:
                    label_name = "Ecoflex" if label_id == 1 else "Cellophane_A" if label_id == 2 else "Cellophane_B"

                    # Create the row of calculated data
                    row = [
                        round(ring_contrasts[0], 4), round(ring_contrasts[1], 4),
                        round(ring_contrasts[2], 4), round(ring_contrasts[3], 4),
                        round(ring_contrasts[4], 4), round(center_contrast, 4),
                        round(variance, 6), label_id, material
                    ]

                    # Write to the file and flush so it saves immediately
                    writer.writerow(row)
                    file.flush()
                    print(f">>> SAVED TO CSV: Labeled as {label_name}")
                else:
                    print(">>> NOT SAVED: No button was held during this rotation.")

                # Clear the buffers to start collecting the next batch
                data_buffer = {i: [] for i in range(6)}
                label_buffer = []
                sample_collected = 0

                print(f"\nWaiting for data... Please rotate the polarizer for {BUFFER_SIZE / FS} seconds.")