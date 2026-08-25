import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


WAVEFORM_COLUMNS = [
    "A0_Waveform",
    "A1_Waveform",
    "A2_Waveform",
    "A3_Waveform",
    "A4_Waveform",
    "A5_Center_Waveform",
]


def apply_lowpass_filter(data, fs=843.06, cutoff=5.0, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return filtfilt(b, a, data)


def load_dataset(filename):
    df = pd.read_csv(filename)
    for col in WAVEFORM_COLUMNS:
        df[col] = df[col].apply(lambda x: np.array(json.loads(x), dtype=float))
    return df


def plot_all_waveforms(df, row_index=0, save_path=None):
    if df.empty:
        raise ValueError("Dataset is empty.")

    if row_index >= len(df):
        raise IndexError(f"row_index {row_index} is out of bounds for dataset with {len(df)} rows.")

    row = df.iloc[row_index]
    sample = row["A5_Center_Waveform"]
    if sample.size == 0:
        raise ValueError("Selected row has an empty waveform array.")

    time_axis = np.linspace(0, 5.0, len(sample))

    fig, ax = plt.subplots(figsize=(12, 7))

    for col in WAVEFORM_COLUMNS:
        values = np.asarray(row[col], dtype=float)
        if values.size == 0:
            continue
        filtered = apply_lowpass_filter(values)
        label = col.replace("_Waveform", "").replace("A5_Center", "A5 Center")
        ax.plot(time_axis, filtered, linewidth=2, label=label)

    ax.set_title(f"Photodiode Waveforms — Row {row_index}")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Intensity (filtered)")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(loc="best")
    plt.tight_layout()

    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=200)
        print(f"Saved waveform plot to {save_path}")

    plt.show()


def main(filename="waveform_row_data_1786958563.csv"):
    root = Path(__file__).resolve().parents[1]
    csv_path = root / filename
    df = load_dataset(csv_path)

    output_dir = root / "output"
    save_path = output_dir / "all_photodiode_waveforms.png"
    plot_all_waveforms(df, row_index=0, save_path=save_path)


if __name__ == "__main__":
    main()
