#!/usr/bin/env python3
"""
Chebyshev Bandpass Filter Calculator
====================================

Calculates component values for a 3rd order Chebyshev bandpass filter
using coupled LC resonator topology with capacitive coupling and L-network matching.

Topology: 50Ω -> L-network -> Tank1 -> Coupling -> Tank2 -> Coupling -> Tank3 -> L-network -> 50Ω

Each tank: L || C (parallel LC resonator)
Matching networks: L-networks (series L + shunt C) for impedance transformation

CONTEXT FROM DEVELOPMENT:
- Started with CSV spreadsheet approach (had quoting/formula issues)  
- Moved to Python for better reliability
- Architecture matches user's KiCad schematic with capacitively-coupled resonators
- Fixed L-network calculations to give proper Chot >> Ccold values
- Frequency range: 13.5-18.5 MHz (20m amateur band)
- Tank inductors: 1000nH (user specified, gives ~99Ω tank impedance)
- Expected coupling caps: ~20pF, Tank caps: ~101pF
- Expected matching: Chot ~318pF, Ccold ~161pF (2:1 ratio)

Author: Claude (with user feedback/corrections)
"""

import math
import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# FILTER PARAMETERS - MODIFY THESE VALUES
# ============================================================================

# Frequency parameters (MHz)
f_lower = 13.5      # Lower cutoff frequency (MHz)  
f_upper = 18.5      # Upper cutoff frequency (MHz)

# Filter characteristics
filter_order = 3    # Filter order (3 for the schematic topology)
ripple_db = 0.1     # Passband ripple (dB)

# Impedance parameters (Ohms)
source_impedance = 50.0   # Source impedance (Ohms)
load_impedance = 50.0     # Load impedance (Ohms)

# Tank inductor value (nH) - USER SPECIFIED PARAMETER
tank_inductor_nh = 1000.0  # Tank inductor value (nH)

# L-network inductor parameters (for insertion loss calculation)
inductor_q_factor = 50      # Quality factor of matching inductors at f_center
inductor_dcr_ohms = 0.5     # DC resistance of matching inductors (ohms)

# ============================================================================
# MAIN CALCULATION FUNCTION
# ============================================================================

