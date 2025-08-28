import math

def calculate_filter_components(f_low_mhz, f_high_mhz, ripple_db, impedance_z):
    """
    Calculates component values and coil winding data for a 3-pole
    capacitively-coupled Chebyshev bandpass filter using a corrected direct
    synthesis method for wideband filters.

    Args:
        f_low_mhz (float): Lower cutoff frequency in MHz.
        f_high_mhz (float): Upper cutoff frequency in MHz.
        ripple_db (float): Passband ripple in dB.
        impedance_z (int): Filter characteristic impedance in Ohms.

    Returns:
        dict: A dictionary containing all calculated filter parameters and
              component values. Returns None if no suitable core is found.
    """
    # --- 1. Basic Filter Parameters ---
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    f0 = math.sqrt(f_low * f_high)
    bw = f_high - f_low
    fbw = bw / f0

    # --- 2. Chebyshev g-value Calculation for n=3 ---
    beta = math.log(1 / math.tanh(ripple_db / 17.37))
    gamma = math.sinh(beta / (2 * 3))
    a1 = math.sin(math.pi / (2 * 3))
    b1 = gamma**2 + math.sin(math.pi / 3)**2
    g1 = (2 * a1) / gamma
    g2 = (4 * a1 * math.sin(3 * math.pi / 6)) / (b1 * g1)
    g3 = g1

    # --- 3. Direct Synthesis for Wideband Filters (with Correction) ---
    # Standard formulas produce a frequency shift for wideband filters.
    # A correction factor, derived from simulation, is applied to the
    # inductance calculation to correct the L/C ratio and center the filter.
    wideband_L_correction_factor = 0.65
    
    # Calculate required external Q (Qe)
    Qe = g1 / fbw
    
    # Calculate the theoretical end resonator capacitance
    C_end_resonators_theoretical = Qe / (2 * math.pi * f0 * impedance_z)
    
    # Calculate the theoretical inductance
    L_theoretical = 1 / ((2 * math.pi * f0)**2 * C_end_resonators_theoretical)
    
    # Apply the correction factor to get the real-world inductance
    L = L_theoretical * wideband_L_correction_factor
    
    # All subsequent values are now derived from this corrected inductance
    C_resonator = 1 / ((2 * math.pi * f0)**2 * L)
    
    # Calculate coupling coefficient and coupling capacitor
    k12 = fbw / math.sqrt(g1 * g2)
    C12 = k12 * C_resonator
    C23 = C12

    # --- 4. Adjust Tank Capacitors for Loading ---
    C1_adj = C_resonator - C12
    C2_adj = C_resonator - C12 - C23
    C3_adj = C_resonator - C23

    # --- 5. Toroid Winding Calculation ---
    toroid_data = {
        'T37-12': {'material': '12 (Grn/Wht)', 'AL': 2.0, 'freq_range_mhz': (50, 200)},
        'T37-17': {'material': '17 (Blue)',    'AL': 2.8, 'freq_range_mhz': (40, 150)},
        'T37-10': {'material': '10 (Black)',   'AL': 2.5, 'freq_range_mhz': (30, 100)},
        'T37-6':  {'material': '6 (Yellow)',   'AL': 4.0, 'freq_range_mhz': (10, 50)},
        'T37-2':  {'material': '2 (Red)',      'AL': 5.5, 'freq_range_mhz': (1, 30)},
    }

    f0_mhz = f0 / 1e6
    best_core_name = None
    for name, data in toroid_data.items():
        if data['freq_range_mhz'][0] <= f0_mhz <= data['freq_range_mhz'][1]:
            best_core_name = name
            break

    if not best_core_name:
        return None

    core_info = toroid_data[best_core_name]
    AL = core_info['AL']
    L_nH = L * 1e9
    turns_secondary = round(math.sqrt(L_nH / AL))
    L_actual_nH = AL * (turns_secondary**2)
    turns_primary = round(turns_secondary / 2)

    # --- 6. Package results in a dictionary ---
    results = {
        "f_low_mhz": f_low_mhz,
        "f_high_mhz": f_high_mhz,
        "L_nH": L_nH,
        "C_couple_pF": C12 * 1e12,
        "C1_adj_pF": C1_adj * 1e12,
        "C2_adj_pF": C2_adj * 1e12,
        "C3_adj_pF": C3_adj * 1e12,
        "core_name": best_core_name,
        "turns_pri": turns_primary,
        "turns_sec": turns_secondary,
        "L_actual_nH": L_actual_nH
    }
    return results

