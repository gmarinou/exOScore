import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from tkinter import filedialog
import tkinter as tk
from scipy.signal import find_peaks

# Function to design a Butterworth filter
def butter_lowpass_filter(data, cutoff_frequency, sampling_rate, order=4):
    nyquist = 0.5 * sampling_rate
    normal_cutoff = cutoff_frequency / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Function to import CSV file, extract "IR_FSR" column, and split values
def import_and_extract(filename, delimiter='|'):
    # Read only the "IR_FSR" column
    df = pd.read_csv(filename, usecols=['Timestamp','IR_FSR','IL_FSR'])

    # Split values using the specified delimiter
    split_values_r = df['IR_FSR'].str.split(delimiter, expand=True)
    split_values_l = df['IL_FSR'].str.split(delimiter, expand=True)
    timestamp = df['Timestamp']


    # Convert the split values to numeric
    split_values_r = split_values_r.apply(pd.to_numeric, errors='coerce')
    split_values_l = split_values_r.apply(pd.to_numeric, errors='coerce')

    # Rename columns right
    num_columns_r = split_values_r.shape[1]
    column_names_r = [f'IR_FSR_{i + 1}' for i in range(num_columns_r)]
    split_values_r.columns = column_names_r
    # Rename columns left
    num_columns_l = split_values_l.shape[1]
    column_names_l = [f'IL_FSR_{i + 1}' for i in range(num_columns_l)]
    split_values_l.columns = column_names_l

    # Concatenate 'Timestamp' and split 'IR_FSR' columns
    result = pd.concat([timestamp, split_values_r, split_values_l], axis=1)


    return result

# Function to prompt user for CSV file selection
def select_csv_file(initial_dir=None):
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Set the initial directory to the user's home folder
    if initial_dir is None:
        initial_dir = os.path.expanduser("/Users/gmarinou/Projects/TWIN/DATA")

    file_path = filedialog.askopenfilename(
        title="Select CSV file",
        initialdir=initial_dir,  # Set the initial directory
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    return file_path

# Prompt user to select a CSV file
filename = select_csv_file()

# Import CSV, extract columns, and split FSR values
data = import_and_extract(filename)
# Access columns
timestamps = data['Timestamp']
FSR_R = data[['IR_FSR_1', 'IR_FSR_2', 'IR_FSR_3']]
FSR_L = data[['IL_FSR_1', 'IL_FSR_2', 'IL_FSR_3']]

# Set the cutoff frequency and sampling rate
cutoff_frequency = 0.5  # Adjust as needed based on your data characteristics
sampling_rate = 2.0  # Adjust based on the sampling rate of your FSR data

# Design and apply the Butterworth filter to each column
heel_r = butter_lowpass_filter(FSR_R['IR_FSR_1'], cutoff_frequency, sampling_rate)
fifth_r = butter_lowpass_filter(FSR_R['IR_FSR_2'], cutoff_frequency, sampling_rate)
first_r = butter_lowpass_filter(FSR_R['IR_FSR_3'], cutoff_frequency, sampling_rate)
heel_l = butter_lowpass_filter(FSR_L['IL_FSR_1'], cutoff_frequency, sampling_rate)
fifth_l = butter_lowpass_filter(FSR_L['IL_FSR_2'], cutoff_frequency, sampling_rate)
first_l = butter_lowpass_filter(FSR_L['IL_FSR_3'], cutoff_frequency, sampling_rate)

# Set the threshold equal to the average amplitude
threshold_r = heel_r.mean()
threshold_l = heel_l.mean()

# Find peaks in filtered_data_1 with the specified threshold
peaks_r, _ = find_peaks(heel_r, height=threshold_r)
peaks_l, _ = find_peaks(heel_l, height=threshold_l)

# Plot the original and filtered data for comparison
#plt.figure(figsize=(10, 6))
#plt.plot(FSR_R['IR_FSR_1'], label='Original Data 1', alpha=0.8)
#plt.plot(heel, label='Heel', linewidth=2)
#plt.plot(FSR_R['IR_FSR_2'], label='Original Data 2', alpha=0.8)
#plt.plot(fifth_m, label='Fifth Metatarsal', linewidth=2)
#plt.plot(FSR_R['IR_FSR_3'], label='Original Data 3', alpha=0.8)
#plt.plot(first_m, label='First Metatarsal', linewidth=2)
#plt.title('Butterworth Low-Pass Filter')
#plt.xlabel('Sample Index')
#plt.ylabel('Amplitude')
#plt.legend()
#plt.show()

# Plot the original and filtered data along with detected peaks
plt.figure(figsize=(10, 6))
plt.plot(timestamps,heel_r, label='Heel_r', linewidth=2)
plt.plot(timestamps[peaks_r], heel_r[peaks_r], "x", label="Peaks", markersize=8, color='r')
plt.title('Peaks Detection in right FSR Heel')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.legend()
plt.show()

# Plot the original and filtered data along with detected peaks
plt.figure(figsize=(10, 6))
plt.plot(timestamps,heel_l, label='Heel_l', linewidth=2)
plt.plot(timestamps[peaks_l], heel_l[peaks_l], "x", label="Peaks", markersize=8, color='r')
plt.title('Peaks Detection in left FSR Heel')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.legend()
plt.show()
