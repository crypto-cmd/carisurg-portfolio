"""Plot each expt4 CSV file as its own graph."""

import os
from pathlib import Path

import matplotlib

backend = "Agg"
if os.name == "nt":
    for candidate in ("TkAgg", "QtAgg", "MacOSX"):
        try:
            matplotlib.use(candidate, force=True)
            backend = candidate
            break
        except Exception:
            continue
else:
    if os.environ.get("DISPLAY"):
        for candidate in ("TkAgg", "QtAgg"):
            try:
                matplotlib.use(candidate, force=True)
                backend = candidate
                break
            except Exception:
                continue
    else:
        matplotlib.use("Agg", force=True)
        backend = "Agg"

import matplotlib.pyplot as plt
import pandas as pd


def main():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    csv_files = sorted(
        path
        for path in data_dir.iterdir()
        if path.is_file() and path.name.startswith("expt4_readings_") and path.suffix.lower() == ".csv"
    )

    if not csv_files:
        print("No expt4 CSV files found in the root data folder.")
        return

    print(f"Found {len(csv_files)} expt4 CSV file(s).")

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, on_bad_lines="skip")
        if df.empty:
            continue

        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
        sensor_columns = [column for column in df.columns if column != "timestamp" and str(column).startswith("sensor_")]

        if not sensor_columns:
            print(f"Skipping file without sensor columns: {csv_file.name}")
            continue

        df[sensor_columns] = df[sensor_columns].apply(pd.to_numeric, errors="coerce")
        min_max_by_sensor = {
            column: (df[column].min(skipna=True), df[column].max(skipna=True))
            for column in sensor_columns
        }

        print(f"\n{csv_file.name}")
        for column in sensor_columns:
            min_value, max_value = min_max_by_sensor[column]
            print(f"  {column}: min={min_value:.3f}, max={max_value:.3f}")

        plt.figure(figsize=(10, 5))
        for column in sensor_columns:
            plt.plot(df.index, df[column], label=column)

        summary_text = "\n".join(
            f"{column}: min={min_max_by_sensor[column][0]:.2f}, max={min_max_by_sensor[column][1]:.2f}"
            for column in sensor_columns
        )
        plt.gca().text(
            1.02,
            1.0,
            summary_text,
            transform=plt.gca().transAxes,
            va="top",
            fontsize=8,
            bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "gray"},
        )

        plt.xlabel("Sample index")
        plt.ylabel("Sensor value")
        plt.title(csv_file.name)
        plt.legend()
        plt.tight_layout(rect=(0, 0, 0.82, 1))

        output_path = csv_file.with_suffix(".png")
        plt.savefig(output_path, dpi=200, bbox_inches="tight")
        print(f"Saved plot to {output_path}")

        if backend.lower() != "agg":
            plt.show()

        plt.close()


if __name__ == "__main__":
    main()
