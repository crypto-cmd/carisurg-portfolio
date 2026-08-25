"""Subtract one expt4 CSV from another and plot the difference."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def load_sensor_frame(csv_path):
    df = pd.read_csv(csv_path)
    sensor_cols = [col for col in df.columns if col.startswith("sensor_")]
    if not sensor_cols:
        raise ValueError(f"No sensor columns found in {csv_path}")

    df[sensor_cols] = df[sensor_cols].apply(pd.to_numeric, errors="coerce")
    return df, sensor_cols


def main():
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data" / "expt4" / "sample_1"

    reference_name = "expt4_readings_20260811_063910.csv"
    target_name = "expt4_readings_20260811_064131.csv"

    reference_path = data_dir / reference_name
    target_path = data_dir / target_name

    if not reference_path.exists() or not target_path.exists():
        raise FileNotFoundError("One or both of the requested CSV files were not found.")

    ref_df, sensor_cols = load_sensor_frame(reference_path)
    target_df, _ = load_sensor_frame(target_path)

    common_length = min(len(ref_df), len(target_df))
    ref_subset = ref_df.iloc[:common_length].reset_index(drop=True)
    target_subset = target_df.iloc[:common_length].reset_index(drop=True)

    difference = target_subset[sensor_cols].subtract(ref_subset[sensor_cols])
    difference.index = range(common_length)

    fig, ax = plt.subplots(figsize=(12, 6))
    for col in sensor_cols:
        ax.plot(difference.index, difference[col], label=col, linewidth=1.2)

    ax.axhline(0, color="black", linestyle="--", linewidth=1.0)
    ax.set_title(f"{target_name} - {reference_name}")
    ax.set_xlabel("Sample index")
    ax.set_ylabel("Difference")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", ncol=2, fontsize=8)
    fig.tight_layout()

    output_path = data_dir / "difference_063910_vs_064131.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Saved difference plot to {output_path}")

    try:
        plt.show()
    except Exception:
        pass


if __name__ == "__main__":
    main()