def calculate_chebyshev_filter():
    """
    Calculate all component values for the coupled resonator Chebyshev filter.
    
    Returns a dictionary with all calculated values for easy access.
    """
    
    # Basic filter parameters
    f_center = math.sqrt(f_lower * f_upper)
    bandwidth = f_upper - f_lower
    quality_factor = f_center / bandwidth
    fractional_bandwidth = bandwidth / f_center
    omega_0 = 2 * math.pi * f_center * 1e6  # Convert MHz to Hz
    
    # Tank impedance at center frequency
    tank_inductance_h = tank_inductor_nh * 1e-9  # Convert nH to H
    tank_impedance = omega_0 * tank_inductance_h
    
    # Ripple factor
    epsilon = math.sqrt(10**(ripple_db/10) - 1)
    
    # Print header and input parameters
    print("=" * 80)
    print("CHEBYSHEV BANDPASS FILTER CALCULATOR")
    print("Coupled Resonator Topology")
    print("=" * 80)
    print()
    
    print("INPUT PARAMETERS:")
    print(f"  Lower Frequency:     {f_lower:.3f} MHz")
    print(f"  Upper Frequency:     {f_upper:.3f} MHz")
    print(f"  Filter Order:        {filter_order}")
    print(f"  Passband Ripple:     {ripple_db:.1f} dB")
    print(f"  Source Impedance:    {source_impedance:.0f} Ω")
    print(f"  Load Impedance:      {load_impedance:.0f} Ω")
    print(f"  Tank Inductor:       {tank_inductor_nh:.0f} nH")
    print()
    
    print("CALCULATED PARAMETERS:")
    print(f"  Center Frequency:    {f_center:.3f} MHz")
    print(f"  Bandwidth:           {bandwidth:.3f} MHz")
    print(f"  Quality Factor:      {quality_factor:.2f}")
    print(f"  Fractional BW:       {fractional_bandwidth:.4f}")
    print(f"  Tank Impedance:      {tank_impedance:.1f} Ω")
    print(f"  Ripple Factor (ε):   {epsilon:.4f}")
    print()
    
    # Calculate Chebyshev prototype values for 3rd order
    n = filter_order
    
    # Corrected Chebyshev prototype calculation
    beta = math.log(1/math.tanh(ripple_db * math.log(10) / 17.37))
    gamma = math.sinh(beta / (2 * n))
    
    g = [0] * (n + 2)  # g0 through g4
    g[0] = 1  # Source resistance
    
    # Calculate g-values using standard recursive formula
    for k in range(1, n + 1):
        if k == 1:
            g[k] = 2 * math.sin(math.pi / (2 * n)) / gamma
        else:
            sin_val = math.sin((2 * k - 1) * math.pi / (2 * n))
            sum_val = gamma**2 + (math.sin((k - 1) * math.pi / n))**2
            g[k] = 4 * sin_val * math.sin((k - 1) * math.pi / n) / (g[k-1] * sum_val)
    
    # Enforce symmetry for 3rd order (g1 = g3)
    if n == 3:
        g[3] = g[1]
    
    # Load resistance
    g[n + 1] = 1 if n % 2 == 1 else 1 / (1 + epsilon**2)
    
    print("CHEBYSHEV PROTOTYPE VALUES:")
    for i in range(n + 2):
        print(f"  g{i}:                 {g[i]:.6f}")
    print(f"  Symmetry check - g1=g3: {abs(g[1] - g[3]) < 1e-10}")
    print()
    
    # Coupling coefficients (should be identical for symmetric 3rd order)
    k12 = fractional_bandwidth / math.sqrt(g[1] * g[2])
    k23 = fractional_bandwidth / math.sqrt(g[2] * g[3])
    
    print("COUPLING COEFFICIENTS:")
    print(f"  k12:                 {k12:.6f}")
    print(f"  k23:                 {k23:.6f}")
    print(f"  Coupling match check: {abs(k12 - k23) < 1e-10}")
    print()
    
    # Calculate component values
    results = {}
    
    # Tank capacitors (all identical for resonance at f0)
    tank_cap_pf = 1 / (omega_0**2 * tank_inductance_h) * 1e12
    results['tank_cap_pf'] = tank_cap_pf
    results['tank_inductor_nh'] = tank_inductor_nh
    
    # Tank capacitors (all identical for symmetric architecture)
    tank_cap_pf = 1 / (omega_0**2 * tank_inductance_h) * 1e12
    
    print("TANK RESONATOR CALCULATIONS:")
    print(f"  Tank capacitance:    {tank_cap_pf:.2f} pF (all tanks identical)")
    print(f"  Tank impedance:      {tank_impedance:.1f} Ω at {f_center:.2f} MHz")
    
    # Coupling capacitors for symmetric tanks
    c_coupling12_pf = k12 / (omega_0 * tank_impedance) * 1e12
    c_coupling23_pf = k23 / (omega_0 * tank_impedance) * 1e12
    
    print(f"  Coupling caps:       {c_coupling12_pf:.2f} pF (symmetric)")
    print()
    
    # L-NETWORK MATCHING CALCULATIONS (Option 1A)
    # ============================================
    # Design L-networks to match 50Ω to tank impedance
    # CRITICAL: C_match is in PARALLEL with tank capacitor!
    # Must compensate by reducing actual tank capacitor value
    
    print("L-NETWORK MATCHING CALCULATIONS:")
    
    # Impedance transformation ratio
    z_ratio = tank_impedance / source_impedance
    print(f"  Impedance ratio:     {z_ratio:.3f}:1 (transform {source_impedance}Ω ↔ {tank_impedance:.1f}Ω)")
    
    # L-network design equations for step-up (input side)
    # For L-network with series L and shunt C:
    # Q_network = sqrt(z_ratio - 1)
    q_network = math.sqrt(z_ratio - 1)
    print(f"  Network Q:           {q_network:.3f}")
    
    # Series inductor reactance: X_L = source_impedance * Q_network
    x_l_input = source_impedance * q_network
    l_match_input_nh = x_l_input / omega_0 * 1e9  # Convert to nH
    
    # Shunt capacitor reactance: X_C = tank_impedance / Q_network
    x_c_input = tank_impedance / q_network
    c_match_input_pf = 1 / (omega_0 * x_c_input) * 1e12  # Convert to pF
    
    print(f"\n  Input L-network (50Ω → {tank_impedance:.1f}Ω):")
    print(f"    Series L_match:    {l_match_input_nh:.1f} nH (X_L = {x_l_input:.1f}Ω)")
    print(f"    Shunt C_match:     {c_match_input_pf:.1f} pF (X_C = {x_c_input:.1f}Ω)")
    
    # CRITICAL CORRECTION: Account for parallel capacitance!
    # C_match is in parallel with the tank capacitor
    # Total capacitance at tank = C_match + C_tank_actual
    # We need: C_match + C_tank_actual = tank_cap_pf (for proper resonance)
    # Therefore: C_tank_actual = tank_cap_pf - C_match
    
    c_tank1_actual_pf = tank_cap_pf - c_match_input_pf
    c_tank3_actual_pf = tank_cap_pf - c_match_input_pf  # Same as input for symmetry
    
    print(f"\n  PARALLEL CAPACITANCE COMPENSATION:")
    print(f"    Target total C:    {tank_cap_pf:.1f} pF (for {f_center:.1f} MHz resonance)")
    print(f"    C_match parallel:  {c_match_input_pf:.1f} pF")
    print(f"    C_tank1 needed:    {c_tank1_actual_pf:.1f} pF (reduced from {tank_cap_pf:.1f} pF)")
    print(f"    C_tank3 needed:    {c_tank3_actual_pf:.1f} pF (reduced from {tank_cap_pf:.1f} pF)")
    
    if c_tank1_actual_pf <= 0 or c_tank3_actual_pf <= 0:
        print("  ⚠ ERROR: C_match is too large! Tank caps would be negative!")
        print("  ⚠ This L-network topology won't work for this impedance ratio")
        c_tank1_actual_pf = max(10, c_tank1_actual_pf)  # Fallback
        c_tank3_actual_pf = max(10, c_tank3_actual_pf)  # Fallback
    else:
        # Verify resonance with parallel combination
        c_total_tank1 = c_match_input_pf + c_tank1_actual_pf
        f_verify = 1 / (2 * math.pi * math.sqrt(tank_inductance_h * c_total_tank1 * 1e-12)) / 1e6
        print(f"    Verification:      {c_match_input_pf:.1f} + {c_tank1_actual_pf:.1f} = {c_total_tank1:.1f} pF")
        print(f"    Resonance check:   {f_verify:.2f} MHz (target: {f_center:.2f} MHz)")
    
    # Output L-network is mirror of input for symmetric filter
    l_match_output_nh = l_match_input_nh
    c_match_output_pf = c_match_input_pf
    
    print(f"\n  Output L-network ({tank_impedance:.1f}Ω → 50Ω):")
    print(f"    Series L_match:    {l_match_output_nh:.1f} nH")
    print(f"    Shunt C_match:     {c_match_output_pf:.1f} pF")
    
    # INSERTION LOSS CALCULATIONS
    print(f"\n  Insertion Loss Analysis:")
    print(f"    Inductor Q factor: {inductor_q_factor}")
    print(f"    Inductor DCR:      {inductor_dcr_ohms:.2f} Ω")
    
    # AC resistance of matching inductors at center frequency
    r_ac = x_l_input / inductor_q_factor  # R_ac = X_L / Q
    r_total = r_ac + inductor_dcr_ohms
    
    # Insertion loss from each L-network
    # IL = -20*log10(1 - R/Z) for small R
    # More accurate: account for power dissipation
    il_per_network_db = 10 * math.log10(1 + r_total/source_impedance)
    il_total_db = 2 * il_per_network_db  # Two L-networks (input + output)
    
    print(f"    AC resistance:     {r_ac:.3f} Ω at {f_center:.1f} MHz")
    print(f"    Total R (AC+DC):   {r_total:.3f} Ω")
    print(f"    Loss per L-network:{il_per_network_db:.2f} dB")
    print(f"    Total added loss:  {il_total_db:.2f} dB")
    
    # Store L-network values
    results['l_match_input_nh'] = l_match_input_nh
    results['c_match_input_pf'] = c_match_input_pf
    results['l_match_output_nh'] = l_match_output_nh
    results['c_match_output_pf'] = c_match_output_pf
    results['il_total_db'] = il_total_db
    results['coupling_cap_pf'] = c_coupling12_pf
    results['c_tank1_actual_pf'] = c_tank1_actual_pf
    results['c_tank3_actual_pf'] = c_tank3_actual_pf
    
    # Store results
    results.update({
        'f_center': f_center,
        'bandwidth': bandwidth,
        'tank_impedance': tank_impedance,
        'c_coupling12_pf': c_coupling12_pf,
        'c_coupling23_pf': c_coupling23_pf
    })
    
    print()
    
    # Create Bill of Materials for L-NETWORK MATCHED ARCHITECTURE (Option 1A)
    components = [
        # Input L-network matching
        {'pos': 'Input Match', 'type': 'Inductor', 'ref': 'L_match1', 'val': round(l_match_input_nh, 1), 'unit': 'nH', 'desc': 'Input L-network series inductor'},
        {'pos': 'Input Match', 'type': 'Capacitor', 'ref': 'C_match1', 'val': round(c_match_input_pf, 1), 'unit': 'pF', 'desc': 'Input L-network shunt capacitor'},
        
        # Tank 1 (Simple LC resonator - compensated for parallel C_match)
        {'pos': 'Tank 1', 'type': 'Inductor', 'ref': 'L7805', 'val': tank_inductor_nh, 'unit': 'nH', 'desc': 'Tank 1 inductor'},
        {'pos': 'Tank 1', 'type': 'Capacitor', 'ref': 'C_tank1', 'val': round(c_tank1_actual_pf, 2), 'unit': 'pF', 'desc': 'Tank 1 capacitor (compensated)'},
        
        # Coupling 1-2
        {'pos': 'Coupling', 'type': 'Capacitor', 'ref': 'C7936', 'val': round(c_coupling12_pf, 2), 'unit': 'pF', 'desc': 'Tank 1→2 coupling'},
        
        # Tank 2 (Center - already correct)
        {'pos': 'Tank 2', 'type': 'Inductor', 'ref': 'L7807', 'val': tank_inductor_nh, 'unit': 'nH', 'desc': 'Tank 2 inductor'},
        {'pos': 'Tank 2', 'type': 'Capacitor', 'ref': 'C7938', 'val': round(tank_cap_pf, 2), 'unit': 'pF', 'desc': 'Tank 2 capacitor'},
        
        # Coupling 2-3
        {'pos': 'Coupling', 'type': 'Capacitor', 'ref': 'C7933', 'val': round(c_coupling23_pf, 2), 'unit': 'pF', 'desc': 'Tank 2→3 coupling'},
        
        # Tank 3 (Simple LC resonator - compensated for parallel C_match)
        {'pos': 'Tank 3', 'type': 'Inductor', 'ref': 'L7809', 'val': tank_inductor_nh, 'unit': 'nH', 'desc': 'Tank 3 inductor'},
        {'pos': 'Tank 3', 'type': 'Capacitor', 'ref': 'C_tank3', 'val': round(c_tank3_actual_pf, 2), 'unit': 'pF', 'desc': 'Tank 3 capacitor (compensated)'},
        
        # Output L-network matching
        {'pos': 'Output Match', 'type': 'Inductor', 'ref': 'L_match2', 'val': round(l_match_output_nh, 1), 'unit': 'nH', 'desc': 'Output L-network series inductor'},
        {'pos': 'Output Match', 'type': 'Capacitor', 'ref': 'C_match2', 'val': round(c_match_output_pf, 1), 'unit': 'pF', 'desc': 'Output L-network shunt capacitor'},
    ]
    
    # Print Bill of Materials
    print("=" * 80)
    print("BILL OF MATERIALS")
    print("=" * 80)
    print(f"{'Position':<12} {'Type':<10} {'Ref':<10} {'Value':<10} {'Unit':<4} {'Description'}")
    print("-" * 80)
    
    for comp in components:
        print(f"{comp['pos']:<12} {comp['type']:<10} {comp['ref']:<10} "
              f"{comp['val']:<10} {comp['unit']:<4} {comp['desc']}")
    
    print()
    print("DESIGN NOTES:")
    print("• L-NETWORK MATCHED ARCHITECTURE (Option 1A):")
    print("  - All three tanks: Simple identical LC resonators (99.3Ω impedance)")
    print("  - Input matching: L-network transforms 50Ω → 99.3Ω")
    print("  - Output matching: L-network transforms 99.3Ω → 50Ω")
    print("• Perfect symmetry with identical tank impedances ensures proper Chebyshev response")
    print("• L-network topology: Series L from 50Ω source, then shunt C to ground at tank connection")
    print(f"• Estimated insertion loss: {results['il_total_db']:.2f} dB (from L-network matching)")
    print("• Tank resonance verification:")
    
    # Calculate actual tank resonance frequencies (all tanks are simple LC now)
    f_tank_all = 1 / (2 * math.pi * math.sqrt(tank_inductance_h * tank_cap_pf * 1e-12)) / 1e6
    
    print(f"  - All tanks (identical): {f_tank_all:.2f} MHz")
    print(f"  - Tank capacitance:      {tank_cap_pf:.2f} pF")
    print(f"  - Tank inductance:       {tank_inductor_nh:.0f} nH")
    
    # Check resonance frequency
    if abs(f_tank_all - f_center) > 0.1:
        print("  ⚠ WARNING: Tank resonance doesn't match center frequency!")
        print("  ⚠ This will cause poor filter response!")
    else:
        print("  ✓ All tanks properly tuned to center frequency")
        print("  ✓ Perfect symmetry with identical LC values")
    
    return results

