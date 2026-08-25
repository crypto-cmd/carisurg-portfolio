from firmware.utils.reader import read_arduino_binary
import numpy as np
import matplotlib.pyplot as plt
import time

from scipy.interpolate import griddata

if __name__ == "__main__":
    COM_PORT = 'COM8' # *** UPDATE THIS TO YOUR PORT ***
    BAUD_RATE = 115200
    BUFFER_SIZE = 1024 # How many samples to average for a stable image

    # --- 1. Define the Spatial Geometry (Pin -> X,Y Coordinates) ---
    # We define a coordinate system (0,0 is center) mapping to the 
    # user's physical requirement for A0-A5.
    
    # Vertices of a unit pentagon pointing down (360/5 = 72 degree steps)
    R = 1.0 # Radius for vertices
    
    # Pin positions arranged [A0, A1, A2, A3, A4, A5]
    pin_coords = np.array([
        (R * np.cos(np.radians(54)), R * np.sin(np.radians(54))),   # A0: Top Right
        (R * np.cos(np.radians(126)), R * np.sin(np.radians(126))), # A1: Top Left
        (R * np.cos(np.radians(198)), R * np.sin(np.radians(198))), # A2: Bottom Left (Inferred)
        (0.0, -R),                                                  # A3: Bottom (cos(270), sin(270))
        (R * np.cos(np.radians(342)), R * np.sin(np.radians(342))), # A4: Bottom Right (Inferred)
        (0.0, 0.0)                                                  # A5: Center
    ])
    
    # Generate the high-resolution grid for interpolation
    grid_size = 100
    grid_x, grid_y = np.mgrid[-1.1:1.1:grid_size*1j, -1.1:1.1:grid_size*1j]

    # Pre-define a "mask" to only show data inside the pentagon (keeps image clean)
    # This step is technically optional but makes the visualization far professional.
    mask = (grid_x**2 + grid_y**2) <= R**2 

    # --- 2. Set up the Live Matplotlib Graph ---
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Initialize the heatmap (initially blank/zeros)
    heatmap = ax.imshow(np.zeros((grid_size, grid_size)), extent=(-1.1, 1.1, -1.1, 1.1),
                        origin='lower', cmap='plasma', interpolation='bilinear',
                        vmin=0, vmax=1023) # Set range to 10-bit ADC limit
    
    # Overlay the physical sensor locations as white dots
    ax.scatter(pin_coords[:, 0], pin_coords[:, 1], c='white', edgecolors='black', s=80, zorder=10)
    
    # Add labels to the sensors (A0-A5)
    labels = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']
    for i, label in enumerate(labels):
        # Slightly offset labels for clarity
        offset_x = 0.08 if pin_coords[i, 0] >= 0 else -0.15
        offset_y = 0.08 if pin_coords[i, 1] >= 0 else -0.15
        if label == 'A5': offset_y = 0.1 # Move center label up
        
        ax.text(pin_coords[i, 0] + offset_x, pin_coords[i, 1] + offset_y, label, 
                color='white', weight='bold', fontsize=12, zorder=11)

    ax.set_title("Live Photodiode Spatial Intensity (A0-A5 Pentagon Geometry)")
    ax.set_aspect('equal') # Keep the geometry locked
    ax.axis('off') # Hide coordinate axes for a clean look
    fig.colorbar(heatmap, label='10-bit Photodiode Value') # Add intensity scale
    
    # --- 3. Process the Data Stream ---
    data_buffer = np.zeros((BUFFER_SIZE, 6))
    buffer_index = 0
    sensor_stream = read_arduino_binary(COM_PORT, BAUD_RATE)
    
    print("Buffering initial data snapshot...")
    
    for readings in sensor_stream:
        data_buffer[buffer_index, :] = readings
        buffer_index += 1
        print(f"Readings: {readings} | Buffer Index: {buffer_index}/{BUFFER_SIZE}", end='\r')
        
        # When the buffer is full, update the spatial map
        if buffer_index >= BUFFER_SIZE:
            
            # 1. Average all 1024 samples to get stable intensity snapshot for each pin
            pin_values = np.mean(data_buffer, axis=0)
            
            # 2. Interpolate: Map 6 data points onto the 100x100 grid
            # Using 'cubic' provides smooth gradients; 'linear' is faster.
            grid_z = griddata(pin_coords, pin_values, (grid_x, grid_y), method='cubic')
            
            # 3. Clean the image: Set outside mask area to NaN (optional, for aesthetics)
            # grid_z[~mask] = np.nan

            # 4. Update the live heatmap image
            heatmap.set_data(grid_z.T) # Transpose needed for imshow alignment
            
            # Draw and pause briefly to render UI
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # Reset buffer index for next update
            buffer_index = 0