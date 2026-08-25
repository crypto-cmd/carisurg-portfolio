"""Experiment 4: record raw sensor readings every 50 ms into a CSV file."""

import csv
from datetime import datetime
from pathlib import Path

from utils.reader import read_arduino_binary


def initialize_output(output_path):
    """Create a fresh CSV file with headers for a new run."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "timestamp",
            "sensor_0",
            "sensor_1",
            "sensor_2",
            "sensor_3",
            "sensor_4",
            "sensor_5",
        ])
    return output_path


def save_sample(output_path, readings, timestamp=None):
    """Append one sample to the CSV file."""
    output_path = Path(output_path)
    with output_path.open("a", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([timestamp or datetime.now().isoformat(), *readings])

    return output_path


def main():
    COM_PORT = "COM8"  # Update this to your port
    BAUD_RATE = 115200
    timestamp_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / f"expt4_readings_{timestamp_suffix}.csv"

    output_path = initialize_output(OUTPUT_PATH)
    sensor_stream = read_arduino_binary(COM_PORT, BAUD_RATE)

    print(f"Saving raw readings every 50 ms to {output_path}")
    print("Waiting for data...")

    last_saved = None
    for readings in sensor_stream:
        now = datetime.now()
        # if last_saved is None or (now - last_saved).total_seconds() >= 0.05:
        save_sample(OUTPUT_PATH, readings, timestamp=now.isoformat())
            # print(f"Saved: {readings}")
            # last_saved = now


if __name__ == "__main__":
    main()
