import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


def apply_lowpass_filter(data, fs=843.06, cutoff=5.0, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)


def resolve_label_name(label_id):
    mapping = {
        0: "No Button",
        1: "Ecoflex",
        2: "Cellophane_A",
        3: "Cellophane_B",
    }
    return mapping.get(int(label_id), "Unknown")


def extract_center_features(row):
    a5_raw = np.asarray(row["A5_Center_Waveform"], dtype=float)
    if a5_raw.size == 0:
        raise ValueError("Center waveform is empty for this row.")

    a5_filtered = apply_lowpass_filter(a5_raw)

    i_max = np.max(a5_filtered)
    i_min = np.min(a5_filtered)
    contrast = (i_max - i_min) / ((i_max + i_min) + 1e-6)
    return i_max, contrast


def load_dataset(filename):
    df = pd.read_csv(filename)
    waveform_cols = [
        "A0_Waveform", "A1_Waveform", "A2_Waveform",
        "A3_Waveform", "A4_Waveform", "A5_Center_Waveform"
    ]
    for col in waveform_cols:
        df[col] = df[col].apply(lambda x: np.array(json.loads(x)))
    return df


def main(filename="waveform_row_data_1786930492.csv"):
    print(f"Loading data from {filename}...")
    df = load_dataset(filename)

    groups = {
        "Ecoflex": {"imax": [], "contrast": []},
        "Cellophane_A": {"imax": [], "contrast": []},
        "Cellophane_B": {"imax": [], "contrast": []},
    }

    print(f"Processing {len(df)} total runs...")

    for _, row in df.iterrows():
        label_id = int(row.get("Label_ID", 0))
        label_name = resolve_label_name(label_id)

        if label_name not in groups:
            continue

        i_max, contrast = extract_center_features(row)
        groups[label_name]["imax"].append(i_max)
        groups[label_name]["contrast"].append(contrast)

    plt.figure(figsize=(10, 6))
    colors = {
        "Ecoflex": "blue",
        "Cellophane_A": "orange",
        "Cellophane_B": "red",
    }

    for label_name, values in groups.items():
        if not values["imax"]:
            continue

        plt.scatter(
            values["contrast"],
            values["imax"],
            c=colors[label_name],
            label=label_name,
            alpha=0.7,
            edgecolors="k",
            s=80,
        )

    plt.title("Center Photodiode: Maximum Intensity vs Optical Contrast")
    plt.xlabel("Optical Contrast")
    plt.ylabel("Maximum Intensity ($I_{max}$)")
    plt.legend(loc="best")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main("waveform_row_data_1786958563.csv")