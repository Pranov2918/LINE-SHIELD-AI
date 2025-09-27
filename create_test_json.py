import pandas as pd
import json

# Load the dataset you created earlier
try:
    df = pd.read_csv('fault_data.csv')
except FileNotFoundError:
    print("Error: 'fault_data.csv' not found. Please run 'data_generator.py' first.")
    exit()

# --- Select a single fault to test ---
# We'll pick the 5th row from your dataset as an example.
test_row_index = 5
test_waveform_data = df.iloc[test_row_index]

# Separate the waveform values from the label
label = int(test_waveform_data['label'])
waveform = test_waveform_data.drop('label').tolist()

# The labels mean: 0=Normal, 1=LG Fault, 2=Arcing Fault
label_map = {0: 'Normal', 1: 'LG_Fault', 2: 'Arcing_Fault'}
expected_fault_type = label_map.get(label, 'Unknown')

# --- Create the JSON structure the API expects ---
output_data = {
    "waveform": waveform
}

# --- Save the JSON file ---
file_name = f"test_{expected_fault_type}.json"
with open(file_name, 'w') as json_file:
    json.dump(output_data, json_file)

print(f"✅ Successfully created '{file_name}'!")
print(f"This file contains a waveform for an event of type: '{expected_fault_type}'")
print("You can now upload this file to the dashboard.")