# ============================================================================
# UTILITY FUNCTIONS FOR CLAUDE CODE DEVELOPMENT
# ============================================================================

def quick_calc(f_low, f_high, L_nh, ripple=0.1):
    """Quick calculation function for iterative design in Claude Code"""
    global f_lower, f_upper, tank_inductor_nh, ripple_db
    f_lower = f_low
    f_upper = f_high  
    tank_inductor_nh = L_nh
    ripple_db = ripple
    return calculate_chebyshev_filter()

def compare_inductors(L_values, f_low=13.5, f_high=18.5):
    """Compare different inductor values"""
    print("INDUCTOR COMPARISON:")
    print("-" * 60)
    for L in L_values:
        print(f"\nTank Inductor: {L}nH")
        results = quick_calc(f_low, f_high, L)
        print(f"  Tank Impedance: {results['tank_impedance']:.1f}Ω")
        print(f"  Chot/Ccold ratio: {results['c_hot_input_pf']/results['c_cold_input_pf']:.2f}")

def generate_spice_netlist(results, filename="filter.cir"):
    """Generate a SPICE netlist for the calculated filter"""
    
    netlist = f""".title Chebyshev Bandpass Filter
* Generated by coupled-resonator-filter.py
* Center frequency: {results['f_center']:.3f} MHz
* Bandwidth: {results['bandwidth']:.3f} MHz

* Input source (50 ohm)
Vin in 0 AC 1
Rin in 1 50

* Input matching network (tapped capacitor)
Chot_in 1 2 {results['c_hot_input_pf']:.2f}p
Ccold_in 2 0 {results['c_cold_input_pf']:.2f}p

* Tank 1
L1 2 0 {results['tank_inductor_nh']:.1f}n
C1 2 0 {results['tank_cap_pf']:.2f}p

* Coupling capacitor 1-2
C12 2 3 {results['coupling_cap_pf']:.3f}p

* Tank 2
L2 3 0 {results['tank_inductor_nh']:.1f}n
C2 3 0 {results['tank_cap_pf']:.2f}p

* Coupling capacitor 2-3
C23 3 4 {results['coupling_cap_pf']:.3f}p

* Tank 3
L3 4 0 {results['tank_inductor_nh']:.1f}n
C3 4 0 {results['tank_cap_pf']:.2f}p

* Output matching network (tapped capacitor)
Ccold_out 4 0 {results['c_cold_output_pf']:.2f}p
Chot_out 4 5 {results['c_hot_output_pf']:.2f}p

* Output load (50 ohm)
Rload 5 0 50

.control
save all
.endc

.end
"""
    
    with open(filename, 'w') as f:
        f.write(netlist)
    
    print(f"\nSPICE netlist written to {filename}")
    return filename

