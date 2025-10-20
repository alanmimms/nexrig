import numpy as np
from scipy import fftpack
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
from simParams import *

# Time vector
t = np.arange(0, simulationDuration, 1 / sampleRate)

# --- Load Data from Simulation Files ---
delayedAmplitude = np.loadtxt('amplitude.txt')[:, 1]
gateDriveSignal = np.loadtxt('gateDrive.txt')[:, 1]

# --- Re-run a minimal ideal signal calculation for comparison ---
complexAudio = np.exp(1j * 2 * np.pi * tone1Frequency * t) + np.exp(1j * 2 * np.pi * tone2Frequency * t)
complexRF = complexAudio * np.exp(1j * 2 * np.pi * carrierFrequency * t)
idealSignal = np.real(complexRF)
idealPhase = np.angle(complexRF)
idealAmplitude_plot = np.abs(complexRF)

# --- Corrected Reconstructed Signal Model ---
# This models the filtered output of the Class-E amplifier.
# The `buckDelay` causes a phase error, which leads to intermodulation distortion.
phaseError = 2 * np.pi * carrierFrequency * buckDelay
reconstructedSignal = delayedAmplitude * np.cos(idealPhase - phaseError)


# --- Frequency Domain Analysis ---
n_reconstructed = len(reconstructedSignal)
yf_reconstructed = fftpack.fft(reconstructedSignal)
x_reconstructed = fftpack.fftfreq(n_reconstructed, 1 / sampleRate)

# FFT of the ideal signal
n_ideal = len(idealSignal)
yf_ideal = fftpack.fft(idealSignal)
x_ideal = fftpack.fftfreq(n_ideal, 1 / sampleRate)


# We only care about the positive frequencies
half_n_ideal = n_ideal // 2
half_n_reconstructed = n_reconstructed // 2
ideal_fft_db = 20 * np.log10(np.abs(yf_ideal[:half_n_ideal]))
reconstructed_fft_db = 20 * np.log10(np.abs(yf_reconstructed[:half_n_reconstructed]))

# Normalize the frequency spectra to have a peak at 0 dB
maxPower = np.max(reconstructed_fft_db)
ideal_fft_normalized = ideal_fft_db - maxPower
reconstructed_fft_normalized = reconstructed_fft_db - maxPower


# --- Visualization ---
try:
    # First plot: Time-domain with high-frequency detail
    plt.figure(figsize=(18, 12))
    
    # Plotting the first 2500 samples as requested
    plot_samples = 2500
    
    plt.plot(t[:plot_samples] * 1e6, idealSignal[:plot_samples], label='Ideal Signal')
    plt.plot(t[:plot_samples] * 1e6, reconstructedSignal[:plot_samples], label='Reconstructed Signal')
    plt.title('Time-Domain Signal Comparison (High-Frequency Detail)')
    plt.xlabel('Time (us)')
    plt.ylabel('Amplitude')
    plt.legend(loc="upper right")
    plt.grid(True)
    
    # Second plot: Time-domain showing the full envelope
    plt.figure(figsize=(18, 12))
    plt.plot(t * 1e6, idealAmplitude_plot, label='Ideal Amplitude')
    plt.plot(t * 1e6, delayedAmplitude, label='Delayed Amplitude')
    plt.title('Amplitude Envelope Comparison (Full Simulation Duration)')
    plt.xlabel('Time (us)')
    plt.ylabel('Amplitude')
    plt.legend(loc="upper right")
    plt.grid(True)

    # Plot Frequency-domain signals
    plt.figure(figsize=(18, 12))
    plt.plot(x_ideal[:half_n_ideal], ideal_fft_normalized, label='Ideal Signal')
    plt.plot(x_reconstructed[:half_n_reconstructed], reconstructed_fft_normalized, label='Reconstructed with Delays')
    plt.title('Frequency Spectrum Comparison')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power (dB)')
    
    # Set the frequency range to +/- 1% of the carrier frequency
    frequencyRange = 0.01 * carrierFrequency
    plt.xlim(carrierFrequency - frequencyRange, carrierFrequency + frequencyRange)
    
    # Find the level of the highest spurious frequency
    bin_size = sampleRate / n_reconstructed
    tone1_bin = int((carrierFrequency + tone1Frequency) / bin_size)
    tone2_bin = int((carrierFrequency + tone2Frequency) / bin_size)
    
    spurious_check_db = np.copy(reconstructed_fft_normalized)
    
    window_size_bins = 10
    spurious_check_db[tone1_bin - window_size_bins : tone1_bin + window_size_bins] = -np.inf
    spurious_check_db[tone2_bin - window_size_bins : tone2_bin + window_size_bins] = -np.inf
    
    max_spurious_power = np.max(spurious_check_db)
    
    print(f"Max spurious power level: {max_spurious_power:.2f} dB")
    
    plt.axhline(y=max_spurious_power, color='r', linestyle='--', label='Max Spurious Level')
    
    plt.ylim(-60, 5)
    
    formatter = mtick.FuncFormatter(lambda x, p: format(x / 1e6, '.2f'))
    plt.gca().xaxis.set_major_formatter(formatter)
    
    plt.legend(loc="upper right")
    plt.grid(True)
    
    # Show all created figures simultaneously
    plt.show()

except ImportError:
    print('Matplotlib not found. Install with "pip install matplotlib" to see plots.')
