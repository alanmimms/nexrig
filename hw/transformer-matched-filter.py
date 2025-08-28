#!/usr/bin/env python3
"""
Transformer-Matched Chebyshev Bandpass Filter Calculator
========================================================

Calculates component values for a 3rd order Chebyshev bandpass filter
using capacitor-coupled LC resonator topology with external transformer matching.

Architecture: 
  50Ω → [1:N Transformer] → 200Ω Filter → [N:1 Transformer] → 50Ω

Filter topology at 200Ω system impedance:
  Tank1 → Coupling_Cap → Tank2 → Coupling_Cap → Tank3

Each tank: L || C (parallel LC resonator at system impedance)
No impedance matching needed within the filter - transformers handle it externally.

Benefits:
- All tanks operate at the same impedance (200Ω default)
- Perfect symmetry for proper Chebyshev response  
- Simple, clean filter design
- No L-networks or tapped capacitors needed
- Transformer provides galvanic isolation

Author: Claude
"""

import math
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# FILTER PARAMETERS - MODIFY THESE VALUES
# ============================================================================

# Frequency parameters (MHz)
f_lower = 13.5      # Lower cutoff frequency (MHz)  
f_upper = 18.5      # Upper cutoff frequency (MHz)

# Filter characteristics
filter_order = 3    # Filter order (3 for this topology)
ripple_db = 0.1     # Passband ripple (dB)

# System impedance (the impedance level at which the filter operates)
# External transformers will match 50Ω to this impedance
system_impedance = 200.0   # Filter impedance level (Ohms) - PARAMETRIC

# External port impedances (what connects to the transformers)
source_impedance = 50.0    # Source impedance (Ohms)
load_impedance = 50.0      # Load impedance (Ohms)

# Tank inductor value (nH) - can be adjusted for desired component values
tank_inductor_nh = 1000.0  # Tank inductor value (nH)

# ============================================================================
# MAIN CALCULATION FUNCTION
# ============================================================================

