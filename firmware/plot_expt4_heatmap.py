from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.interpolate import Rbf


data_dir = Path(__file__).resolve().parents[1] / "data"
csv_files = sorted(data_dir.glob("expt4_readings_*.csv"))

if not csv_files:
    raise FileNotFoundError("No expt4 CSV files found in the data directory.")

latest_csv = max(csv_files, key=lambda path: path.stat().st_mtime)
df = pd.read_csv(latest_csv, parse_dates=["timestamp"])
sensor_columns = ['sensor_0', 'sensor_1', 'sensor_2', 'sensor_3', 'sensor_4', 'sensor_5']
df[sensor_columns] = df[sensor_columns].apply(pd.to_numeric, errors='coerce')

# Define the physical layout of the sensors based on the specified parameters
angles_deg = [54, 126, 198, 270, 342]
angles_rad = np.radians(angles_deg)

# Convert polar coordinates to Cartesian for the 5 outer sensors (radius = 1)
x_coords = np.cos(angles_rad)
y_coords = np.sin(angles_rad)

# Add Sensor 5 at the center origin (0, 0)
x_coords = np.append(x_coords, 0)
y_coords = np.append(y_coords, 0)

# Create a dense grid for spatial interpolation
grid_x, grid_y = np.mgrid[-1.2:1.2:100j, -1.2:1.2:100j]

fig, ax = plt.subplots(figsize=(8, 7))
plt.subplots_adjust(bottom=0.2)

# Global min and max for consistent color scaling across all frames
vmin = df[sensor_columns].min().min()
vmax = df[sensor_columns].max().max()

cax = ax.pcolormesh(grid_x, grid_y, np.zeros_like(grid_x), shading='auto', 
                    cmap='magma', vmin=vmin, vmax=vmax)
fig.colorbar(cax, ax=ax, label='Sensor Value')

# Overlay the physical sensor locations
ax.scatter(x_coords, y_coords, color='cyan', edgecolors='black', s=100, zorder=5)
for i, (x, y) in enumerate(zip(x_coords, y_coords)):
    ax.text(x + 0.05, y + 0.05, f'S{i}', color='white', weight='bold', zorder=6)

time_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, color='white', weight='bold')

slider_ax = plt.axes([0.2, 0.05, 0.6, 0.03])
slider = Slider(slider_ax, "frame", 0, len(df) - 1, valinit=0, valstep=1)


def update(frame_idx):
    frame_idx = int(frame_idx)
    row = df.iloc[frame_idx]
    values = np.asarray(row[sensor_columns].to_numpy(dtype=float), dtype=float)

    rbfi = Rbf(x_coords, y_coords, values, function='linear')
    interpolated_grid = rbfi(grid_x, grid_y)

    radius_mask = np.sqrt(grid_x**2 + grid_y**2) > 1.05
    interpolated_grid[radius_mask] = np.nan

    cax.set_array(interpolated_grid.ravel())
    time_text.set_text(f"Time: {row['timestamp'].strftime('%H:%M:%S.%f')[:-3]}")
    ax.set_title(f"Spatiotemporal Sensor Animation | frame {frame_idx}")
    ax.axis('off')
    fig.canvas.draw_idle()


slider.on_changed(update)
update(0)

plt.tight_layout()
plt.show()