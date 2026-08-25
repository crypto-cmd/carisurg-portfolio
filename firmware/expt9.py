"""Save one averaged row per trigger window to CSV and update a live plot."""

import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt
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


def setup_live_plot():
    """Initialize an interactive live plot for channels A0-A5."""
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))

    lines = []
    for channel in range(6):
        (line,) = ax.plot([], [], marker="o", linewidth=1.5, label=f"A{channel}")
        lines.append(line)

    ax.set_title("Experiment 9 Live Averages")
    ax.set_xlabel("Saved Row ID")
    ax.set_ylabel("Averaged Sensor Value")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", ncol=3)

    fig.tight_layout()
    return fig, ax, lines


def update_live_plot(ax, lines, history):
    """Refresh the live plot with all saved averaged rows."""
    if not history:
        return

    x_values = list(range(len(history)))
    for channel, line in enumerate(lines):
        y_values = [row[channel] for row in history]
        line.set_data(x_values, y_values)

    ax.relim()
    ax.autoscale_view()
    ax.figure.canvas.draw_idle()
    ax.figure.canvas.flush_events()
    plt.pause(0.001)


def update_live_plot_with_active(ax, lines, history, active_window):
    """Refresh the plot including an in-progress point from the active trigger window."""
    y_series = [[] for _ in range(6)]

    for row in history:
        for channel in range(6):
            y_series[channel].append(row[channel])

    has_active_data = any(active_window[channel] for channel in range(6))
    if has_active_data:
        for channel in range(6):
            channel_values = active_window[channel]
            if channel_values:
                y_series[channel].append(float(np.mean(channel_values)))
            else:
                y_series[channel].append(np.nan)

    max_len = max((len(series) for series in y_series), default=0)
    if max_len == 0:
        return

    x_values = list(range(max_len))
    for channel, line in enumerate(lines):
        line.set_data(x_values, y_series[channel])

    ax.relim()
    ax.autoscale_view()
    ax.figure.canvas.draw_idle()
    ax.figure.canvas.flush_events()
    plt.pause(0.001)


def main():
    timestamp = int(time.time())
    script_dir = Path(__file__).resolve().parent
    csv_path = script_dir / f"waveform_row_data_rotating_polarizers_expt9_{timestamp}.csv"

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)

    sensor_stream = read_arduino_binary(COMP_PORT, BAUD_RATE)
    active_window = {i: [] for i in range(6)}
    last_label = None
    row_id = 0
    history = []
    plot_refresh_counter = 0

    fig, ax, lines = setup_live_plot()

    try:
        for readings in sensor_stream:
            label = int(readings[6])

            if label == 4:
                if should_record_point(label, last_label):
                    print("Detected trigger label 4. Collecting record window...")
                    active_window = {i: [] for i in range(6)}
                for channel in range(6):
                    active_window[channel].append(readings[channel])
                plot_refresh_counter += 1
                if plot_refresh_counter >= 5:
                    update_live_plot_with_active(ax, lines, history, active_window)
                    plot_refresh_counter = 0
                last_label = label
                continue

            if last_label == 4 and any(active_window[channel] for channel in range(6)):
                averaged = average_trigger_windows([active_window])
                averaged_readings = [float(np.mean(averaged[channel])) for channel in range(6)]
                save_csv_row(csv_path, row_id, averaged_readings)
                history.append(averaged_readings)
                update_live_plot(ax, lines, history)
                plot_refresh_counter = 0

                print(f"Saved row {row_id}: {averaged_readings}")
                row_id += 1
                active_window = {i: [] for i in range(6)}

            last_label = label

    except KeyboardInterrupt:
        print("Stopped data capture.")
    finally:
        plt.ioff()
        plt.close(fig)


if __name__ == "__main__":
    main()