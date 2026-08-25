import numpy as np
def median_filter(data, window_size):
    """
    Applies a median filter to the input data.
    
    Parameters:
        data (list or np.ndarray): The input data to be filtered.
        window_size (int): The size of the moving window. Must be an odd integer.
        
    Returns:
        np.ndarray: The filtered data.
    """
    if window_size % 2 == 0:
        # Still allow even window sizes but warn the user
        print("Warning: Even window size provided. Consider using an odd window size for better results.")
        
    
    # Convert input data to a numpy array for easier manipulation
    data = np.asarray(data)
    
    # Pad the data at the edges to handle boundary conditions
    pad_width = window_size // 2
    padded_data = np.pad(data, pad_width, mode='edge')
    
    # Prepare an array to hold the filtered results
    filtered_data = np.zeros_like(data)
    
    # Apply the median filter
    for i in range(len(data)):
        window = padded_data[i:i + window_size]
        filtered_data[i] = np.median(window)
    
    return filtered_data

import numpy as np
from scipy.signal import butter, filtfilt

def apply_lowpass_filter(data, fs, cutoff=5.0, order=4):
    # The Nyquist frequency is half the sampling rate
    nyquist = 0.5 * fs
    
    # Normalize the cutoff frequency for the digital filter
    normal_cutoff = cutoff / nyquist
    
    # Design the Butterworth filter coefficients (b, a)
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    
    # Apply the zero-phase forward-backward filter
    filtered_data = filtfilt(b, a, data)
    
    return filtered_data