def calculate_transformer_matched_filter():
    """
    Calculate component values for transformer-matched Chebyshev filter.
    
    All calculations are done at the system impedance level.
    External transformers handle the impedance matching.
    """
    
    # Basic filter parameters
    f_center = math.sqrt(f_lower * f_upper)
    bandwidth = f_upper - f_lower
    quality_factor = f_center / bandwidth
    fractional_bandwidth = bandwidth / f_center
    omega_0 = 2 * math.pi * f_center * 1e6  # Convert MHz to Hz
    
    # Tank impedance at center frequency (at system impedance level)
    tank_inductance_h = tank_inductor_nh * 1e-9  # Convert nH to H
    tank_impedance = omega_0 * tank_inductance_h
    
    # Ripple factor
    epsilon = math.sqrt(10**(ripple_db/10) - 1)
    
    # Transformer turns ratio
    transformer_ratio = math.sqrt(system_impedance / source_impedance)
    
    # Print header
    print("=" * 80)
    print("TRANSFORMER-MATCHED CHEBYSHEV BANDPASS FILTER")
    print("Capacitor-Coupled LC Resonator Topology")
    print("=" * 80)
    print()
    
    print("INPUT PARAMETERS:")
    print(f"  Lower Frequency:     {f_lower:.3f} MHz")
    print(f"  Upper Frequency:     {f_upper:.3f} MHz")
    print(f"  Filter Order:        {filter_order}")
    print(f"  Passband Ripple:     {ripple_db:.1f} dB")
    print(f"  System Impedance:    {system_impedance:.0f} Ω (filter operates at this Z)")
    print(f"  External Ports:      {source_impedance:.0f} Ω → transformer → filter → transformer → {load_impedance:.0f} Ω")
    print(f"  Tank Inductor:       {tank_inductor_nh:.0f} nH")
    print()
    
    print("CALCULATED PARAMETERS:")
    print(f"  Center Frequency:    {f_center:.3f} MHz")
    print(f"  Bandwidth:           {bandwidth:.3f} MHz")
    print(f"  Quality Factor:      {quality_factor:.2f}")
    print(f"  Fractional BW:       {fractional_bandwidth:.4f}")
    print(f"  Tank Impedance:      {tank_impedance:.1f} Ω (at {system_impedance:.0f}Ω system)")
    print(f"  Ripple Factor (ε):   {epsilon:.4f}")
    print()
    
    print("TRANSFORMER SPECIFICATIONS:")
    print(f"  Impedance ratio:     {system_impedance/source_impedance:.0f}:1")
    print(f"  Turns ratio:         {transformer_ratio:.3f}:1 (√{system_impedance/source_impedance:.0f})")
    print(f"  Input transformer:   1:{transformer_ratio:.3f} step-up")
    print(f"  Output transformer:  {transformer_ratio:.3f}:1 step-down")
    print()
    
    # Calculate Chebyshev prototype values
    n = filter_order
    beta = math.log(1/math.tanh(ripple_db * math.log(10) / 17.37))
    gamma = math.sinh(beta / (2 * n))
    
    g = [0] * (n + 2)  # g0 through g4
    g[0] = 1  # Normalized source resistance
    
    # Calculate g-values
    for k in range(1, n + 1):
        if k == 1:
            g[k] = 2 * math.sin(math.pi / (2 * n)) / gamma
        else:
            sin_val = math.sin((2 * k - 1) * math.pi / (2 * n))
            sum_val = gamma**2 + (math.sin((k - 1) * math.pi / n))**2
            g[k] = 4 * sin_val * math.sin((k - 1) * math.pi / n) / (g[k-1] * sum_val)
    
    # For 3rd order, enforce symmetry
    if n == 3:
        g[3] = g[1]
    
    # Load resistance
    g[n + 1] = 1 if n % 2 == 1 else 1 / (1 + epsilon**2)
    
    print("CHEBYSHEV PROTOTYPE VALUES:")
    for i in range(n + 2):
        print(f"  g{i}:                 {g[i]:.6f}")
    print(f"  Symmetry check:      g1=g3: {abs(g[1] - g[3]) < 1e-10}")
    print()
    
    # External Q calculation
    qe = g[0] * g[1] / fractional_bandwidth
    print(f"  External Q:          {qe:.4f}")
    
    # Coupling coefficients
    k12 = fractional_bandwidth / math.sqrt(g[1] * g[2])
    k23 = fractional_bandwidth / math.sqrt(g[2] * g[3])
    
    print("\nCOUPLING COEFFICIENTS:")
    print(f"  k12:                 {k12:.6f}")
    print(f"  k23:                 {k23:.6f}")
    print(f"  Symmetry check:      k12=k23: {abs(k12 - k23) < 1e-10}")
    print()
    
    # COMPONENT CALCULATIONS AT SYSTEM IMPEDANCE
    print("COMPONENT VALUES (at {:.0f}Ω system impedance):".format(system_impedance))
    print("=" * 60)
    
    # Tank capacitor for resonance at f_center
    tank_cap_pf = 1 / (omega_0**2 * tank_inductance_h) * 1e12
    
    print(f"\nTANK RESONATORS (all identical):")
    print(f"  Inductance:          {tank_inductor_nh:.1f} nH")
    print(f"  Capacitance:         {tank_cap_pf:.2f} pF")
    print(f"  Resonant freq:       {f_center:.3f} MHz")
    print(f"  Tank impedance:      {tank_impedance:.1f} Ω")
    
    # Verify tank impedance makes sense at system impedance
    impedance_ratio = tank_impedance / system_impedance
    print(f"  Z_tank/Z_system:     {impedance_ratio:.3f}")
    
    if impedance_ratio < 0.2 or impedance_ratio > 5:
        print(f"  ⚠ WARNING: Tank impedance poorly matched to system impedance")
        print(f"  ⚠ Consider adjusting tank inductor value")
    
    # Coupling capacitor calculations
    # At system impedance level
    c_coupling12_pf = k12 / (omega_0 * tank_impedance) * 1e12
    c_coupling23_pf = k23 / (omega_0 * tank_impedance) * 1e12
    
    print(f"\nCOUPLING CAPACITORS:")
    print(f"  C12 (tanks 1-2):     {c_coupling12_pf:.3f} pF")
    print(f"  C23 (tanks 2-3):     {c_coupling23_pf:.3f} pF")
    
    # External coupling calculation
    # For transformer-coupled input/output, external Q is determined by transformer
    # The transformer provides the correct termination impedance
    print(f"\nEXTERNAL COUPLING:")
    print(f"  Provided by transformers terminating at {system_impedance:.0f}Ω")
    print(f"  No additional coupling components needed")
    
    # Create results dictionary
    results = {
        'f_center': f_center,
        'bandwidth': bandwidth,
        'system_impedance': system_impedance,
        'transformer_ratio': transformer_ratio,
        'tank_inductor_nh': tank_inductor_nh,
        'tank_cap_pf': tank_cap_pf,
        'tank_impedance': tank_impedance,
        'c_coupling12_pf': c_coupling12_pf,
        'c_coupling23_pf': c_coupling23_pf,
        'qe': qe,
        'k12': k12,
        'k23': k23
    }
    
    # BILL OF MATERIALS
    print("\n" + "=" * 80)
    print("BILL OF MATERIALS")
    print("=" * 80)
    print(f"{'Component':<20} {'Value':<15} {'Description'}")
    print("-" * 80)
    
    # Transformers
    print(f"{'T1 (input)':<20} {'1:' + f'{transformer_ratio:.2f}':<14} {source_impedance:.0f}Ω to {system_impedance:.0f}Ω step-up transformer")
    print(f"{'T2 (output)':<20} {f'{transformer_ratio:.2f}' + ':1':<14} {system_impedance:.0f}Ω to {load_impedance:.0f}Ω step-down transformer")
    print()
    
    # Tank components
    print(f"{'L1, L2, L3':<20} {f'{tank_inductor_nh:.1f} nH':<14} Tank inductors (all identical)")
    print(f"{'C1, C2, C3':<20} {f'{tank_cap_pf:.2f} pF':<14} Tank capacitors (all identical)")
    print()
    
    # Coupling capacitors
    print(f"{'C12':<20} {f'{c_coupling12_pf:.3f} pF':<14} Coupling between tanks 1-2")
    print(f"{'C23':<20} {f'{c_coupling23_pf:.3f} pF':<14} Coupling between tanks 2-3")
    
    # DESIGN NOTES
    print("\n" + "=" * 80)
    print("DESIGN NOTES")
    print("=" * 80)
    print("• All components operate at {:.0f}Ω system impedance".format(system_impedance))
    print("• External transformers handle 50Ω matching")
    print("• Perfect symmetry ensures proper Chebyshev response")
    print("• No impedance matching networks needed within filter")
    print("• Transformers can be wound on ferrite cores (FT37-43 for HF)")
    print("• For 1:{:.2f} ratio: Primary = N turns, Secondary = {:.1f}×N turns".format(
        transformer_ratio, transformer_ratio))
    
    # Suggest different system impedances
    print("\nALTERNATIVE SYSTEM IMPEDANCES:")
    for z_sys in [100, 200, 300, 500]:
        L_alt = tank_impedance / (2 * math.pi * f_center * 1e6) * 1e9
        C_alt = 1 / (omega_0**2 * (L_alt * 1e-9)) * 1e12
        ratio = math.sqrt(z_sys / source_impedance)
        print(f"  {z_sys:3.0f}Ω: L={L_alt:.0f}nH, C={C_alt:.1f}pF, Transformer 1:{ratio:.2f}")
    
    print("\n" + "=" * 80)
    
    return results

