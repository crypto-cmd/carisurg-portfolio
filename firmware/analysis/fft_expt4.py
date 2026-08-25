"""Plot FFTs for each CSV in the expt4 sample_1 directory in one figure."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SENSOR_PREFIX = "sensor_"


def compute_fft(values, sample_rate_hz):
    """Return frequency bins and magnitude spectrum for a 1D signal."""
    signal = np.asarray(values, dtype=float)
    if signal.size < 2:
        return np.array([]), np.array([])

    window = np.hanning(signal.size)
    windowed_signal = signal * window
    spectrum = np.fft.rfft(windowed_signal)
    freqs = np.fft.rfftfreq(signal.size, d=1.0 / sample_rate_hz)
    magnitudes = np.abs(spectrum)
    return freqs, magnitudes


def load_csv_data(csv_path):
    """Read a CSV and return a dataframe plus the sensor columns."""
    df = pd.read_csv(csv_path)
    sensor_columns = [column for column in df.columns if column.startswith(SENSOR_PREFIX)]
    if not sensor_columns:
        raise ValueError(f"No sensor columns found in {csv_path}")

    df[sensor_columns] = df[sensor_columns].apply(pd.to_numeric, errors="coerce")
    return df, sensor_columns


def infer_sample_rate_hz(df):
    """Estimate the sample rate from the timestamp column when available."""
    if "timestamp" not in df.columns:
        return 100.0

    timestamps = pd.to_datetime(df["timestamp"], errors="coerce")
    timestamps = timestamps.dropna()
    if len(timestamps) < 2:
        return 100.0

    deltas = np.diff(timestamps.astype("int64") / 1e9)
    positive_deltas = deltas[deltas > 0]
    if positive_deltas.size == 0:
        return 100.0

    return 1.0 / np.median(positive_deltas)


def main():
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data" / "expt4" / "sample_1"
    csv_files = sorted(data_dir.glob("expt4_readings_*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    fig, axes = plt.subplots(len(csv_files), 1, figsize=(12, 4 * len(csv_files)), sharex=False)
    if len(csv_files) == 1:
        axes = [axes]

    for ax, csv_path in zip(axes, csv_files):
        df, sensor_columns = load_csv_data(csv_path)
        sample_rate_hz = infer_sample_rate_hz(df)

        for sensor_name in sensor_columns:
            freqs, magnitudes = compute_fft(df[sensor_name].dropna().to_numpy(), sample_rate_hz)
            if freqs.size == 0:
                continue
            ax.plot(freqs, magnitudes, label=sensor_name, linewidth=1.0)

        ax.set_title(csv_path.name)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Magnitude")
        ax.grid(alpha=0.3)
        ax.legend(loc="upper right", ncol=2, fontsize=8)
        ax.set_xlim(0, min(sample_rate_hz / 2, 250))

    fig.suptitle("FFT comparison for expt4 sample_1 CSVs")
    fig.tight_layout(rect=[0, 0, 1, 0.98])

    output_path = data_dir / "fft_comparison.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Saved combined FFT figure to {output_path}")

    try:
        plt.show()
    except Exception:
        pass


if __name__ == "__main__":
    main()