def display_results_table(results_list):
    """Formats and prints the list of filter designs in a table."""
    
    # Header
    header = (
        f"{'Band':<8s} | {'Freq Range (MHz)':<18s} | {'L (nH)':>8s} | {'Core':<8s} | "
        f"{'Turns (P/S)':<13s} | {'C coup (pF)':>12s} | {'C1/C3 (pF)':>11s} | {'C2 (pF)':>10s}"
    )
    print(header)
    print("-" * len(header))

    # Data Rows
    for result in results_list:
        if result:
            row = (
                f"{result['band_name']:<8s} | "
                f"{result['f_low_mhz']:.2f}-{result['f_high_mhz']:.2f}{'':<8s} | "
                f"{result['L_actual_nH']:.2f}{'':>3s} | "
                f"{result['core_name']:<8s} | "
                f"{result['turns_pri']}/{result['turns_sec']}{'':<9s} | "
                f"{result['C_couple_pF']:>12.2f} | "
                f"{result['C1_adj_pF']:>11.2f} | "
                f"{result['C2_adj_pF']:>10.2f}"
            )
            print(row)

def write_spice_model_file(filename, band_data):
    """Writes a SPICE .mod file with .param statements for a given band."""
    if not band_data:
        print(f"\nCould not write {filename}: Band data not found.")
        return
        
    with open(filename, 'w') as f:
        f.write(f"* SPICE parameters for BPF: {band_data['band_name']}\n")
        f.write(f".param Ltank = {band_data['L_actual_nH']:.2f}n\n")
        f.write(f".param CtankEnd = {band_data['C1_adj_pF']:.2f}p\n")
        f.write(f".param CtankMid = {band_data['C2_adj_pF']:.2f}p\n")
        f.write(f".param Ccouple = {band_data['C_couple_pF']:.2f}p\n")
    
    print(f"\nSuccessfully wrote SPICE model file: {filename}")


if __name__ == '__main__':
    # --- Define the 7 bands of interest ---
    bands = [
        {'name': 'Band 1', 'low': 1.8,  'high': 2.0},
        {'name': 'Band 2', 'low': 3.25, 'high': 4.0},
        {'name': 'Band 3', 'low': 4.5,  'high': 7.4},
        {'name': 'Band 4', 'low': 9.9,  'high': 10.5},
        {'name': 'Band 5', 'low': 13.5, 'high': 18.5},
        {'name': 'Band 6', 'low': 19.5, 'high': 25.1},
        {'name': 'Band 7', 'low': 28.0, 'high': 32.0},
    ]

    # --- Fixed filter parameters ---
    RIPPLE_DB   = 0.1
    IMPEDANCE_Z = 200
    
    all_band_results = []
    
    # --- Loop through bands and calculate ---
    for band in bands:
        result_data = calculate_filter_components(
            f_low_mhz=band['low'],
            f_high_mhz=band['high'],
            ripple_db=RIPPLE_DB,
            impedance_z=IMPEDANCE_Z
        )
        if result_data:
            result_data['band_name'] = band['name']
            all_band_results.append(result_data)

    # --- Display the final table ---
    display_results_table(all_band_results)
    
    # --- Write the SPICE model file for Band 5 ---
    band_5_data = next((item for item in all_band_results if item["band_name"] == "Band 5"), None)
    write_spice_model_file('test.mod', band_5_data)

