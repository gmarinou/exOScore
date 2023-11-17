import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
from tkinter import filedialog
import tkinter as tk

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
    df = pd.read_csv(filename, usecols=['Timestamp', 'IR_FSR', 'IL_FSR'])

    # Split values using the specified delimiter
    split_values_r = df['IR_FSR'].str.split(delimiter, expand=True)
    split_values_l = df['IL_FSR'].str.split(delimiter, expand=True)
    timestamp = df['Timestamp']

    # Convert the split values to numeric
    split_values_r = split_values_r.apply(pd.to_numeric, errors='coerce')
    split_values_l = split_values_l.apply(pd.to_numeric, errors='coerce')

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

# Function to create and save a new CSV file with selected columns
def save_peaks_to_csv(timestamps_r, heel_r_peaks, timestamps_l, heel_l_peaks, additional_filename_part):
    output_filename = f"peaks_data_{additional_filename_part}.csv"

    df = pd.DataFrame({
        'Timestamps_r': timestamps_r,
        'Heel_r_Peaks': heel_r_peaks,
        'Timestamps_l': timestamps_l,
        'Heel_l_Peaks': heel_l_peaks
    })

    df.to_csv(output_filename, index=False)
    return output_filename

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
fsr_columns = ['IR_FSR_1', 'IR_FSR_2', 'IR_FSR_3', 'IL_FSR_1', 'IL_FSR_2', 'IL_FSR_3']

for column in fsr_columns:
    data[column] = butter_lowpass_filter(data[column], cutoff_frequency, sampling_rate)

# Set the threshold equal to the average amplitude
threshold_r = FSR_R.mean().mean()
threshold_l = FSR_L.mean().mean()

# Find peaks in filtered_data_1 with the specified threshold
peaks_r, _ = find_peaks(data['IR_FSR_1'], height=threshold_r)
peaks_l, _ = find_peaks(data['IL_FSR_1'], height=threshold_l)

# Prompt user for additional part of the filename
additional_filename_part = input("Enter additional part of the filename: ")

# Save the selected columns to a new CSV file
output_filename = save_peaks_to_csv(timestamps[peaks_r], data['IR_FSR_1'][peaks_r], timestamps[peaks_l], data['IL_FSR_1'][peaks_l], additional_filename_part)

print(f"Data saved to: {output_filename}")