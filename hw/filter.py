import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import math

# --- Configuration ---
RIPPLE_DB = 0.1  # Passband ripple in dB for Chebyshev filter
FILTER_ORDER = 3 # The order of the filter
Z0 = 200.0       # System impedance in Ohms (high-impedance design)

# Amateur Radio Bands (in MHz)
# Each tuple: (band_name, f_start, f_stop)
HAM_BANDS = [
    ("160m", 1.8, 2.0),
    ("80m", 3.5, 4.0),
    ("60m", 5.3305, 5.405),
    ("40m", 7.0, 7.3),
    ("30m", 10.1, 10.15),
    ("20m", 14.0, 14.35),
    ("17m", 18.068, 18.168),
    ("15m", 21.0, 21.45),
    ("12m", 24.89, 24.99),
    ("10m", 28.0, 29.7),
]

# --- Main Script Logic ---

def design_chebyshev_lowpass_prototypes(order, ripple_db):
    """
    Calculates the g-values (prototype element values) for a Chebyshev lowpass filter.
    These values are for a filter with a cutoff frequency of 1 rad/s and 1-ohm impedance.
    """
    g = np.zeros(order + 2)
    beta = math.log(1.0 / math.tanh(ripple_db / (40.0 / math.log(10))))
    gamma = math.sinh(beta / (2.0 * order))
    a = np.zeros(order + 1)
    b = np.zeros(order + 1)

    for k in range(1, order + 1):
        a[k] = math.sin(((2 * k - 1) * math.pi) / (2.0 * order))
        b[k] = gamma**2 + math.sin((k * math.pi) / order)**2

    g[0] = 1.0  # Source resistance
    g[1] = (2 * a[1]) / gamma

    for k in range(2, order + 1):
        g[k] = (4 * a[k - 1] * a[k]) / (b[k - 1] * g[k - 1])

    # Determine termination resistance based on filter order
    if order % 2 == 0:
        g[order + 1] = 1.0 / (math.tanh(beta / 4.0)**2) # Even order
    else:
        g[order + 1] = 1.0 # Odd order

    return g

def transform_to_bandpass(g_values, f_center, bw):
    """
    Transforms lowpass prototype values to capacitively-coupled bandpass component values.
    Returns a dictionary of component values.
    """
    w0 = 2 * np.pi * f_center
    FBW = bw / f_center # Fractional Bandwidth

    # This design makes all resonators identical, based on the g1 value.
    # This is a simplification but should yield a working filter.
    # L_res and C_res are calculated to resonate at f_center.
    L_res = (Z0 * g_values[1]) / (2 * np.pi * bw)
    C_res = 1 / ((w0**2) * L_res)

    # Calculate coupling coefficients (k) based on standard filter theory
    k12 = FBW / math.sqrt(g_values[1] * g_values[2])
    k23 = FBW / math.sqrt(g_values[2] * g_values[3])

    # Calculate coupling capacitors from the coupling coefficient and resonator capacitance
    C_couple12 = k12 * C_res
    C_couple23 = k23 * C_res
    
    # All resonators are identical in this simplified model
    L1 = L_res
    C1 = C_res
    L2 = L_res
    C2 = C_res
    L3 = L_res
    C3 = C_res

    return {
        "L1": L1, "C1": C1,
        "L2": L2, "C2": C2,
        "L3": L3, "C3": C3,
        "C12": C_couple12,
        "C23": C_couple23
    }


def generate_netlist(band_name, f_start, f_stop, components):
    """Generates the ngspice .cir netlist file for a given filter design."""
    f_center = (f_start + f_stop) / 2
    # Widen sweep to see skirts better, especially for narrow bands
    sweep_multiplier = max(4.0, 100.0 / (((f_stop - f_start) / f_center) * 100.0))
    f_sweep_start = f_center - (f_stop - f_start) * sweep_multiplier
    f_sweep_stop = f_center + (f_stop - f_start) * sweep_multiplier
    f_sweep_start = max(f_sweep_start, 0.1) # Ensure frequency is positive

    netlist_content = f"""
* {band_name} 3-Pole Chebyshev Bandpass Filter Simulation
* Center Freq: {f_center:.3f} MHz, BW: {f_stop - f_start:.3f} MHz
* Impedance: {Z0} Ohms

.options savecurrents

* --- Source and Load ---
* Thevenin equivalent of a 1V 50-ohm source transformed 1:4 to 200 ohms.
* V_thevenin = 1V * sqrt(200/50) = 2V
* R_thevenin = 50 * (200/50) = 200 Ohms
V1 1 0 AC 2
R_source 1 2 {Z0}

* --- Filter Components ---
* Resonator 1 (Shunt LC at node 2)
L1 2 0 {components['L1']:.6e}
C1 2 0 {components['C1']:.6e}

* Coupling Capacitor
C12 2 3 {components['C12']:.6e}

* Resonator 2 (Shunt LC at node 3)
L2 3 0 {components['L2']:.6e}
C2 3 0 {components['C2']:.6e}

* Coupling Capacitor
C23 3 9 {components['C23']:.6e}

* Resonator 3 (Shunt LC at node 9)
L3 9 0 {components['L3']:.6e}
C3 9 0 {components['C3']:.6e}

* --- Load ---
* The filter is terminated in 200 Ohms, representing the transformed 50 Ohm load.
R_load 9 0 {Z0}

* --- Analysis ---
.control
    ac lin 801 {f_sweep_start * 1e6} {f_sweep_stop * 1e6}
    * We measure voltage at the load (node 9)
    let Vout = V(9)
    * Insertion Loss is defined as 20*log10(V_load / V_source_available)
    * V_source_available is the voltage at the load if Z_load = Z_source, which is V_source / 2.
    * Since our V_source is 2V, V_source_available is 1V.
    * So, IL(dB) = 20*log10(mag(Vout) / 1) = 20*log10(mag(Vout))
    let VdB = 20*log10(mag(Vout))
    wrdata results/{band_name}.dat VdB
    exit
.endc

.end
"""
    filename = f"netlists/{band_name}.cir"
    with open(filename, "w") as f:
        f.write(netlist_content)
    return filename