def calculate_with_impedance(z_system, L_nh=None):
    """
    Recalculate filter with different system impedance.
    If L_nh not specified, adjusts L to maintain reasonable tank Z.
    """
    global system_impedance, tank_inductor_nh
    
    old_z = system_impedance
    old_L = tank_inductor_nh
    
    system_impedance = z_system
    
    if L_nh is None:
        # Scale inductor to maintain similar tank/system impedance ratio
        tank_inductor_nh = old_L * (z_system / old_z)
    else:
        tank_inductor_nh = L_nh
    
    results = calculate_transformer_matched_filter()
    
    # Restore
    system_impedance = old_z
    tank_inductor_nh = old_L
    
    return results

def compare_impedances():
    """Compare different system impedance options with Q-factor analysis"""
    print("\n" + "=" * 80)
    print("SYSTEM IMPEDANCE COMPARISON WITH Q-FACTOR ANALYSIS")
    print("=" * 80)
    
    impedances = [50, 100, 200, 300, 500]
    
    print(f"{'Z_sys':<8} {'Trans':<8} {'L (nH)':<10} {'C (pF)':<10} {'C_coup':<10} {'Practical?'}")
    print("-" * 70)
    
    for z in impedances:
        # Maintain constant tank Q by scaling L with impedance
        L_scaled = tank_inductor_nh * (z / 200.0)
        
        # Quick calculation
        f_c = math.sqrt(f_lower * f_upper)
        omega = 2 * math.pi * f_c * 1e6
        C = 1 / (omega**2 * L_scaled * 1e-9) * 1e12
        
        # Coupling cap (approximate)
        k = 0.198  # Typical for 0.1dB ripple, BW=5MHz
        Z_tank = omega * L_scaled * 1e-9
        C_coup = k / (omega * Z_tank) * 1e12
        
        trans = math.sqrt(z / 50.0)
        
        practical = "✓" if (10 < C < 500 and 5 < C_coup < 100 and L_scaled < 5000) else "✗"
        
        print(f"{z:<8.0f} 1:{trans:<6.2f} {L_scaled:<10.1f} {C:<10.2f} {C_coup:<10.2f} {practical}")
    
    print("\nNOTE: 'Practical' assumes standard component values are available")

