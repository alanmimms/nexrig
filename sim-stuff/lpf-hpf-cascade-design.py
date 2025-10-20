#!/usr/bin/env python3
"""
LPF + HPF Cascade Design with Integrated Impedance Transformation
=================================================================

Design 3rd-order LPF followed by 3rd-order HPF with:
- Input transformer integrated into first LPF inductor
- Output transformer integrated into last HPF inductor
- 6 inductors + 6 capacitors per band total

Author: Claude
"""

import math
import numpy as np
import matplotlib.pyplot as plt

def calculate_lpf_hpf_cascade(f_low_mhz, f_high_mhz, ripple_db=0.1):
    """
    Design LPF+HPF cascade with integrated transformers.
    
    Args:
        f_low_mhz: High-pass cutoff frequency
        f_high_mhz: Low-pass cutoff frequency  
        ripple_db: Passband ripple
    
    Returns:
        dict: Component values for LPF and HPF sections
    """
    
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    omega_low = 2 * math.pi * f_low
    omega_high = 2 * math.pi * f_high
    
    print(f"  LPF cutoff: {f_high_mhz} MHz")  
    print(f"  HPF cutoff: {f_low_mhz} MHz")
    
    # 3rd-order Chebyshev g-values (0.1dB ripple)
    g0 = 1.0
    g1 = 0.9441  # Standard values from tables
    g2 = 1.4065
    g3 = 0.9441  
    g4 = 1.0
    
    # System impedances
    Z_source = 50      # Input impedance
    Z_filter = 200     # Filter design impedance  
    Z_load = 50        # Output impedance
    
    # === LOW-PASS FILTER SECTION (f_high cutoff) ===
    print(f"  LPF design at {Z_filter}Ω:")
    
    # Standard LPF component calculation
    L1_lpf_base = g1 * Z_filter / omega_high
    C1_lpf = g2 / (omega_high * Z_filter) 
    L2_lpf = g3 * Z_filter / omega_high
    
    # Transform first inductor for 50Ω → 200Ω (1:2 impedance ratio)
    # Impedance ratio = 4:1, so turns ratio = 2:1
    # L_secondary = 4 × L_primary for same magnetic energy
    L1_lpf_transformed = L1_lpf_base  # This will be the secondary
    L1_lpf_primary = L1_lpf_transformed / 4  # Primary for 50Ω side
    
    print(f"    L1_primary: {L1_lpf_primary*1e9:.1f} nH (50Ω side)")
    print(f"    L1_secondary: {L1_lpf_transformed*1e9:.1f} nH (200Ω side)")
    print(f"    C1: {C1_lpf*1e12:.1f} pF")
    print(f"    L2: {L2_lpf*1e9:.1f} nH")
    
    # === HIGH-PASS FILTER SECTION (f_low cutoff) ===
    print(f"  HPF design at {Z_filter}Ω:")
    
    # For HPF, L and C roles are swapped compared to LPF
    C1_hpf = 1 / (g1 * omega_low * Z_filter)
    L1_hpf = g2 * Z_filter / omega_low  
    C2_hpf = 1 / (g3 * omega_low * Z_filter)
    
    # Transform last inductor for 200Ω → 50Ω  
    L1_hpf_secondary = L1_hpf  # This connects to 200Ω filter
    L1_hpf_primary = L1_hpf / 4  # This connects to 50Ω load
    
    print(f"    C1: {C1_hpf*1e12:.1f} pF")
    print(f"    L1_secondary: {L1_hpf_secondary*1e9:.1f} nH (200Ω side)")
    print(f"    L1_primary: {L1_hpf_primary*1e9:.1f} nH (50Ω side)")
    print(f"    C2: {C2_hpf*1e12:.1f} pF")
    
    # === TOROIDAL CORE CALCULATIONS ===
    # Choose cores based on frequency range
    f_center = math.sqrt(f_low * f_high) / 1e6
    
    if f_center < 5:
        core_type = 'T37-2'
        AL = 5.5
    elif f_center < 15:
        core_type = 'T37-6' 
        AL = 4.0
    elif f_center < 30:
        core_type = 'T37-10'
        AL = 2.5
    else:
        core_type = 'T37-12'
        AL = 2.0
    
    print(f"  Recommended core: {core_type} (AL = {AL} nH/turn²)")
    
    # Calculate turns for each inductor
    inductors = {
        'L1_lpf_pri': L1_lpf_primary * 1e9,
        'L1_lpf_sec': L1_lpf_transformed * 1e9,
        'L2_lpf': L2_lpf * 1e9,
        'L1_hpf_sec': L1_hpf_secondary * 1e9,
        'L1_hpf_pri': L1_hpf_primary * 1e9,
    }
    
    turns = {}
    for name, L_nH in inductors.items():
        turns[name] = max(2, round(math.sqrt(L_nH / AL)))
    
    # Package results
    results = {
        'f_low_mhz': f_low_mhz,
        'f_high_mhz': f_high_mhz,
        'f_center_mhz': f_center,
        
        # LPF section
        'L1_lpf_pri_nH': L1_lpf_primary * 1e9,
        'L1_lpf_sec_nH': L1_lpf_transformed * 1e9,
        'C1_lpf_pF': C1_lpf * 1e12,
        'L2_lpf_nH': L2_lpf * 1e9,
        
        # HPF section  
        'C1_hpf_pF': C1_hpf * 1e12,
        'L1_hpf_sec_nH': L1_hpf_secondary * 1e9,
        'L1_hpf_pri_nH': L1_hpf_primary * 1e9,
        'C2_hpf_pF': C2_hpf * 1e12,
        
        # Core info
        'core_type': core_type,
        'AL': AL,
        'turns': turns,
    }
    
    return results