def run_ngspice(netlist_file):
    """Runs ngspice in batch mode."""
    print(f"  Simulating {netlist_file}...")
    try:
        # Using -b for batch mode, -o for log file
        # We redirect stdout and stderr to DEVNULL to keep the console clean
        subprocess.run(
            ["ngspice", "-b", "-o", f"logs/{os.path.basename(netlist_file)}.log", netlist_file],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("  Simulation complete.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  ERROR: ngspice simulation failed for {netlist_file}.")
        print(f"  Make sure 'ngspice' is installed and in your system's PATH.")
        print(f"  Error details: {e}")
        return False

def plot_results(band_name, f_start, f_stop):
    """Plots the simulation results from the data file."""
    data_file = f"results/{band_name}.dat"
    plot_file = f"plots/{band_name}_response.png"
    
    try:
        # ngspice output is space-delimited. First column is frequency, second is VdB.
        data = np.loadtxt(data_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"  ERROR: Could not read or parse results file {data_file}. Skipping plot.")
        print(f"  Error details: {e}")
        return

    freqs = data[:, 0] / 1e6  # Convert Hz to MHz
    vdb = data[:, 1]

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(freqs, vdb, label='Filter Response', color='#007acc', linewidth=2)

    # --- Formatting ---
    ax.set_title(f"{band_name} Bandpass Filter Response (Order={FILTER_ORDER}, Z={Z0}Ω)", fontsize=16)
    ax.set_xlabel("Frequency (MHz)", fontsize=12)
    ax.set_ylabel("Insertion Loss (dB)", fontsize=12)
    
    # Set Y-axis limits for better visualization
    # Add a check to prevent error on empty slice
    passband_slice = vdb[(freqs >= f_start) & (freqs <= f_stop)]
    if passband_slice.size > 0:
        passband_max = np.max(passband_slice)
        ax.set_ylim(passband_max - 80, passband_max + 2)
    else:
        # Fallback if no points are in the passband, though unlikely with linear sweep
        ax.set_ylim(-80, 2)

    
    # Highlight the passband region
    ax.axvspan(f_start, f_stop, color='green', alpha=0.2, label=f'{band_name} Passband')
    
    # Add grid and legend
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    
    # Add text box with component values
    components = design_chebyshev_bandpass_from_band(f_start*1e6, f_stop*1e6)
    text_str = "Component Values:\n"
    text_str += f"L (all): {components['L1']*1e6:.3f} uH\n"
    text_str += f"C (res): {components['C1']*1e12:.3f} pF\n"
    text_str += f"C12: {components['C12']*1e12:.3f} pF\n"
    text_str += f"C23: {components['C23']*1e12:.3f} pF\n"
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.35, text_str, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close(fig)
    print(f"  Plot saved to {plot_file}")

def design_chebyshev_bandpass_from_band(f_start_hz, f_stop_hz):
    """Helper function to run design steps for a given band."""
    f_center = (f_start_hz + f_stop_hz) / 2.0
    bw = f_stop_hz - f_start_hz
    
    # 1. Get lowpass prototype g-values
    g_values = design_chebyshev_lowpass_prototypes(FILTER_ORDER, RIPPLE_DB)
    
    # 2. Transform to bandpass component values
    components = transform_to_bandpass(g_values, f_center, bw)
    return components

def main():
    """Main execution function."""
    # Create directories if they don't exist
    for d in ["netlists", "results", "logs", "plots"]:
        os.makedirs(d, exist_ok=True)

    print("--- Starting HF Filter Design and Simulation ---")
    
    for band_name, f_start_mhz, f_stop_mhz in HAM_BANDS:
        print(f"\nProcessing {band_name}...")
        
        f_start_hz = f_start_mhz * 1e6
        f_stop_hz = f_stop_mhz * 1e6

        # Design the filter
        components = design_chebyshev_bandpass_from_band(f_start_hz, f_stop_hz)
        print(f"  Designed Components for {band_name}:")
        print(f"    Resonator L: {components['L1']*1e6:.4f} uH")
        print(f"    Resonator C: {components['C1']*1e12:.4f} pF")
        print(f"    Coupling C12: {components['C12']*1e12:.4f} pF")
        print(f"    Coupling C23: {components['C23']*1e12:.4f} pF")
        
        # Generate the SPICE netlist for this design
        netlist_file = generate_netlist(band_name, f_start_mhz, f_stop_mhz, components)
        
        # Run the simulation
        if run_ngspice(netlist_file):
            # Plot the results if simulation was successful
            plot_results(band_name, f_start_mhz, f_stop_mhz)

    print("\n--- All bands processed successfully! ---")

if __name__ == "__main__":
    main()
