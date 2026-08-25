"""Save one averaged row per trigger window to CSV with no live plotting."""

import csv
import time
from pathlib import Path

import numpy as np

from utils.reader import read_arduino_binary

COMP_PORT = "COM8"
BAUD_RATE = 115200
CSV_HEADER = ["id", "A0", "A1", "A2", "A3", "A4", "A5"]


def should_record_point(current_label, last_label):
    """Return True only on the transition into the 4 record label."""
    return current_label == 4 and last_label != 4


def average_trigger_windows(windows):
    """Average channel values across all collected trigger windows."""
    if not windows:
        return {channel: np.array([], dtype=float) for channel in range(6)}

    averaged = {}
    for channel in range(6):
        values = [np.asarray(window.get(channel, []), dtype=float) for window in windows]
        values = [arr for arr in values if arr.size]
        if not values:
            averaged[channel] = np.array([], dtype=float)
        else:
            averaged[channel] = np.mean(np.stack(values, axis=0), axis=0)
    return averaged


def save_csv_row(csv_path, row_id, averaged_readings):
    """Append one averaged row to the CSV file."""
    with open(csv_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([row_id, *averaged_readings])


def main():
    timestamp = int(time.time())
    script_dir = Path(__file__).resolve().parent
    csv_path = script_dir / f"waveform_row_data_rotating_polarizers_expt8_{timestamp}.csv"

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)

    sensor_stream = read_arduino_binary(COMP_PORT, BAUD_RATE)
    active_window = {i: [] for i in range(6)}
    last_label = None
    row_id = 0

    try:
        for readings in sensor_stream:
            label = int(readings[6])

            if label == 4:
                if should_record_point(label, last_label):
                    print("Detected trigger label 4. Collecting record window...")
                    active_window = {i: [] for i in range(6)}
                for channel in range(6):
                    active_window[channel].append(readings[channel])
                last_label = label
                continue

            if last_label == 4 and any(active_window[channel] for channel in range(6)):
                averaged = average_trigger_windows([active_window])
                averaged_readings = [float(np.mean(averaged[channel])) for channel in range(6)]
                save_csv_row(csv_path, row_id, averaged_readings)
                print(f"Saved row {row_id}: {averaged_readings}")
                row_id += 1
                active_window = {i: [] for i in range(6)}

            last_label = label

    except KeyboardInterrupt:
        print("Stopped data capture.")


if __name__ == "__main__":
    main()