def create_circuit_diagram():
    """Create ASCII circuit diagram showing the topology."""
    
    print("\nCIRCUIT TOPOLOGY:")
    print("=" * 80)
    print("50Ω INPUT → 3rd-Order LPF @ 200Ω → 3rd-Order HPF @ 200Ω → 50Ω OUTPUT")
    print()
    print("Detailed schematic:")
    print()
    print("       ┌─── LOW-PASS FILTER ────┐  ┌─── HIGH-PASS FILTER ───┐")
    print("       │                        │  │                        │")
    print("50Ω ───T1═══L1───┬───L2───┬─────┼──┼──┬───T2═══┬─────────── 50Ω")
    print("      pri sec    │        │     │  │  │    sec pri           ")
    print("       1:2      C1       C_lpf  │  │ C1_hpf  │              ")
    print("                │        │      │  │  │      │              ")
    print("                └────────┴──────┘  └──┴──────┘              ")
    print("                                                             ")
    print("T1: Input transformer (50Ω → 200Ω, integrated with L1_lpf)")
    print("T2: Output transformer (200Ω → 50Ω, integrated with L1_hpf)")
    print("L1_lpf, L2_lpf: LPF inductors at 200Ω")
    print("C1_lpf: LPF capacitor")  
    print("C1_hpf, C2_hpf: HPF capacitors")
    print("L1_hpf: HPF inductor (part of T2)")
    print()
    
    print("COMPONENT COUNT PER BAND:")
    print("  • Inductors: 6 (2×T1 + L2_lpf + L1_hpf + 2×T2)")
    print("  • Capacitors: 3 (C1_lpf + C1_hpf + C2_hpf)")
    print("  • Transformers: 2 (input + output)")
    print()
    
    print("ADVANTAGES:")
    print("  ✓ True bandpass response (LPF × HPF)")
    print("  ✓ 6th-order selectivity (3+3)")
    print("  ✓ Sharp skirts on both sides") 
    print("  ✓ Integrated impedance matching")
    print("  ✓ No impossibly tight coupling required")
    print("  ✓ Standard filter design techniques")

def design_all_bands():
    """Design LPF+HPF cascade for wide-band coverage (4 bands total)."""
    
    # Wide bands with 100kHz overlap for tuning flexibility
    bands = [
        {'name': 'Band 1 (HF-Low)', 'low': 1.8, 'high': 4.6},
        {'name': 'Band 2 (HF-Mid)', 'low': 4.4, 'high': 10.1},
        {'name': 'Band 3 (HF-High)', 'low': 9.9, 'high': 18.1},
        {'name': 'Band 4 (HF-VHF)', 'low': 17.9, 'high': 30.0},
    ]
    
    print("LPF+HPF CASCADE DESIGN - 4 WIDE BANDS FOR TAYLOE DETECTOR")
    print("=" * 80)
    
    all_results = []
    
    for i, band in enumerate(bands, 1):
        print(f"\n{band['name']}: {band['low']}-{band['high']} MHz")
        print("-" * 50)
        
        result = calculate_lpf_hpf_cascade(band['low'], band['high'])
        result['band_name'] = band['name']
        result['band_num'] = i
        all_results.append(result)
    
    # Summary table
    print(f"\n{'='*80}")
    print("COMPONENT SUMMARY TABLE")
    print(f"{'='*80}")
    
    print(f"{'Band':<15} | {'Range (MHz)':<12} | {'Core':<8} | {'LPF L1/L2 (nH)':<15} | {'HPF L1 (nH)':<12} | {'Caps (pF)':<15}")
    print("-" * 95)
    
    for result in all_results:
        band_str = f"Band {result['band_num']}"
        range_str = f"{result['f_low_mhz']:.1f}-{result['f_high_mhz']:.1f}"
        lpf_l_str = f"{result['L1_lpf_sec_nH']:.0f}/{result['L2_lpf_nH']:.0f}"
        hpf_l_str = f"{result['L1_hpf_sec_nH']:.0f}"
        caps_str = f"{result['C1_lpf_pF']:.0f},{result['C1_hpf_pF']:.0f},{result['C2_hpf_pF']:.0f}"
        
        print(f"{band_str:<15} | {range_str:<12} | {result['core_type']:<8} | {lpf_l_str:<15} | {hpf_l_str:<12} | {caps_str:<15}")
    
    return all_results

if __name__ == '__main__':
    create_circuit_diagram()
    design_all_bands()
    
    print(f"\n{'='*80}")
    print("PRACTICAL IMPLEMENTATION NOTES:")
    print(f"{'='*80}")
    print("• Each band requires 6 toroidal inductors + 3 capacitors")
    print("• Input/output transformers use bifilar winding (k > 0.95)")
    print("• All inductors can be wound on same core type per band")
    print("• Capacitors can be standard NPO ceramic or air variable")
    print("• Much better stopband rejection than 3-pole designs")
    print("• Each section can be aligned independently")
    print("• True Chebyshev response achievable")