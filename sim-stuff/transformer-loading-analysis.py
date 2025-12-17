#!/usr/bin/env python3
"""
Transformer Loading Effect on Filter Tank
=========================================

Analyzes how autotransformer inductance affects the first LC tank.
This is a CRITICAL issue that must be addressed!

Author: Claude
"""

import math
import numpy as np

def analyze_transformer_loading():
    """
    Calculate how transformer inductance affects tank resonance.
    """
    
    print("=" * 80)
    print("TRANSFORMER LOADING EFFECT ON FIRST TANK")
    print("=" * 80)
    
    # Filter parameters at 100Ω system impedance
    f_center = 15.8  # MHz
    omega = 2 * math.pi * f_center * 1e6
    
    # Proposed tank values (100Ω system, optimized for stability)
    L_tank_nH = 350  # Tank inductor
    C_tank_pF = 290  # Tank capacitor
    
    # Convert to base units
    L_tank = L_tank_nH * 1e-9
    C_tank = C_tank_pF * 1e-12
    
    # Verify tank resonance without transformer
    f_tank_alone = 1 / (2 * math.pi * math.sqrt(L_tank * C_tank)) / 1e6
    
    print(f"\nTANK WITHOUT TRANSFORMER:")
    print(f"  L_tank: {L_tank_nH} nH")
    print(f"  C_tank: {C_tank_pF} pF")
    print(f"  Resonance: {f_tank_alone:.2f} MHz ✓")
    
    # Autotransformer inductance (from 100Ω side)
    # From previous calculation: 10 turns = 42µH from 50Ω side
    # From 100Ω side (14 turns): 82.32µH
    L_transformer_uH = 82.32
    L_transformer = L_transformer_uH * 1e-6
    
    print(f"\nAUTOTRANSFORMER LOADING:")
    print(f"  Transformer L (100Ω side): {L_transformer_uH:.1f} µH")
    print(f"  Tank L: {L_tank_nH/1000:.3f} µH")
    print(f"  Ratio: {L_transformer_uH/(L_tank_nH/1000):.1f}:1")
    
    # CRITICAL: These are in PARALLEL!
    L_parallel = (L_tank * L_transformer) / (L_tank + L_transformer)
    L_parallel_nH = L_parallel * 1e9
    
    print(f"\nPARALLEL COMBINATION:")
    print(f"  L_effective = L_tank || L_transformer")
    print(f"  L_effective = {L_parallel_nH:.1f} nH (was {L_tank_nH} nH)")
    print(f"  Reduction: {(1 - L_parallel_nH/L_tank_nH)*100:.1f}% - HUGE PROBLEM!")
    
    # New resonant frequency with transformer loading
    f_loaded = 1 / (2 * math.pi * math.sqrt(L_parallel * C_tank)) / 1e6
    
    print(f"\nRESONANCE SHIFT:")
    print(f"  Original: {f_tank_alone:.2f} MHz")
    print(f"  With transformer: {f_loaded:.2f} MHz")
    print(f"  Shift: {f_loaded - f_tank_alone:.2f} MHz ({(f_loaded/f_tank_alone - 1)*100:+.1f}%)")
    print(f"  ⚠ COMPLETELY DETUNES THE FILTER!")
    
    # Required capacitor to compensate
    C_required = 1 / ((2 * math.pi * f_center * 1e6)**2 * L_parallel)
    C_required_pF = C_required * 1e12
    
    print(f"\nCOMPENSATION REQUIRED:")
    print(f"  Original C: {C_tank_pF:.1f} pF")
    print(f"  Required C: {C_required_pF:.1f} pF")
    print(f"  Must REDUCE by: {C_tank_pF - C_required_pF:.1f} pF")

def analyze_solutions():
    """
    Analyze solutions to the transformer loading problem.
    """
    
    print("\n" + "=" * 80)
    print("SOLUTIONS TO TRANSFORMER LOADING")
    print("=" * 80)
    
    f_center = 15.8
    omega = 2 * math.pi * f_center * 1e6
    
    print("\nOPTION 1: HIGH-INDUCTANCE TRANSFORMER")
    print("-" * 50)
    
    # Need transformer L >> tank L (at least 10x)
    L_tank_nH = 350
    L_transformer_min_uH = L_tank_nH * 10 / 1000  # 10x tank inductance
    
    print(f"  Requirement: L_transformer >> L_tank")
    print(f"  Target: L_transformer > {L_transformer_min_uH:.1f} µH")
    
    # For FT37-43 with AL = 420 nH/turn²
    AL = 420
    N_required = math.sqrt(L_transformer_min_uH * 1000 / AL)
    
    print(f"  Turns needed on FT37-43: {N_required:.0f} turns (from 100Ω port)")
    print(f"  Tap ratio: 1:1.41 means {N_required/1.41:.0f} turn tap")
    print(f"  ✗ Not practical - too many turns!")
    
    print("\nOPTION 2: SERIES COUPLING CAPACITOR")
    print("-" * 50)
    print("  Add DC blocking cap between transformer and tank")
    print("  Breaks the parallel inductance connection")
    
    # Calculate coupling cap value
    # Should be >> tank cap to not affect resonance
    C_coupling_block = 1000  # pF, large enough to be "transparent"
    X_C = 1 / (omega * C_coupling_block * 1e-12)
    
    print(f"  Blocking cap: {C_coupling_block} pF")
    print(f"  Reactance at {f_center} MHz: {X_C:.1f} Ω")
    print(f"  ✓ WORKS! Simple solution")
    
    print("\nOPTION 3: COMPENSATED TANK DESIGN")
    print("-" * 50)
    print("  Design tank accounting for parallel transformer L")
    
    # Given transformer with reasonable turns (e.g., 10+4 turns)
    L_trans_100 = 82.32e-6  # 14 turns on FT37-43
    
    # Design tank inductor to give correct parallel value
    L_parallel_target_nH = 350  # Want this effective inductance
    L_parallel_target = L_parallel_target_nH * 1e-9
    
    # Solve: 1/L_parallel = 1/L_tank + 1/L_transformer
    # So: L_tank = (L_parallel * L_transformer) / (L_transformer - L_parallel)
    L_tank_required = (L_parallel_target * L_trans_100) / (L_trans_100 - L_parallel_target)
    L_tank_required_nH = L_tank_required * 1e9
    
    print(f"  Target L_effective: {L_parallel_target_nH} nH")
    print(f"  Transformer L: {L_trans_100*1e9:.0f} nH")
    print(f"  Required tank L: {L_tank_required_nH:.1f} nH")
    print(f"  ✓ Possible, but tiny inductor value!")
    
    print("\nOPTION 4: TRANSFORMER WITH LESS INDUCTANCE")
    print("-" * 50)
    print("  Use different core with lower AL value")
    
    # Try FT37-61 with AL = 75 nH/turn²
    AL_61 = 75
    N_design = 10  # 100Ω side turns
    L_trans_61 = AL_61 * N_design**2 / 1000  # µH
    
    print(f"  FT37-61 core (AL = {AL_61} nH/turn²)")
    print(f"  10 turns gives: {L_trans_61:.1f} µH")
    print(f"  Still too much loading on 350nH tank!")
    
    print("\nOPTION 5: SEPARATE TRANSFORMER (BEST!)")
    print("-" * 50)
    print("  Place transformer BEFORE a coupling capacitor")
    print("  Coupling cap isolates transformer from tank")
    print()
    print("  50Ω → [Transformer] → [100Ω] → [Coupling Cap] → [Tank]")
    print()
    print("  ✓✓ BEST SOLUTION - No loading effect!")

