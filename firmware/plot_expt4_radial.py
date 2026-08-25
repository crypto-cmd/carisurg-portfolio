"""Animate expt4 sensor values as a radial layout matching the circular sensor arrangement."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pandas as pd
import numpy as np


def plot_radial_sequence(csv_path):
    df = pd.read_csv(csv_path)
    if df.empty:
        return

    sensor_columns = [f"sensor_{i}" for i in range(6)]
    values = df[sensor_columns].to_numpy(dtype=float)

    angles = np.deg2rad([90, 18, 306, 234, 162, 0])

    fig, ax = plt.subplots(figsize=(7, 7))
    plt.subplots_adjust(bottom=0.2)
    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.axis("off")

    for idx, angle in enumerate(angles[:-1]):
        x = np.cos(angle)
        y = np.sin(angle)
        ax.scatter(x, y, color="lightgray", s=180)
        ax.text(x * 1.12, y * 1.12, str(idx), ha="center", va="center", fontsize=10)

    slider_ax = plt.axes([0.2, 0.05, 0.6, 0.03])
    slider = Slider(slider_ax, "sample", 0, len(df) - 1, valinit=0, valstep=1)

    def update(step):
        step = int(step)
        current = values[step]
        ax.clear()
        ax.set_aspect("equal")
        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.4, 1.4)
        ax.axis("off")

        for idx, angle in enumerate(angles[:-1]):
            x = np.cos(angle)
            y = np.sin(angle)
            radius = 0.65 + 0.35 * (current[idx] / 1023.0)
            ax.scatter(x * radius, y * radius, color="tab:blue", s=220)
            ax.text(x * 1.12, y * 1.12, str(idx), ha="center", va="center", fontsize=10)

        center_radius = 0.28 + 0.35 * (current[5] / 1023.0)
        ax.scatter(0, 0, color="tab:red", s=220 * (1 + 0.4 * center_radius))
        ax.set_title(f"{csv_path.name} | sample {step}")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    update(0)
    plt.show()


def main():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    csv_files = sorted(data_dir.glob("expt4_readings_*.csv"))

    if not csv_files:
        print("No expt4 CSV files found in the data folder.")
        return

    for csv_file in csv_files:
        plot_radial_sequence(csv_file)


if __name__ == "__main__":
    main()
