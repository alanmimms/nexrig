import numpy as np
from simParams import *

# Time vector
t = np.arange(0, simulationDuration, 1 / sampleRate)

# --- Signal Generation and Decomposition ---
# Create a complex baseband signal directly from the two tones
complexAudio = np.exp(1j * 2 * np.pi * tone1Frequency * t) + np.exp(1j * 2 * np.pi * tone2Frequency * t)

# Upconvert the complex baseband signal to the RF carrier frequency
complexRF = complexAudio * np.exp(1j * 2 * np.pi * carrierFrequency * t)

# Get the ideal amplitude and phase signals
idealAmplitude = np.abs(complexRF)
idealPhase = np.angle(complexRF)

# --- Model Phase Drift and Delays ---
# Model a slowly evolving baseline phase
baselinePhaseDrift = np.linspace(0, totalPhaseDrift, len(t))

# Add the phase drift to the ideal phase signal
phaseWithDrift = idealPhase + baselinePhaseDrift

# Model the buck converter delay on the amplitude path
buckDelaySamples = int(buckDelay * sampleRate)
delayedAmplitude = np.roll(idealAmplitude, buckDelaySamples)


# --- FPGA Model ---
# This function models the FPGA's logic to generate a gate drive signal.
# It simulates the FPGA's NCO and phase-locking loop (PLL) logic
# to track and correct for the input phase, including the baseline drift.
def modelFpga(inputPhase, amplitude):
    # A simple phase correction model to perfectly compensate for the drift
    # In a real system, this would be a control loop (e.g., a PI controller)
    # The FPGA would correct for the drift and any phase error
    compensatedPhase = inputPhase - baselinePhaseDrift
    
    # Generate a square wave based on the compensated phase
    # This models the NCO output driving a digital gate.
    gateDriveSignal = np.sign(np.sin(compensatedPhase))
    
    return gateDriveSignal

gateDriveSignal = modelFpga(phaseWithDrift, delayedAmplitude)


# --- Output Data for Ngspice Simulation ---
# Combine time and signal data into a single 2-column array for Ngspice PWL source
amplitudeData = np.vstack((t, delayedAmplitude)).T
gateDriveData = np.vstack((t, gateDriveSignal)).T

# Save the data in a format suitable for ngspice
np.savetxt('amplitude.txt', amplitudeData, fmt='%e', delimiter=' ')
np.savetxt('gateDrive.txt', gateDriveData, fmt='%e', delimiter=' ')

print('Amplitude and gate drive signals have been saved to amplitude.txt and gateDrive.txt')