def optimize_for_stability(z_system, max_bw_variation_pct=3.0):
    """
    Find optimal L/C values for given system impedance to minimize sensitivity.
    
    Goal: Make coupling capacitors large enough that variations are tolerable.
    Constraint: Keep tank impedance reasonable for Q requirements.
    """
    print("\n" + "=" * 80)
    print(f"OPTIMIZING L/C FOR {z_system}Ω SYSTEM (Max BW variation: {max_bw_variation_pct}%)")
    print("=" * 80)
    
    f_c = math.sqrt(f_lower * f_upper)
    omega = 2 * math.pi * f_c * 1e6
    k = 0.198  # Coupling coefficient
    
    # Assume ±25% total capacitor variation (environmental + manufacturing)
    cap_variation_pct = 25.0
    
    # Required minimum coupling cap to meet bandwidth stability requirement
    # BW variation ≈ 1.5 × coupling variation
    # So for 3% BW variation with 25% cap variation:
    # We need the coupling variation effect to be reduced
    
    # Since relative effect decreases with larger caps (better SNR to variations)
    # We need minimum coupling capacitance
    min_coupling_pF = 30.0  # Start with empirical minimum for stability
    
    print(f"\nAssuming ±{cap_variation_pct}% total capacitor variation")
    print(f"Target: <{max_bw_variation_pct}% bandwidth variation")
    print(f"Minimum coupling cap for stability: {min_coupling_pF} pF")
    
    print("\n" + "-" * 80)
    print(f"{'L (nH)':<10} {'C (pF)':<10} {'Z_tank':<10} {'C_coup':<10} {'BW_var':<10} {'Tank/Sys':<12} {'Assessment'}")
    print("-" * 80)
    
    # Try different L values
    L_values = [250, 500, 750, 1000, 1500, 2000, 2500, 3000]
    
    best_option = None
    
    for L_nH in L_values:
        L_H = L_nH * 1e-9
        
        # Tank capacitance for resonance
        C_tank_pF = 1 / (omega**2 * L_H) * 1e12
        
        # Tank impedance at resonance
        Z_tank = omega * L_H
        
        # Coupling capacitor
        C_coup_pF = k / (omega * Z_tank) * 1e12
        
        # Bandwidth variation estimate
        # Larger coupling caps = less relative variation
        relative_effect = min_coupling_pF / C_coup_pF if C_coup_pF > 0 else 1
        bw_variation = cap_variation_pct * 1.5 * relative_effect
        
        # Tank-to-system impedance ratio
        tank_sys_ratio = Z_tank / z_system
        
        # Assessment
        if C_coup_pF < 20:
            assessment = "Too small"
        elif C_coup_pF > 100:
            assessment = "Very stable"
        elif bw_variation < max_bw_variation_pct:
            assessment = "GOOD"
        elif bw_variation < max_bw_variation_pct * 2:
            assessment = "Marginal"
        else:
            assessment = "Poor"
        
        # Check if this is practical
        if 0.2 < tank_sys_ratio < 2.0 and C_tank_pF < 500 and assessment == "GOOD":
            if best_option is None or C_coup_pF > best_option['C_coup_pF']:
                best_option = {
                    'L_nH': L_nH,
                    'C_tank_pF': C_tank_pF,
                    'C_coup_pF': C_coup_pF,
                    'Z_tank': Z_tank,
                    'bw_variation': bw_variation
                }
        
        print(f"{L_nH:<10.0f} {C_tank_pF:<10.1f} {Z_tank:<10.1f} {C_coup_pF:<10.1f} "
              f"{bw_variation:<10.1f} {tank_sys_ratio:<12.2f} {assessment}")
    
    if best_option:
        print(f"\n" + "=" * 60)
        print(f"RECOMMENDED DESIGN for {z_system}Ω system:")
        print(f"  Tank inductor:    {best_option['L_nH']:.0f} nH")
        print(f"  Tank capacitor:   {best_option['C_tank_pF']:.1f} pF")
        print(f"  Coupling caps:    {best_option['C_coup_pF']:.1f} pF")
        print(f"  Tank impedance:   {best_option['Z_tank']:.1f} Ω")
        print(f"  Expected BW var:  ±{best_option['bw_variation']:.1f}%")
        print(f"\nThis design achieves <{max_bw_variation_pct}% bandwidth variation")
        print(f"with ±{cap_variation_pct}% capacitor tolerance!")
    else:
        print(f"\n⚠ WARNING: Cannot achieve {max_bw_variation_pct}% stability at {z_system}Ω")
        print(f"Consider lower system impedance or tighter component tolerances")
    
    return best_option

