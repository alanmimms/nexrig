#!/usr/bin/env python3
"""
Simplified filter plotting without SPICE simulation
Shows the calculated values and theoretical response
"""

import math
import numpy as np
import matplotlib.pyplot as plt

# Filter results from our calculations
results = {
    'f_center': 15.803,
    'bandwidth': 5.0,
    'tank_inductor_nh': 1000.0,
    'tank_cap_pf': 101.42,
    'coupling_cap_pf': 20.147,
    'c_hot_input_pf': 202.41,
    'c_cold_input_pf': 101.2,
    'c_hot_output_pf': 202.41,
    'c_cold_output_pf': 101.2
}

def plot_theoretical_response():
    """Plot theoretical Chebyshev response and component values"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Generate frequency range
    f_plot = np.logspace(0, 2, 1000)  # 1 to 100 MHz
    omega = 2 * np.pi * f_plot * 1e6
    omega_0 = 2 * np.pi * results['f_center'] * 1e6
    
    # Normalized frequency for Chebyshev response
    fractional_bw = results['bandwidth'] / results['f_center']
    w_norm = (omega/omega_0 - omega_0/omega) / fractional_bw
    
    # Chebyshev response (3rd order, 0.1dB ripple)
    epsilon = math.sqrt(10**(0.1/10) - 1)
    T3 = 4*w_norm**3 - 3*w_norm  # Chebyshev polynomial T3(x) = 4x³ - 3x
    
    # Avoid overflow for large |T3|
    T3_clipped = np.clip(T3, -100, 100)
    H_ideal = 1 / np.sqrt(1 + epsilon**2 * T3_clipped**2)
    H_ideal_db = 20 * np.log10(np.maximum(H_ideal, 1e-10))  # Avoid log(0)
    
    # Plot ideal response
    ax1.semilogx(f_plot, H_ideal_db, 'r-', linewidth=2, label='Theoretical Chebyshev')
    
    # Mark passband edges
    f_low = results['f_center'] - results['bandwidth']/2
    f_high = results['f_center'] + results['bandwidth']/2
    ax1.axvline(x=f_low, color='g', linestyle='--', alpha=0.7, label=f'Passband edges')
    ax1.axvline(x=f_high, color='g', linestyle='--', alpha=0.7)
    ax1.axvline(x=results['f_center'], color='b', linestyle=':', alpha=0.7, label=f"f₀ = {results['f_center']:.1f} MHz")
    
    # Mark -3dB line
    ax1.axhline(y=-3, color='orange', linestyle='--', alpha=0.5, label='-3dB line')
    
    # Format main plot
    ax1.set_xlabel('Frequency (MHz)')
    ax1.set_ylabel('Gain (dB)')
    ax1.set_title('Theoretical Chebyshev Bandpass Filter Response (3rd Order, 0.1dB Ripple)')
    ax1.grid(True, which="both", ls="-", alpha=0.3)
    ax1.set_xlim([5, 50])
    ax1.set_ylim([-60, 5])
    ax1.legend()
    
    # Add annotations
    ax1.text(results['f_center'], -10, 
            f"BW: {results['bandwidth']:.1f} MHz\\nf₀: {results['f_center']:.1f} MHz\\nQ: {results['f_center']/results['bandwidth']:.1f}",
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
            ha='center')
    
    # Component values table
    ax2.axis('off')
    component_text = f"""
CALCULATED COMPONENT VALUES (matching your schematic):
════════════════════════════════════════════════════════

Tank Resonators:
  • Inductors (L1, L2, L3):     {results['tank_inductor_nh']:.0f} nH
  • Capacitors (C1, C2, C3):    {results['tank_cap_pf']:.1f} pF

Inter-resonator Coupling:
  • C12 (Tank 1→2):             {results['coupling_cap_pf']:.1f} pF  
  • C23 (Tank 2→3):             {results['coupling_cap_pf']:.1f} pF

Input Matching Network (Tapped Capacitors):
  • C_hot (series, to source):  {results['c_hot_input_pf']:.1f} pF
  • C_cold (shunt, to ground):  {results['c_cold_input_pf']:.1f} pF
  • Ratio (hot/cold):           {results['c_hot_input_pf']/results['c_cold_input_pf']:.2f}

Output Matching Network (Tapped Capacitors):  
  • C_hot (series, to load):    {results['c_hot_output_pf']:.1f} pF
  • C_cold (shunt, to ground):  {results['c_cold_output_pf']:.1f} pF

Design Notes:
  • All tank resonators tuned to f₀ = {results['f_center']:.1f} MHz
  • Coupling caps provide inter-resonator coupling
  • Tapped-C networks provide 50Ω matching + input/output coupling
  • Values match your KiCad schematic (202.8pF ≈ {results['c_hot_input_pf']:.1f}pF)
"""
    
    ax2.text(0.05, 0.95, component_text, transform=ax2.transAxes, 
            fontfamily='monospace', fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('theoretical_filter_response.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("\\nTheoretical filter response plotted!")
    print("Component values calculated to match your schematic.")
    print("Plot saved as 'theoretical_filter_response.png'")
    print("\\nThe calculated values should work properly in your simulation.")

if __name__ == "__main__":
    plot_theoretical_response()