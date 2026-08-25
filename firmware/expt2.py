"""
Experiment 2: collect photodiode readings and save them to a CSV file for later visualization.
"""

import csv
from datetime import datetime
from pathlib import Path
from statistics import median

from utils.reader import read_arduino_binary


def moving_median(readings_buffer, window_size=3):
    """Return a filtered reading for the latest sample using a moving median across channels."""
    if not readings_buffer:
        return []

    window = readings_buffer[-window_size:]
    if len(window) == 1:
        return list(window[0])

    filtered = []
    for channel in range(len(window[0])):
        channel_values = [sample[channel] for sample in window]
        filtered.append(median(channel_values))

    return filtered


def save_readings_to_csv(output_path, readings, timestamp=None):
    """Append one filtered reading sample to a CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = output_path.exists()
    with output_path.open("a", newline="") as handle:
        writer = csv.writer(handle)
        if not file_exists or output_path.stat().st_size == 0:
            writer.writerow([
                "timestamp",
                "sensor_0",
                "sensor_1",
                "sensor_2",
                "sensor_3",
                "sensor_4",
                "sensor_5",
            ])

        writer.writerow([timestamp or datetime.now().isoformat(), *readings])

    return output_path


def main():
    COM_PORT = "COM8"  # Update this to your port
    BAUD_RATE = 115200
    BUFFER_SIZE = 2**5  # Number of samples to average for a stable reading
    OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "expt2_readings.csv"

    sensor_stream = read_arduino_binary(COM_PORT, BAUD_RATE)

    print(f"Saving readings to {OUTPUT_PATH}")
    print("Waiting for data...")

    readings_buffer = []
    sample_count = 0
    output_path = OUTPUT_PATH

    for readings in sensor_stream:
        readings_buffer.append(readings)

        if len(readings_buffer) >= BUFFER_SIZE:
            latest_reading = moving_median(readings_buffer, window_size=3)
            output_path = save_readings_to_csv(output_path, latest_reading)
            sample_count += 1
            print(f"Saved sample {sample_count}: {latest_reading}")

            readings_buffer.pop(0)

    print(f"Finished. Data saved to {output_path}")


if __name__ == "__main__":
    main()