def analyze_q_sensitivity(inductor_q=50, capacitor_q=500):
    """
    Analyze how system impedance affects Q-factor criticality and insertion loss.
    
    Higher impedance systems are MORE sensitive to component Q because:
    1. Inductors become larger (more wire resistance)
    2. Capacitors become smaller (higher loss tangent impact)
    3. Current is lower but voltage is higher
    """
    print("\n" + "=" * 80)
    print("Q-FACTOR SENSITIVITY AND INSERTION LOSS ANALYSIS")
    print("=" * 80)
    print(f"Assumed component Q: Inductor Q={inductor_q}, Capacitor Q={capacitor_q}")
    print()
    
    impedances = [50, 100, 200, 300, 500]
    f_c = math.sqrt(f_lower * f_upper)
    omega = 2 * math.pi * f_c * 1e6
    bw = (f_upper - f_lower) * 1e6  # Hz
    filter_q = f_c / (f_upper - f_lower)
    
    print(f"{'Z_sys':<8} {'L(nH)':<8} {'C(pF)':<8} {'L_loss':<10} {'C_loss':<10} {'Total_IL':<10} {'Q_crit':<10}")
    print(f"{'(Ω)':<8} {'':<8} {'':<8} {'(dB)':<10} {'(dB)':<10} {'(dB)':<10} {'Factor':<10}")
    print("-" * 80)
    
    reference_il = None
    
    for z_sys in impedances:
        # Scale components to maintain constant loaded Q
        L = tank_inductor_nh * (z_sys / 200.0) * 1e-9  # Henry
        C = 1 / (omega**2 * L) * 1e12  # pF
        C_farads = C * 1e-12
        
        # Tank impedance
        X_L = omega * L
        X_C = 1 / (omega * C_farads)
        
        # Loss resistances
        R_L = X_L / inductor_q  # Series resistance of inductor
        R_C = X_C / capacitor_q  # Equivalent series resistance of capacitor
        
        # Unloaded Q of the tank
        # Q_u = (parallel combination of Q_L and Q_C)
        Q_L = inductor_q
        Q_C = capacitor_q
        Q_unloaded = 1 / (1/Q_L + 1/Q_C)
        
        # Loaded Q (including external loading from system impedance)
        # For critically coupled filter, QL ≈ filter_q
        Q_loaded = filter_q
        
        # Insertion loss contribution from finite unloaded Q
        # IL ≈ 4.343 * (QL/QU) for each resonator
        il_per_tank_db = 4.343 * (Q_loaded / Q_unloaded)
        
        # Total IL for 3 tanks
        total_il_db = 3 * il_per_tank_db
        
        # Separate contributions
        il_inductor_db = 4.343 * (Q_loaded / Q_L) * 3
        il_capacitor_db = 4.343 * (Q_loaded / Q_C) * 3
        
        # Q criticality factor (how much Q affects performance)
        # Higher Z systems need higher component Q to maintain low loss
        q_criticality = z_sys / 200.0  # Normalized to 200Ω reference
        
        if reference_il is None:
            reference_il = total_il_db
        
        print(f"{z_sys:<8.0f} {L*1e9:<8.0f} {C:<8.1f} {il_inductor_db:<10.3f} "
              f"{il_capacitor_db:<10.3f} {total_il_db:<10.3f} {q_criticality:<10.2f}x")
    
    print("\nKEY INSIGHTS:")
    print("• Lower impedance: Inductor Q more critical (smaller L, higher current)")
    print("• Higher impedance: Capacitor Q more critical (smaller C, higher voltage)")
    print("• Insertion loss increases with system impedance for same component Q")
    print("• Q criticality factor shows relative sensitivity to component losses")