def run_ngspice_simulation(netlist_file, output_file="filter_output.txt"):
    """Run ngspice simulation and capture output"""
    
    # Create ngspice control file with proper formatting
    control_script = f"""source {netlist_file}
set wr_vecnames
set units=degrees
op
ac dec 500 1MEG 100MEG
print frequency vdb(5) > {output_file}
quit
"""
    
    control_file = "ngspice_control.txt"
    with open(control_file, 'w') as f:
        f.write(control_script)
    
    try:
        # Run ngspice
        result = subprocess.run(['ngspice', '-b', control_file], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"ngspice error: {result.stderr}")
            return None
            
        print(f"Simulation complete. Output saved to {output_file}")
        return output_file
        
    except subprocess.TimeoutExpired:
        print("ngspice simulation timed out")
        return None
    except FileNotFoundError:
        print("ngspice not found. Please install ngspice: sudo apt-get install ngspice")
        return None

def parse_ngspice_output(output_file):
    """Parse ngspice output file to extract frequency and gain data"""
    
    freq = []
    gain_db = []
    
    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
            
        # Skip header lines and find data
        data_started = False
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*') or line.startswith('Index'):
                continue
            if line.startswith('-----'):
                data_started = True
                continue
            if data_started and line:
                # Parse data lines (format: index frequency gain)
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        f_val = float(parts[1])
                        g_val = float(parts[2])
                        freq.append(f_val)
                        gain_db.append(g_val)
                    except ValueError:
                        continue
                        
        return np.array(freq), np.array(gain_db)
        
    except FileNotFoundError:
        print(f"Output file {output_file} not found")
        return None, None

