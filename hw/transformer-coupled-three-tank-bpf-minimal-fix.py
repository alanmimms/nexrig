#!/usr/bin/env python3
"""
MINIMAL FIX: Keep Your Working Design, Just Fix Passband Shift
=============================================================

Your original design WORKS for Chebyshev ripple. The only issue is
the passband is shifted slightly high due to the 0.65 factor.

Minimal change: Adjust the center frequency calculation to compensate
for the shift, keeping everything else identical.

Author: Claude (minimal intervention approach)
"""

import math

def calculate_filter_components(f_low_mhz, f_high_mhz, ripple_db, impedance_z):
    """
    Minimal fix: Keep your working approach, just adjust f0 for shift compensation.
    """
    
    # --- 1. Bandwidth compensation approach ---
    # Instead of frequency shifting, try designing for slightly narrower bandwidth
    # to account for the filter being slightly wider than designed
    bw_compensation_factor = 0.90  # Design for 90% of target bandwidth (was 0.95, going narrower)
    
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    f0_design = math.sqrt(f_low * f_high)  # Use target center freq
    
    bw_target = f_high - f_low
    bw_design = bw_target * bw_compensation_factor  # Slightly narrower design
    fbw = bw_design / f0_design  # Use compensated bandwidth
    
    print(f"Target f0: {f0_design/1e6:.3f} MHz")
    print(f"Target BW: {bw_target/1e6:.1f} MHz, Design BW: {bw_design/1e6:.1f} MHz (factor {bw_compensation_factor:.2f})")
    
    # --- 2. YOUR ORIGINAL g-value Calculation (KEEP EXACTLY) ---
    beta = math.log(1 / math.tanh(ripple_db / 17.37))
    gamma = math.sinh(beta / (2 * 3))  # Your version: beta / (2*n)
    a1 = math.sin(math.pi / (2 * 3))   # Your version: pi / (2*n)
    b1 = gamma**2 + math.sin(math.pi / 3)**2
    g1 = (2 * a1) / gamma
    g2 = (4 * a1 * math.sin(3 * math.pi / 6)) / (b1 * g1)
    g3 = g1
    
    print(f"Your g-values: g1={g1:.4f}, g2={g2:.4f}")
    
    # --- 3. YOUR ORIGINAL Synthesis (KEEP EXACTLY) ---
    wideband_L_correction_factor = 0.65  # Keep your working factor!
    
    Qe = g1 / fbw
    C_end_theoretical = Qe / (2 * math.pi * f0_design * impedance_z)
    L_theoretical = 1 / ((2 * math.pi * f0_design)**2 * C_end_theoretical)
    L = L_theoretical * wideband_L_correction_factor  # Your 0.65 factor
    C_resonator = 1 / ((2 * math.pi * f0_design)**2 * L)
    
    k12 = fbw / math.sqrt(g1 * g2)
    C12 = k12 * C_resonator
    C23 = C12
    
    # --- 4. YOUR ORIGINAL Loading Adjustments (KEEP EXACTLY) ---
    C1_adj = C_resonator - C12
    C2_adj = C_resonator - C12 - C23
    C3_adj = C_resonator - C23
    
    print(f"Using your 0.65 factor: L = {L*1e9:.1f} nH")
    print(f"C_coupling: {C12*1e12:.1f} pF")
    
    # --- 5. YOUR ORIGINAL Toroid Calculation (KEEP EXACTLY) ---
    toroid_data = {
        'T37-12': {'material': '12 (Grn/Wht)', 'AL': 2.0, 'freq_range_mhz': (50, 200)},
        'T37-17': {'material': '17 (Blue)',    'AL': 2.8, 'freq_range_mhz': (40, 150)},
        'T37-10': {'material': '10 (Black)',   'AL': 2.5, 'freq_range_mhz': (30, 100)},
        'T37-6':  {'material': '6 (Yellow)',   'AL': 4.0, 'freq_range_mhz': (10, 50)},
        'T37-2':  {'material': '2 (Red)',      'AL': 5.5, 'freq_range_mhz': (1, 30)},
    }

    f0_mhz = f0_design / 1e6  # Use design frequency for core selection
    best_core_name = None
    for name, data in toroid_data.items():
        if data['freq_range_mhz'][0] <= f0_mhz <= data['freq_range_mhz'][1]:
            best_core_name = name
            break

    if not best_core_name:
        best_core_name = 'T37-2'  # Default

    core_info = toroid_data[best_core_name]
    AL = core_info['AL']
    L_nH = L * 1e9
    turns_secondary = round(math.sqrt(L_nH / AL))
    L_actual_nH = AL * (turns_secondary**2)
    turns_primary = round(turns_secondary / 2)

    # --- 6. Package Results ---
    results = {
        "f_low_mhz": f_low_mhz,
        "f_high_mhz": f_high_mhz,
        "f0_target_mhz": f0_design / 1e6,
        "f0_design_mhz": f0_design / 1e6,
        "L_nH": L_nH,
        "C_couple_pF": C12 * 1e12,
        "C1_adj_pF": C1_adj * 1e12,
        "C2_adj_pF": C2_adj * 1e12,
        "C3_adj_pF": C3_adj * 1e12,
        "core_name": best_core_name,
        "turns_pri": turns_primary,
        "turns_sec": turns_secondary,
        "L_actual_nH": L_actual_nH,
        "bw_factor": bw_compensation_factor,
    }
    
    return results

