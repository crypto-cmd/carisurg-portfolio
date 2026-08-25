"""Plot the saved sensor readings from expt2."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main():
    csv_path = Path(__file__).resolve().parents[1] / "data" / "expt2_readings.csv"
    df = pd.read_csv(csv_path)

    if df.empty:
        print("No data found in the CSV file.")
        return

    plt.figure(figsize=(12, 6))
    for column in df.columns[1:]:
        plt.plot(df.index, df[column], label=column)

    plt.xlabel("Sample index")
    plt.ylabel("Sensor value")
    plt.title("Experiment 2 sensor readings")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
