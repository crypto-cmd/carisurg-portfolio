from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


# Ensure imports work whether this file is run from /firmware or /firmware/graphs
FIRMWARE_DIR = Path(__file__).resolve().parents[1]
if str(FIRMWARE_DIR) not in sys.path:
	sys.path.insert(0, str(FIRMWARE_DIR))

from firmware.utils.reader import read_arduino_binary


if __name__ == "__main__":
	COM_PORT = "COM8"  # *** UPDATE THIS TO YOUR PORT ***
	BAUD_RATE = 115200
	WINDOW_SIZE = 400  # Number of recent samples to display

	labels = ["A0", "A1", "A2", "A3", "A4", "A5"]
	colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]

	# Rolling buffer of shape (WINDOW_SIZE, 6)
	y_buffer = np.zeros((WINDOW_SIZE, 6), dtype=float)
	x = np.arange(WINDOW_SIZE)

	plt.ion()
	fig, ax = plt.subplots(figsize=(12, 6))

	lines = []
	for i, label in enumerate(labels):
		(line,) = ax.plot(x, y_buffer[:, i], label=label, color=colors[i], linewidth=1.8)
		lines.append(line)

	ax.set_title("Live Photodiode Readings (A0-A5)")
	ax.set_xlabel("Recent Samples")
	ax.set_ylabel("ADC Value")
	ax.set_ylim(0, 1)
	ax.set_xlim(0, WINDOW_SIZE - 1)
	ax.grid(True, alpha=0.3)
	ax.legend(loc="upper right", ncol=3)
	fig.tight_layout()

	sensor_stream = read_arduino_binary(COM_PORT, BAUD_RATE)
	print("Streaming... Close the plot window or press Ctrl+C to stop.")

	update_every = 5  # Redraw every N samples for smoother performance
	sample_count = 0

	try:
		for readings in sensor_stream:
			sample_count += 1

			# Shift buffer left and append newest 6-channel sample
			y_buffer[:-1] = y_buffer[1:]
			y_buffer[-1] = readings

			if sample_count % update_every == 0:
				for i, line in enumerate(lines):
					line.set_ydata(y_buffer[:, i])

				current_max = float(np.max(y_buffer))
				y_top = min(max(1.0, current_max * 1.05), 1023)  # 5% headroom
				ax.set_ylim(0, y_top)

				fig.canvas.draw()
				fig.canvas.flush_events()

	except KeyboardInterrupt:
		print("\nStopped by user.")
