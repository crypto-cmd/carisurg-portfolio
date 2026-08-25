"""Plot Arduino sensor readings in real time."""

import os
import time

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
from serial.tools import list_ports

from utils.reader import read_arduino_binary


def find_port(candidates=None):
    """Return the first available serial port from a preferred list."""
    candidates = candidates or [
        os.environ.get("ARDUINO_PORT"),
        "COM8",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM9",
    ]

    available_ports = [port.device for port in list_ports.comports()]

    for candidate in candidates:
        if candidate and candidate in available_ports:
            return candidate

    if available_ports:
        return available_ports[0]

    return candidates[0] or "COM8"


def main():
    port = find_port()
    baud_rate = 115200

    print(f"Connecting to {port} at {baud_rate} baud...")
    sensor_stream = read_arduino_binary(port, baud_rate)

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Real-time sensor readings")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Value")

    samples = []
    timestamps = []
    start_time = None
    history_window = 10.0
    sensor_lines = [ax.plot([], [], label=f"sensor_{index}")[0] for index in range(6)]
    ax.legend(loc="upper right")

    def update(_frame):
        nonlocal start_time

        try:
            readings = next(sensor_stream)
        except StopIteration:
            return tuple(sensor_lines)
        except serial.SerialException as exc:
            print(f"Serial error: {exc}")
            return tuple(sensor_lines)

        if start_time is None:
            start_time = time.monotonic()

        now = time.monotonic() - start_time
        timestamps.append(now)
        samples.append(readings)

        cutoff = now - history_window
        while timestamps and timestamps[0] < cutoff:
            timestamps.pop(0)
            samples.pop(0)

        for index, line in enumerate(sensor_lines):
            values = [sample[index] for sample in samples]
            line.set_data(timestamps, values)

        ax.relim()
        ax.autoscale_view()
        return tuple(sensor_lines)

    animation = FuncAnimation(fig, update, interval=5, cache_frame_data=False)
    print("Waiting for sensor data...")
    plt.show()


if __name__ == "__main__":
    main()