def analyze_coupling_effects():
    """
    Analyze how system impedance affects coupling capacitor requirements.
    """
    print("\n" + "=" * 80)
    print("COUPLING CAPACITOR EFFECTS VS SYSTEM IMPEDANCE")
    print("=" * 80)
    
    impedances = [50, 100, 200, 300, 500]
    f_c = math.sqrt(f_lower * f_upper)
    omega = 2 * math.pi * f_c * 1e6
    k = 0.198  # Coupling coefficient
    
    print(f"{'Z_sys':<8} {'C_coup':<10} {'X_coup':<10} {'Voltage':<12} {'Current':<12} {'C_tolerance':<12}")
    print(f"{'(Ω)':<8} {'(pF)':<10} {'(Ω)':<10} {'Stress':<12} {'(relative)':<12} {'Criticality':<12}")
    print("-" * 90)
    
    for z_sys in impedances:
        # Tank components
        L = tank_inductor_nh * (z_sys / 200.0) * 1e-9
        Z_tank = omega * L
        
        # Coupling capacitor
        C_coup = k / (omega * Z_tank) * 1e12  # pF
        X_coup = 1 / (omega * C_coup * 1e-12)  # Reactance
        
        # Relative voltage and current (normalized to 200Ω case)
        voltage_factor = math.sqrt(z_sys / 200.0)  # V ∝ √Z for constant power
        current_factor = math.sqrt(200.0 / z_sys)  # I ∝ 1/√Z
        
        # Tolerance criticality (smaller caps are harder to tolerance)
        # 1% of 10pF is much more critical than 1% of 100pF
        tolerance_criticality = 20.0 / C_coup  # Normalized to ~20pF
        
        print(f"{z_sys:<8.0f} {C_coup:<10.2f} {X_coup:<10.0f} {voltage_factor:<12.2f}x "
              f"{current_factor:<12.2f}x {tolerance_criticality:<12.2f}x")
    
    print("\nCOUPLING CAPACITOR INSIGHTS:")
    print("• Lower impedance: Larger coupling caps needed (easier to implement)")
    print("• Higher impedance: Smaller coupling caps (tighter tolerance needed)")
    print("• Voltage stress increases with impedance (may need higher voltage rating)")
    print("• Current decreases with impedance (can use smaller physical parts)")
    print("• Small coupling caps (<10pF) become dominated by parasitics")

