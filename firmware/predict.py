"""
Live Prediction Script:
- Streams data from the Arduino in real-time.
- Buffers 5 seconds of data during manual polarizer rotation.
- Applies the zero-phase low-pass filter.
- Evaluates the Center PD features using the 2D Bounding Box model.
- Prints the live prediction and strip alignment instantly.
"""
import numpy as np
import time
from utils.filters import apply_lowpass_filter
from utils.reader import read_arduino_binary

FS = 843.06  # Sampling frequency in Hz
TIME_WINDOW = 5.0  # Time window for data collection in seconds
BUFFER_SIZE = int(FS * TIME_WINDOW)  # Buffer size for the specified time window

if __name__ == "__main__":
    COMP_PORT = 'COM8'
    BAUD_RATE = 115200  # Baud rate for serial communication

    print("Starting Live Prediction System...")
    print(f"Connecting to Arduino on {COMP_PORT}...")
    
    sensor_stream = read_arduino_binary(COMP_PORT, BAUD_RATE)

    data_buffer = {i: [] for i in range(6)}  # Buffer for the 6 photodiodes
    sample_collected = 0
    
    print(f"\nSystem Ready! Please rotate the polarizer continuously for {BUFFER_SIZE / FS:.1f} seconds per test.")

    for readings in sensor_stream:
        # Buffer only the first 6 sensor readings (A0-A5), ignoring any button labels
        for i in range(6):
            data_buffer[i].append(readings[i])

        sample_collected += 1

        # Check if the 5-second buffer is full
        if sample_collected >= BUFFER_SIZE:
            print("\n--------------------------------------------------")
            print("Buffer full. Analyzing rotation...")

            contrasts = []
            max_intensities = []

            # Mathematical processing for live prediction
            for i in range(6):
                channel_data = np.array(data_buffer[i])
                smoothed_data = apply_lowpass_filter(channel_data, FS, cutoff=5.0, order=4)
                I_max = np.max(smoothed_data)
                I_min = np.min(smoothed_data)

                contrast = (I_max - I_min) / ((I_max + I_min) + 1e-6)
                contrasts.append(contrast)
                max_intensities.append(I_max)

            # Extract Center PD features (A5 is index 5)
            center_contrast = contrasts[5]
            center_I_max = max_intensities[5]
            ring_contrasts = contrasts[:5]

            print(f"Metrics -> Center I_max: {center_I_max:.1f} | Center Contrast: {center_contrast:.4f}")

            # --- 2D BOUNDING BOX CLASSIFIER ---
            # Ecoflex Goldilocks Zone: I_max between 200 and 265, Contrast > 0.50
            is_ecoflex = (200 < center_I_max < 265) and (center_contrast > 0.50)

            if is_ecoflex:
                print(">>> PREDICTION: PURE ECOFLEX")
                print("    (Readings fall securely inside the baseline Goldilocks zone)")
            else:
                print(">>> PREDICTION: CELLOPHANE STRIP DETECTED!")
                if center_I_max > 265:
                    print("    (Signature: Optical Window Alignment)")
                else:
                    print("    (Signature: Birefringent Waveplate Alignment)")
                
                # Locate which ring sensor the strip is pointing toward
                min_index = np.argmin(ring_contrasts)
                print(f">>> ALIGNMENT: Strip is pointing toward Ring PD A{min_index}")

            print("--------------------------------------------------")

            # Reset the buffer to immediately start listening for the next test
            data_buffer = {i: [] for i in range(6)}
            sample_collected = 0

            print(f"Waiting for next rotation... Rotate for {BUFFER_SIZE / FS:.1f} seconds.")