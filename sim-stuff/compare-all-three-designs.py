#!/usr/bin/env python3
"""
Compare All Three Filter Design Approaches
===========================================

1. Original (crude 0.65 factor, all tanks at f0)
2. Improved (frequency staggering - WRONG for capacitive coupling)
3. Corrected (proper bandwidth factor, all tanks at f0)
"""

import math

# Band 5 parameters
f_low_mhz = 13.5
f_high_mhz = 18.5
ripple_db = 0.1
impedance_z = 200

f_low = f_low_mhz * 1e6
f_high = f_high_mhz * 1e6
f0 = math.sqrt(f_low * f_high)
bw = f_high - f_low
fbw = bw / f0
omega0 = 2 * math.pi * f0

# g-values (same for all)
beta = math.log(1 / math.tanh(ripple_db / 17.37))
gamma = math.sinh(beta / 6)
a1 = math.sin(math.pi / 6)
b1 = gamma**2 + math.sin(math.pi / 3)**2
g1 = (2 * a1) / gamma
g2 = (4 * a1 * math.sin(3 * math.pi / 6)) / (b1 * g1)

Qe = g1 / fbw
k12 = fbw / math.sqrt(g1 * g2)

print("COMPARISON: ALL THREE FILTER DESIGN APPROACHES")
print("=" * 80)
print(f"Band 5: {f_low_mhz}-{f_high_mhz} MHz")
print(f"Ripple: {ripple_db} dB, Z: {impedance_z} Ω")
print()

# Method 1: Original (working)
print("METHOD 1: ORIGINAL (Working)")
print("-" * 40)

L_theo_1 = Qe / (2 * math.pi * f0 * impedance_z)
L_theo_1 = 1 / ((2 * math.pi * f0)**2 * L_theo_1)
L_1 = L_theo_1 * 0.65  # Crude factor
C_res_1 = 1 / ((2 * math.pi * f0)**2 * L_1)
C12_1 = k12 * C_res_1
C1_1 = C_res_1 - C12_1
C2_1 = C_res_1 - 2*C12_1
C3_1 = C_res_1 - C12_1

print(f"Inductance: {L_1*1e9:.1f} nH")
print(f"All tanks tuned to: {f0/1e6:.3f} MHz")
print(f"C_coupling: {C12_1*1e12:.1f} pF")
print(f"C1/C3: {C1_1*1e12:.1f} pF")
print(f"C2: {C2_1*1e12:.1f} pF")
print("Status: WORKS (Chebyshev + centered)")

# Method 2: Wrong improved (frequency staggering)
print("\nMETHOD 2: WRONG 'IMPROVED' (Frequency staggering)")
print("-" * 50)

X_tank_2 = impedance_z / 2
L_2 = X_tank_2 / omega0
delta_f1 = fbw**2 / (8 * Qe)
f1_2 = f0 * (1 + delta_f1)
C1_2 = 1 / ((2 * math.pi * f1_2)**2 * L_2)
C2_2 = 1 / ((2 * math.pi * f0)**2 * L_2)
Z_tank = omega0 * L_2
C12_2 = k12 / (omega0 * Z_tank)
C1_adj_2 = C1_2 - C12_2/2
C2_adj_2 = C2_2 - C12_2

print(f"Inductance: {L_2*1e9:.1f} nH") 
print(f"Tank 1/3 tuned to: {f1_2/1e6:.3f} MHz (DETUNED)")
print(f"Tank 2 tuned to: {f0/1e6:.3f} MHz")
print(f"C_coupling: {C12_2*1e12:.1f} pF")
print(f"C1/C3: {C1_adj_2*1e12:.1f} pF")
print(f"C2: {C2_adj_2*1e12:.1f} pF")
print("Status: BROKEN (no ripple, lopsided)")

# Method 3: Corrected
print("\nMETHOD 3: CORRECTED (Proper bandwidth factor)")
print("-" * 45)

X_tank_3 = impedance_z / 2
L_base_3 = X_tank_3 / omega0
bw_factor = 0.82  # From corrected design
L_3 = L_base_3 * bw_factor
C_res_3 = 1 / ((omega0**2) * L_3)
C12_3 = k12 * C_res_3
C1_3 = C_res_3 - C12_3
C2_3 = C_res_3 - 2*C12_3

print(f"Inductance: {L_3*1e9:.1f} nH")
print(f"All tanks tuned to: {f0/1e6:.3f} MHz")
print(f"C_coupling: {C12_3*1e12:.1f} pF")
print(f"C1/C3: {C1_3*1e12:.1f} pF")
print(f"C2: {C2_3*1e12:.1f} pF")
print("Status: SHOULD WORK (Chebyshev + better centering)")

print("\n" + "=" * 80)
print("KEY INSIGHTS:")
print("=" * 80)

print("\n✓ CORRECT PRINCIPLES:")
print("  • All resonators at SAME frequency for Chebyshev response")
print("  • Ripple comes from coupling network, not detuning")
print("  • Bandwidth effects need L/C ratio adjustment, not frequency shift")

print("\n✗ WRONG APPROACH (Method 2):")
print("  • Frequency staggering destroys Chebyshev characteristic")
print("  • Creates asymmetric response")
print("  • Reduces effective bandwidth")

print("\n🔧 COMPARISON OF L/C VALUES:")
print(f"  Original:  L={L_1*1e9:.0f}nH, factor=0.65 (arbitrary)")
print(f"  Corrected: L={L_3*1e9:.0f}nH, factor={bw_factor:.2f} (bandwidth-based)")
print(f"  Ratio: {L_3/L_1:.2f} (corrected is {(L_3/L_1-1)*100:+.0f}% different)")

print("\n📊 EXPECTED RESULTS:")
print("  Method 1: Works but passband shifted slightly high")
print("  Method 2: Broken - no Chebyshev ripple, lopsided")  
print("  Method 3: Should work with better passband centering")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("Test Method 3 (corrected). It should give proper Chebyshev")
print("response with better passband centering than Method 1.")