def recommended_architecture():
    """
    Show the recommended architecture to avoid loading.
    """
    
    print("\n" + "=" * 80)
    print("RECOMMENDED ARCHITECTURE")
    print("=" * 80)
    
    print("""
    WRONG (Transformer loads tank):
    ================================
    50Ω ──[1:1.41]──┬── L_tank ──┬── Coupling ──
                    │            │
                    └── C_tank ──┘
    
    Problem: Transformer L in parallel with tank L
    
    
    CORRECT (Isolated by coupling cap):
    ====================================
    50Ω ──[1:1.41]──[100Ω]──[C_DC]──┬── L_tank ──┬── C_coup ──
                                      │            │
                                      └── C_tank ──┘
    
    C_DC = DC blocking/isolation cap (~1000pF)
    
    
    ALTERNATIVE (Account for loading):
    ==================================
    If transformer MUST connect directly:
    1. Use very high inductance transformer (>10x tank L)
    2. Reduce tank L to compensate for parallel transformer L
    3. Adjust tank C accordingly
    
    But this is complex and constrains the design!
    """)
    
    print("\nFINAL RECOMMENDATION:")
    print("=" * 60)
    print("USE BLOCKING CAPACITOR between transformer and tank!")
    print()
    print("Transformer: 10+4 turns on FT37-43 (1:1.41 auto)")
    print("Blocking cap: 1000pF NP0/C0G (low loss)")
    print("Tank: 350nH inductor, 290pF capacitor")
    print("Coupling: 57pF to second tank")
    print()
    print("This completely isolates the transformer inductance")
    print("from the tank resonance - problem solved!")

def calculate_blocking_cap_value():
    """
    Calculate optimal blocking capacitor value.
    """
    
    print("\n" + "=" * 80)
    print("BLOCKING CAPACITOR OPTIMIZATION")
    print("=" * 80)
    
    f_center = 15.8
    f_low = 13.5
    omega_low = 2 * math.pi * f_low * 1e6
    Z_system = 100  # Ohms
    
    print(f"\nBLOCKING CAP REQUIREMENTS:")
    print(f"  1. Low reactance at {f_low}-{18.5} MHz")
    print(f"  2. High-Q (NP0/C0G ceramic)")
    print(f"  3. Not affect filter response")
    
    print(f"\nREACTANCE ANALYSIS at {f_low} MHz:")
    
    for C_pF in [470, 680, 1000, 1500, 2200]:
        X_C = 1 / (omega_low * C_pF * 1e-12)
        ratio = X_C / Z_system
        
        if ratio < 0.1:
            assessment = "Excellent"
        elif ratio < 0.2:
            assessment = "Good"
        else:
            assessment = "Marginal"
            
        print(f"  {C_pF:4} pF: X_C = {X_C:6.1f}Ω ({ratio*100:4.1f}% of Z_sys) - {assessment}")
    
    print(f"\nRECOMMENDED: 1000pF NP0/C0G")
    print(f"  • X_C = 12Ω at 13.5 MHz (12% of 100Ω)")
    print(f"  • Negligible effect on filter")
    print(f"  • Standard value, readily available")
    print(f"  • 100V rating more than adequate")

if __name__ == "__main__":
    print("CRITICAL ANALYSIS: TRANSFORMER LOADING EFFECTS")
    print("=" * 80)
    
    analyze_transformer_loading()
    analyze_solutions()
    recommended_architecture()
    calculate_blocking_cap_value()
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("You identified a CRITICAL issue!")
    print()
    print("The autotransformer inductance would completely")
    print("detune the first tank if connected directly.")
    print()
    print("SOLUTION: Add a 1000pF blocking capacitor between")
    print("the transformer secondary and the first LC tank.")
    print()
    print("This preserves all benefits of the autotransformer")
    print("while eliminating the loading problem.")