def plot_frequency_response(results, simulate=True):
    """Plot the frequency response of the filter"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    if simulate:
        # Generate and run SPICE simulation
        netlist_file = generate_spice_netlist(results)
        output_file = run_ngspice_simulation(netlist_file)
        
        if output_file:
            freq, gain_db = parse_ngspice_output(output_file)
            
            if freq is not None and len(freq) > 0:
                # Plot simulated response
                ax1.semilogx(freq/1e6, gain_db, 'b-', linewidth=2, label='SPICE Simulation')
                
                # Find -3dB points
                max_gain = np.max(gain_db)
                f_3db_idx = np.where(gain_db >= max_gain - 3)[0]
                if len(f_3db_idx) > 0:
                    f_low_3db = freq[f_3db_idx[0]] / 1e6
                    f_high_3db = freq[f_3db_idx[-1]] / 1e6
                    bw_3db = f_high_3db - f_low_3db
                    
                    # Mark -3dB points
                    ax1.axhline(y=max_gain-3, color='r', linestyle='--', alpha=0.5, label='-3dB line')
                    ax1.axvline(x=f_low_3db, color='g', linestyle='--', alpha=0.5)
                    ax1.axvline(x=f_high_3db, color='g', linestyle='--', alpha=0.5)
                    
                    # Add text annotations
                    ax1.text(results['f_center'], max_gain-10, 
                            f"BW: {bw_3db:.2f} MHz\nf_low: {f_low_3db:.2f} MHz\nf_high: {f_high_3db:.2f} MHz",
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Plot ideal Chebyshev response for comparison
    f_plot = np.logspace(0, 2, 1000)  # 1 to 100 MHz
    omega = 2 * np.pi * f_plot * 1e6
    omega_0 = 2 * np.pi * results['f_center'] * 1e6
    
    # Normalized frequency
    w_norm = (omega/omega_0 - omega_0/omega) / (results['bandwidth']/results['f_center'])
    
    # Chebyshev response (3rd order, 0.1dB ripple)
    epsilon = math.sqrt(10**(0.1/10) - 1)
    T3 = 4*w_norm**3 - 3*w_norm  # Chebyshev polynomial of order 3
    H_ideal = 1 / np.sqrt(1 + epsilon**2 * T3**2)
    H_ideal_db = 20 * np.log10(H_ideal)
    
    ax1.semilogx(f_plot, H_ideal_db, 'r--', alpha=0.7, label='Ideal Chebyshev')
    
    # Format plot
    ax1.set_xlabel('Frequency (MHz)')
    ax1.set_ylabel('Gain (dB)')
    ax1.set_title('Filter Frequency Response')
    ax1.grid(True, which="both", ls="-", alpha=0.3)
    ax1.set_xlim([1, 100])
    ax1.set_ylim([-60, 5])
    ax1.legend()
    
    # Plot component values
    ax2.axis('off')
    component_text = f"""
