"""
I have 5 photodiodes in a circular arrangement (A0-A4 from top left counterclockwise with A3 at the bottom). 
A sixth photodiode (A5) is placed in the center of the circle. 
The photodiodes are connected to an Arduino, which reads their values and sends them to a computer via serial.

Experiment 6:
- Stream the readings from the Arduino
- Buffer 5 seconds of data and apply a zero-phase low-pass filter for live terminal feedback
- Save the entire raw 5-second waveform to a single CSV row for offline analysis
"""
import csv
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np

from utils.filters import apply_lowpass_filter
from utils.reader import read_arduino_binary

FS = 843.06  # Sampling frequency in Hz
TIME_WINDOW = 5.0  # Time window for data collection in seconds
BUFFER_SIZE = int(FS * TIME_WINDOW)  # Buffer size for the specified time window

DEFAULT_OUTPUT_PATH = Path(r"C:\Users\orvil\source\repos\carisurg-portfolio\waveform_row_data_1786958563.csv")
CSV_HEADER = [
    "Run_ID", "Label_ID", "Material",
    "A0_Waveform", "A1_Waveform", "A2_Waveform",
    "A3_Waveform", "A4_Waveform", "A5_Center_Waveform"
]


def resolve_label_info(label_id):
    """Map the Arduino button states to a stable label/material tuple.

    Arduino values are:
      0 = no button
      1 = ecoflex
      2 = cellophane_A
      3 = cellophane_B
      4 = record point (one trigger, even if sent repeatedly)
    """
    if label_id == 1:
        return 1, "Ecoflex"
    if label_id == 2:
        return 2, "Cellophane_A"
    if label_id == 3:
        return 3, "Cellophane_B"
    if label_id == 4:
        return 4, "Record_Point"
    return 0, "No Button"


def should_record_point(current_label, last_label):
    """Return True only on the first label 4 in a consecutive run.

    Repeated 4 values should not trigger multiple saves. The trigger fires only
    on the transition from a non-4 label to 4.
    """
    return current_label == 4 and last_label != 4


def ensure_csv_headers(csv_path):
    """Create a CSV with headers if it does not already exist."""
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists() or csv_path.stat().st_size == 0:
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)


def resolve_next_run_id(csv_path):
    """Return the next Run_ID, continuing from the last row already in the CSV."""
    csv_path = Path(csv_path)
    ensure_csv_headers(csv_path)

    with open(csv_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) <= 1:
        return 1

    last_run_id = 0
    for row in rows[1:]:
        if not row:
            continue
        try:
            last_run_id = max(last_run_id, int(row[0]))
        except (TypeError, ValueError):
            continue

    return last_run_id + 1


def append_waveform_row(csv_path, row):
    """Append one waveform row to an existing CSV while ensuring headers exist."""
    csv_path = Path(csv_path)
    ensure_csv_headers(csv_path)

    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)
        file.flush()


if __name__ == "__main__":
    COMP_PORT = 'COM8'
    BAUD_RATE = 115200  # Baud rate for serial communication

    output_path = DEFAULT_OUTPUT_PATH
    ensure_csv_headers(output_path)
    run_id = resolve_next_run_id(output_path)

    print(f"Data collection ready. Saving raw waveforms to {output_path.name}")
    print("Hold Button 1 (Ecoflex) or Button 2 (Cellophane) while rotating.")

    sensor_stream = read_arduino_binary(COMP_PORT, BAUD_RATE)

    data_buffer = {i: [] for i in range(6)}
    label_buffer = []
    sample_collected = 0
    last_label = None
    trigger_pending = False

    print(f"\nWaiting for data... Please rotate the polarizer for {BUFFER_SIZE / FS} seconds.")

    for readings in sensor_stream:
        current_label = int(readings[6])
        trigger_pending = should_record_point(current_label, last_label)
        last_label = current_label

        # Append the 6 sensor readings
        for i in range(6):
            data_buffer[i].append(readings[i])

        # Append the 7th value (the button label)
        label_buffer.append(current_label)

        sample_collected += 1

        # Check if the buffer is full
        if sample_collected >= BUFFER_SIZE:
            print("\nBuffer full. Processing data...")

            contrasts = []

            # Mathematical processing for live terminal feedback
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

            # --- SAVE WAVEFORM ROW LOGIC ---
            if trigger_pending:
                label_id, material = resolve_label_info(4)
                label_name = "Record_Point"
            else:
                dominant_label = Counter(label_buffer).most_common(1)[0][0]
                label_id, material = resolve_label_info(dominant_label)
                label_name = "Ecoflex" if label_id == 1 else "Cellophane_A" if label_id == 2 else "Cellophane_B" if label_id == 3 else "No Button"

            if label_id > 0:
                print(f">>> SAVING WAVEFORM TO CSV: Labeled as {label_name} (Run ID: {run_id})")

                row = [
                    run_id,
                    label_id,
                    material,
                    json.dumps(data_buffer[0]),
                    json.dumps(data_buffer[1]),
                    json.dumps(data_buffer[2]),
                    json.dumps(data_buffer[3]),
                    json.dumps(data_buffer[4]),
                    json.dumps(data_buffer[5])
                ]

                append_waveform_row(output_path, row)
                print(">>> SAVE COMPLETE.")
                run_id += 1
            else:
                print(">>> NOT SAVED: No button was held during this rotation.")

            # Clear the buffers to start collecting the next batch
            data_buffer = {i: [] for i in range(6)}
            label_buffer = []
            sample_collected = 0
            trigger_pending = False

            print(f"\nWaiting for data... Please rotate the polarizer for {BUFFER_SIZE / FS} seconds.")