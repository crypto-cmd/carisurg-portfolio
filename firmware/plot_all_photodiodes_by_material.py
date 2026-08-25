import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


PHOTODIODE_COLUMNS = [
    "A0_Waveform",
    "A1_Waveform",
    "A2_Waveform",
    "A3_Waveform",
    "A4_Waveform",
    "A5_Center_Waveform",
]


LABEL_COLOR_MAP = {
    "Ecoflex": "#1f77b4",
    "Cellophane_A": "#d62728",
    "Cellophane_B": "#2ca02c",
    "Cellophane": "#d62728",
}


def apply_lowpass_filter(data, fs=843.06, cutoff=5.0, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return filtfilt(b, a, data)


def resolve_label_name(label_id):
    mapping = {
        0: "No Button",
        1: "Ecoflex",
        2: "Cellophane_A",
        3: "Cellophane_B",
    }
    return mapping.get(int(label_id), "Unknown")


def normalize_label_name(row):
    label_id = row.get("Label_ID")
    if pd.notna(label_id):
        resolved = resolve_label_name(label_id)
        if resolved in LABEL_COLOR_MAP:
            return resolved

    material = str(row.get("Material", "")).strip()
    if material.lower() == "ecoflex":
        return "Ecoflex"
    if "cellophane" in material.lower():
        return "Cellophane_A"
    return "Unknown"


def load_dataset(filename):
    df = pd.read_csv(filename)
    for col in PHOTODIODE_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: np.asarray(json.loads(x), dtype=float)
                if isinstance(x, str) else np.asarray(x, dtype=float)
            )
    return df


def main(filename="waveform_row_data_1786958563.csv"):
    root = Path(__file__).resolve().parents[1]
    df = load_dataset(root / filename)

    fig, axes = plt.subplots(len(PHOTODIODE_COLUMNS), 1, figsize=(14, 18), sharex=True)
    if len(PHOTODIODE_COLUMNS) == 1:
        axes = [axes]

    for ax, photodiode in zip(axes, PHOTODIODE_COLUMNS):
        for _, row in df.iterrows():
            label_name = normalize_label_name(row)
            if label_name == "Unknown":
                continue

            waveform = np.asarray(row[photodiode], dtype=float)
            if waveform.size == 0:
                continue

            filtered = apply_lowpass_filter(waveform)
            time_axis = np.linspace(0, 5.0, len(filtered))
            ax.plot(
                time_axis,
                filtered,
                color=LABEL_COLOR_MAP[label_name],
                alpha=0.35,
                linewidth=1.4,
            )

        title_name = photodiode.replace("_Waveform", "").replace("_Center", " Center")
        ax.set_title(f"{title_name} — all runs")
        ax.set_ylabel("Intensity")
        ax.grid(True, linestyle="--", alpha=0.6)

    axes[-1].set_xlabel("Time (s)")

    legend_handles = [
        plt.Line2D([0], [0], color=LABEL_COLOR_MAP[name], lw=2, label=name)
        for name in ["Ecoflex", "Cellophane_A", "Cellophane_B"]
        if name in LABEL_COLOR_MAP
    ]
    fig.legend(handles=legend_handles, loc="upper right", bbox_to_anchor=(0.98, 0.98))
    fig.suptitle("Photodiode traces by material class", fontsize=16)
    fig.tight_layout(rect=[0, 0, 0.9, 0.97])

    out_dir = root / "output"
    out_dir.mkdir(exist_ok=True)
    output_path = out_dir / "all_photodiodes_by_material.png"
    fig.savefig(output_path, dpi=200)
    print(f"Saved figure to {output_path}")
    plt.show()


if __name__ == "__main__":
    main()
