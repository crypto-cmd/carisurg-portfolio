import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# 1. Recreate the identical filter used in your live script
def apply_lowpass_filter(data, fs=843.06, cutoff=5.0, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def calculate_contrast(filtered_data):
    I_max = np.max(filtered_data)
    I_min = np.min(filtered_data)
    # 1e-6 prevents division by zero
    return (I_max - I_min) / ((I_max + I_min) + 1e-6)

# 2. Load the CSV
# ---> REPLACE THIS with the actual filename from your folder <---
filename = "waveform_row_data_1786904281.csv" 
print(f"Loading data from {filename}...")
df = pd.read_csv(filename)

# 3. Unpack the JSON strings back into usable NumPy arrays
waveform_cols = [
    "A0_Waveform", "A1_Waveform", "A2_Waveform", 
    "A3_Waveform", "A4_Waveform", "A5_Center_Waveform"
]
for col in waveform_cols:
    df[col] = df[col].apply(lambda x: np.array(json.loads(x)))

# 4. Separate the data by material
ecoflex_df = df[df['Material'] == 'Ecoflex']
cello_df = df[df['Material'] == 'Cellophane']

print(f"Found {len(ecoflex_df)} Ecoflex runs and {len(cello_df)} Cellophane runs.")

# Make sure we have at least one of each to compare
if not ecoflex_df.empty and not cello_df.empty:
    # Grab the very first run of each type for this plot
    eco_run = ecoflex_df.iloc[0]
    cello_run = cello_df.iloc[0]

    # Create a time axis for the X-axis (5 seconds total)
    time_axis = np.linspace(0, 5.0, len(eco_run["A5_Center_Waveform"]))

    # Filter the Center PD data for both runs
    eco_center_filtered = apply_lowpass_filter(eco_run["A5_Center_Waveform"])
    cello_center_filtered = apply_lowpass_filter(cello_run["A5_Center_Waveform"])

    eco_contrast = calculate_contrast(eco_center_filtered)
    cello_contrast = calculate_contrast(cello_center_filtered)

    # 5. Set up the visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # --- PLOT 1: Center Photodiode Comparison ---
    ax1.plot(time_axis, eco_center_filtered, label=f'Pure Ecoflex (Contrast: {eco_contrast:.3f})', color='blue', linewidth=2)
    ax1.plot(time_axis, cello_center_filtered, label=f'Cellophane (Contrast: {cello_contrast:.3f})', color='red', linewidth=2)
    
    ax1.set_title('Center Photodiode (A5) Waveform Comparison')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Intensity (Raw ADC Voltage)')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.7)

    # --- PLOT 2: Ring Asymmetry in the Cellophane Run ---
    colors = ['purple', 'orange', 'green', 'brown', 'pink']
    
    # Loop through A0 to A4
    for i, col in enumerate(waveform_cols[:5]): 
        filtered_ring = apply_lowpass_filter(cello_run[col])
        contrast = calculate_contrast(filtered_ring)
        ax2.plot(time_axis, filtered_ring, label=f'Ring A{i} (Contrast: {contrast:.3f})', color=colors[i], linewidth=1.5)

    ax2.set_title(f'Cellophane Run Alignment: Ring Sensors A0-A4 (Run ID {cello_run["Run_ID"]})')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Intensity (Raw ADC Voltage)')
    
    # Place legend outside the plot so it doesn't cover the waves
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax2.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()
    
else:
    print("Error: Missing either Ecoflex or Cellophane data in this CSV. Cannot run comparison.")