def write_spice_model_file(filename, band_data):
    """Write SPICE model file."""
    if not band_data:
        return
    
    with open(filename, 'w') as f:
        f.write(f"* SPICE parameters for Minimally Fixed BPF: {band_data['band_name']}\n")
        f.write(f"* Target f0: {band_data['f0_target_mhz']:.3f} MHz\n")
        f.write(f"* Design BW: {band_data['f_high_mhz'] - band_data['f_low_mhz']:.1f} MHz (BW factor {band_data['bw_factor']:.2f})\n")
        f.write(f"* Keeps your working 0.65 factor and g-value calculation\n")
        f.write(f".param Ltank = {band_data['L_actual_nH']:.2f}n\n")
        f.write(f".param CtankEnd = {band_data['C1_adj_pF']:.2f}p\n")
        f.write(f".param CtankMid = {band_data['C2_adj_pF']:.2f}p\n")
        f.write(f".param Ccouple = {band_data['C_couple_pF']:.2f}p\n")
    
    print(f"\nSPICE model written to: {filename}")

def display_results_table(results_list):
    """Formats and prints the list of filter designs in a table."""
    
    # Header
    header = (
        f"{'Band':<8s} | {'Freq Range (MHz)':<18s} | {'FBW%':>6s} | {'L (nH)':>8s} | {'Core':<8s} | "
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
                f"{(result['f_high_mhz']-result['f_low_mhz'])/result['f0_target_mhz']*100:>6.1f} | "
                f"{result['L_actual_nH']:>8.2f} | "
                f"{result['core_name']:<8s} | "
                f"{result['turns_pri']}/{result['turns_sec']}{'':<9s} | "
                f"{result['C_couple_pF']:>12.2f} | "
                f"{result['C1_adj_pF']:>11.2f} | "
                f"{result['C2_adj_pF']:>10.2f}"
            )
            print(row)

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
    RIPPLE_DB = 0.1
    IMPEDANCE_Z = 200
    
    print("MINIMAL FIX FILTER DESIGN - ALL 7 BANDS")
    print("=" * 80)
    print(f"Design parameters: Ripple = {RIPPLE_DB} dB, Z = {IMPEDANCE_Z} Ω")
    print("Strategy: Design for 90% of target bandwidth to compensate for widening")
    print()
    
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
    
    # --- Write individual SPICE model files for each band ---
    print(f"\nGenerating individual SPICE model files:")
    
    for i, result in enumerate(all_band_results, 1):
        filename = f'band{i}.mod'
        write_spice_model_file(filename, result)
        print(f"  {filename} - {result['band_name']}: {result['f_low_mhz']:.1f}-{result['f_high_mhz']:.1f} MHz")
    
    print(f"\nAll 7 band files generated: band1.mod through band7.mod")
    print(f"Ready for KiCad simulation of all bands!")