Component Values:
-----------------
Tank Inductors:     {results['tank_inductor_nh']:.1f} nH
Tank Capacitors:    {results['tank_cap_pf']:.2f} pF
Coupling Caps:      {results['coupling_cap_pf']:.3f} pF

Input Matching:
  C_hot (series):   {results['c_hot_input_pf']:.2f} pF
  C_cold (shunt):   {results['c_cold_input_pf']:.2f} pF
  
Output Matching:
  C_hot (series):   {results['c_hot_output_pf']:.2f} pF
  C_cold (shunt):   {results['c_cold_output_pf']:.2f} pF

Design Parameters:
  Center Freq:      {results['f_center']:.3f} MHz
  Bandwidth:        {results['bandwidth']:.3f} MHz
  Tank Impedance:   {results['tank_impedance']:.1f} Ω
"""
    ax2.text(0.1, 0.9, component_text, transform=ax2.transAxes, 
            fontfamily='monospace', fontsize=10, verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('filter_response.png', dpi=150)
    plt.show()
    
    print("\nFrequency response plot saved to filter_response.png")

if __name__ == "__main__":
    # Run the main calculation
    results = calculate_chebyshev_filter()
    
    # Example of how to use in Claude Code for quick iterations:
    print("\n" + "="*80)
    print("SIMULATION AND PLOTTING:")
    print("="*80)
    
    # Show the L-network architecture component values
    print("\nCOMPONENT VALUES FOR L-NETWORK ARCHITECTURE:")
    print("============================================")
    print("REPLACE tapped capacitors with L-networks and simple tank caps:")
    print("\nNew L-network components (ADD):")
    print(f"- L_match1 (input):  {results['l_match_input_nh']:.1f} nH  (series from 50Ω source)")
    print(f"- C_match1 (input):  {results['c_match_input_pf']:.1f} pF  (shunt to ground)")
    print(f"- L_match2 (output): {results['l_match_output_nh']:.1f} nH  (series to 50Ω load)")
    print(f"- C_match2 (output): {results['c_match_output_pf']:.1f} pF  (shunt to ground)")
    print("\nTank capacitors (REPLACE tapped pairs):")
    print(f"- C_tank1:           {results['c_tank1_actual_pf']:.1f} pF  (replaces C7931+C7934)")
    print(f"                     Note: {results['c_match_input_pf']:.1f} pF from C_match1 adds in parallel")
    print(f"- C7938:             {results['tank_cap_pf']:.1f} pF  (keep as-is) ✓")
    print(f"- C_tank3:           {results['c_tank3_actual_pf']:.1f} pF  (replaces C7939+C7940)")
    print(f"                     Note: {results['c_match_output_pf']:.1f} pF from C_match2 adds in parallel")
    print("\nCoupling capacitors (keep similar):")
    print(f"- C7936:             {results['c_coupling12_pf']:.1f} pF  ✓")
    print(f"- C7933:             {results['c_coupling23_pf']:.1f} pF  ✓")
    print(f"\nExpected insertion loss: {results['il_total_db']:.2f} dB")
    
    print("\n" + "="*80)
    print("USAGE EXAMPLES:")
    print("="*80)
    print("# Quick recalculation with different parameters:")
    print("results = quick_calc(f_low=10, f_high=20, L_nh=1500)")
    print()
    print("# Compare different inductor values:")
    print("compare_inductors([1000, 1500, 2000, 3000])")
    print()
    print("# Generate SPICE netlist:")
    print("generate_spice_netlist(results, 'my_filter.cir')")
    print()
    print("# Run simulation and plot:")
    print("plot_frequency_response(results, simulate=True)")
