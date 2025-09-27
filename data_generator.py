import numpy as np
import pandas as pd

# --- Parameters ---
SAMPLES = 200      # Samples per cycle
CYCLES = 5         # Number of cycles to simulate
N_SAMPLES_TOTAL = SAMPLES * CYCLES
N_EVENTS = 1000    # Number of data events to generate for each class
FREQ = 50          # 50 Hz

def generate_normal(v_peak=325):
    """Generates a clean 3-phase sine wave."""
    t = np.linspace(0, CYCLES / FREQ, N_SAMPLES_TOTAL)
    va = v_peak * np.sin(2 * np.pi * FREQ * t)
    vb = v_peak * np.sin(2 * np.pi * FREQ * t - 2 * np.pi / 3)
    vc = v_peak * np.sin(2 * np.pi * FREQ * t + 2 * np.pi / 3)
    noise = np.random.normal(0, 0.5, (3, N_SAMPLES_TOTAL))
    return np.vstack([va, vb, vc]) + noise

def generate_lg_fault(v_peak=325, fault_magnitude=0.5):
    """Generates a waveform with a voltage sag on one phase."""
    normal_waves = generate_normal(v_peak)
    fault_start_index = SAMPLES * 2
    normal_waves[0, fault_start_index:] *= fault_magnitude # Sag on Phase A
    return normal_waves

def generate_arcing_fault(v_peak=325):
    """Generates a waveform with high-frequency noise, simulating an arc."""
    normal_waves = generate_normal(v_peak)
    fault_start_index = SAMPLES * 2
    arc_noise = np.random.normal(0, 15, N_SAMPLES_TOTAL - fault_start_index)
    normal_waves[1, fault_start_index:] += arc_noise # Arc on Phase B
    return normal_waves

# --- Generate the Dataset ---
data = []
labels = []

print("Generating data... this might take a moment.")
for _ in range(N_EVENTS):
    data.append(generate_normal().flatten())
    labels.append(0) # 0 for Normal

for _ in range(N_EVENTS):
    data.append(generate_lg_fault().flatten())
    labels.append(1) # 1 for LG Fault

for _ in range(N_EVENTS):
    data.append(generate_arcing_fault().flatten())
    labels.append(2) # 2 for Arcing Fault

# --- Create and Save DataFrame ---
df = pd.DataFrame(data)
df['label'] = labels
df = df.sample(frac=1).reset_index(drop=True)
df.to_csv('fault_data.csv', index=False)
print(f"✅ Successfully generated fault_data.csv with shape: {df.shape}")