def analyze_overall_performance():
    """
    Analyze overall filter performance metrics vs system impedance.
    """
    print("\n" + "=" * 80)
    print("OVERALL FILTER PERFORMANCE VS SYSTEM IMPEDANCE")
    print("=" * 80)
    
    print("\nFACTOR SUMMARY:")
    print("-" * 60)
    
    factors = [
        ("Filter Steepness", "UNCHANGED", "Determined by order and ripple, not Z"),
        ("Shape Factor", "UNCHANGED", "Set by Chebyshev polynomials"),
        ("Insertion Loss", "INCREASES with Z", "Higher Z → higher component loss"),
        ("Inductor Q Critical", "DECREASES with Z", "Larger L → lower current density"),
        ("Capacitor Q Critical", "INCREASES with Z", "Smaller C → higher loss tangent impact"),
        ("Voltage Handling", "INCREASES with Z", "Higher voltage for same power"),
        ("Current Handling", "DECREASES with Z", "Lower current for same power"),
        ("PCB Parasitics", "MORE CRITICAL at high Z", "Small C dominated by strays"),
        ("Component Tolerance", "MORE CRITICAL at high Z", "Small values → tight tolerance"),
        ("Dynamic Range", "BETTER at high Z", "Higher voltage → better SNR"),
        ("Transformer Loss", "INCREASES with Z", "Higher turns ratio → more loss"),
    ]
    
    for factor, trend, reason in factors:
        print(f"{factor:<20} {trend:<20} {reason}")
    
    print("\nRECOMMENDED SYSTEM IMPEDANCES:")
    print("-" * 60)
    print("50-100Ω:  Best for high power, accepts lower Q components")
    print("200-300Ω: Good compromise, moderate component values")
    print("400-500Ω: Best for low noise, requires high Q components")
    print("\nFOR YOUR APPLICATION (13.5-18.5 MHz SSB):")
    print("• 200Ω is a good choice - reasonable component values")
    print("• 100Ω if using lower Q inductors")
    print("• 300Ω if you have high Q components available")

def generate_spice_netlist(results, filename="transformer_filter.cir"):
    """Generate SPICE netlist for the transformer-matched filter"""
    
    netlist = f""".title Transformer-Matched Chebyshev Bandpass Filter
* System impedance: {results['system_impedance']:.0f} ohms
* Center frequency: {results['f_center']:.3f} MHz
* Bandwidth: {results['bandwidth']:.3f} MHz

* Input source (50 ohm)
Vin in 0 AC 1
Rin in 1 50

* Input transformer (1:{results['transformer_ratio']:.3f})
* Ideal transformer model using controlled sources
E1 2 0 1 0 {results['transformer_ratio']:.3f}
* Add small series R to avoid numerical issues
R1 2 3 0.1

* Tank 1
L1 3 0 {results['tank_inductor_nh']:.1f}n
C1 3 0 {results['tank_cap_pf']:.2f}p

* Coupling 1-2
C12 3 4 {results['c_coupling12_pf']:.3f}p

* Tank 2
L2 4 0 {results['tank_inductor_nh']:.1f}n
C2 4 0 {results['tank_cap_pf']:.2f}p

* Coupling 2-3
C23 4 5 {results['c_coupling23_pf']:.3f}p

* Tank 3
L3 5 0 {results['tank_inductor_nh']:.1f}n
C3 5 0 {results['tank_cap_pf']:.2f}p

* Output transformer ({results['transformer_ratio']:.3f}:1)
E2 out 0 5 0 {1/results['transformer_ratio']:.3f}

* Output load (50 ohm)
Rload out 0 50

.control
ac dec 500 1MEG 100MEG
plot vdb(out)
.endc

.end
"""
    
    with open(filename, 'w') as f:
        f.write(netlist)
    
    print(f"\nSPICE netlist written to {filename}")
    return filename

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run main calculation
    results = calculate_transformer_matched_filter()
    
    # Show comparison table
    compare_impedances()
    
    # Detailed analysis
    analyze_q_sensitivity(inductor_q=50, capacitor_q=500)
    analyze_coupling_effects()
    analyze_overall_performance()
    
    # Optimize for stability at different system impedances
    print("\n" + "=" * 80)
    print("OPTIMIZATION FOR STABLE BANDWIDTH (<3% variation)")
    print("=" * 80)
    
    for z_sys in [200, 300, 500]:
        optimize_for_stability(z_sys, max_bw_variation_pct=3.0)
    
    # Usage examples
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES:")
    print("=" * 80)
    print("# Calculate with different system impedance:")
    print("results = calculate_with_impedance(z_system=300)")
    print()
    print("# Analyze Q sensitivity with your component specs:")
    print("analyze_q_sensitivity(inductor_q=30, capacitor_q=200)")
    print()
    print("# Generate SPICE netlist:")
    print("generate_spice_netlist(results, 'my_filter.cir')")
    print()
    print("# Compare different impedance options:")
    print("compare_impedances()")