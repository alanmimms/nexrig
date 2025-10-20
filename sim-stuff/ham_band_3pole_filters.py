#!/usr/bin/env python3
"""
3-Pole Chebyshev BPF for Individual Amateur Radio Bands
Uses the proven transformer-coupled design from the original working script
"""

import math
import numpy as np
import subprocess
import matplotlib.pyplot as plt

def calculate_3pole_bpf_components(f_low_mhz, f_high_mhz, ripple_db=0.1):
    """
    Calculate 3-pole Chebyshev BPF using the proven working approach.
    Based on the original transformer-coupled-three-tank-bpf.py
    """
    
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    f0 = math.sqrt(f_low * f_high)
    bw = f_high - f_low
    fbw = bw / f0
    
    print(f"  {f_low_mhz:.2f}-{f_high_mhz:.2f} MHz, FBW: {fbw:.1%}")
    
    # 3rd-order Chebyshev g-values (0.1dB ripple) 
    g0 = 1.0
    g1 = 0.9441
    g2 = 1.4065
    g3 = 0.9441
    g4 = 1.0
    
    # System impedances - use the proven 200Ω filter impedance
    Rs = 50        # Source impedance  
    Z0 = 200       # Filter design impedance
    RL = 50        # Load impedance
    
    omega0 = 2 * math.pi * f0
    
    # Prototype to bandpass transformation
    L1 = g1 * Z0 / (omega0 * fbw)
    C1_series = fbw / (g1 * omega0 * Z0)
    
    L2 = fbw * Z0 / (g2 * omega0) 
    C2_parallel = g2 / (omega0 * fbw * Z0)
    
    L3 = g3 * Z0 / (omega0 * fbw)
    C3_series = fbw / (g3 * omega0 * Z0)
    
    # Apply the proven 0.65 correction factor for proper Chebyshev response
    # This was working correctly in the original design
    correction_factor = 0.65
    
    C1_series *= correction_factor
    C2_parallel *= correction_factor  
    C3_series *= correction_factor
    
    # Calculate tapped capacitor values (hybrid architecture)
    # This creates the impedance transformation within the filter
    n1 = math.sqrt(Rs / Z0)  # Turns ratio for input
    n3 = math.sqrt(Z0 / RL)  # Turns ratio for output
    
    # Tank 1: Tapped capacitor for input matching
    C1_total = C1_series
    C1a = C1_total / (1 - n1**2)  # Main capacitor
    C1b = C1_total * n1**2 / (1 - n1**2)  # Tap capacitor
    
    # Tank 2: Parallel capacitor (no tapping)
    C2 = C2_parallel
    
    # Tank 3: Tapped capacitor for output matching  
    C3_total = C3_series
    C3a = C3_total / (1 - n3**2)  # Main capacitor
    C3b = C3_total * n3**2 / (1 - n3**2)  # Tap capacitor
    
    # Choose toroidal core based on frequency
    if f0 / 1e6 < 5:
        core_type = 'T37-2'
        AL = 5.5
    elif f0 / 1e6 < 15:
        core_type = 'T37-6'
        AL = 4.0
    elif f0 / 1e6 < 30:
        core_type = 'T37-10'
        AL = 2.5
    else:
        core_type = 'T37-12'
        AL = 2.0
    
    # Calculate turns for inductors
    def turns_needed(L_nH, AL_nH_per_turn2):
        return max(2, round(math.sqrt(L_nH / AL_nH_per_turn2)))
    
    L1_nH = L1 * 1e9
    L2_nH = L2 * 1e9  
    L3_nH = L3 * 1e9
    
    results = {
        'band_name': f"{f_low_mhz:.1f}-{f_high_mhz:.1f} MHz",
        'f0_mhz': f0 / 1e6,
        'f_low_mhz': f_low_mhz,
        'f_high_mhz': f_high_mhz,
        'fbw': fbw,
        
        # Inductor values
        'L1_nH': L1_nH,
        'L2_nH': L2_nH,
        'L3_nH': L3_nH,
        
        # Capacitor values (with correction factor applied)
        'C1a_pF': C1a * 1e12,
        'C1b_pF': C1b * 1e12,
        'C2_pF': C2 * 1e12,
        'C3a_pF': C3a * 1e12,
        'C3b_pF': C3b * 1e12,
        
        # Core selection
        'core_type': core_type,
        'AL': AL,
        'L1_turns': turns_needed(L1_nH, AL),
        'L2_turns': turns_needed(L2_nH, AL),
        'L3_turns': turns_needed(L3_nH, AL),
    }
    
    print(f"    L: {L1_nH:.0f}, {L2_nH:.0f}, {L3_nH:.0f} nH")
    print(f"    C: {C1a*1e12:.0f}+{C1b*1e12:.0f}, {C2*1e12:.0f}, {C3a*1e12:.0f}+{C3b*1e12:.0f} pF")
    print(f"    Core: {core_type}")
    
    return results

def create_3pole_netlist(band_num, design):
    """Create ngspice netlist using the proven 3-pole topology."""
    
    netlist = f"""* 3-Pole Chebyshev BPF - {design['band_name']}
* Transformer-coupled hybrid tapped-capacitor design (PROVEN TOPOLOGY)

.param f0={design['f0_mhz']:.3f}meg
.param fbw={design['fbw']:.4f}

* Inductor values
.param L1={design['L1_nH']:.1f}n
.param L2={design['L2_nH']:.1f}n  
.param L3={design['L3_nH']:.1f}n

* Capacitor values (with 0.65 correction factor)
.param C1a={design['C1a_pF']:.2f}p
.param C1b={design['C1b_pF']:.2f}p
.param C2={design['C2_pF']:.2f}p
.param C3a={design['C3a_pF']:.2f}p
.param C3b={design['C3b_pF']:.2f}p

* === SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === FILTER SECTION ===
* Tank 1: Tapped capacitor for input matching (hybrid architecture)
L1 n1 n2 {{L1}}
C1a n2 0 {{C1a}}
C1b n1 0 {{C1b}}

* Tank 2: Standard parallel tank
L2 n2 n3 {{L2}}
C2 n3 0 {{C2}}

* Tank 3: Tapped capacitor for output matching  
L3 n3 n4 {{L3}}
C3a n4 0 {{C3a}}
C3b n3 0 {{C3b}}

* === LOAD ===
RL n4 0 50

* === ANALYSIS ===
.ac dec 100 100k 100meg
.control
run
print frequency vdb(n4)
.endc
.end
"""
    
    filename = f"ham_band_{band_num}_3pole.cir"
    with open(filename, 'w') as f:
        f.write(netlist)
    
    return filename

def design_all_ham_bands():
    """Design 3-pole BPFs for all amateur radio bands."""
    
    # Combined amateur radio bands for practical fractional bandwidths
    ham_bands = [
        {'name': '160m', 'f_low': 1.8, 'f_high': 2.0, 'color': 'navy'},
        {'name': '80m', 'f_low': 3.5, 'f_high': 4.0, 'color': 'blue'}, 
        {'name': '40m', 'f_low': 7.0, 'f_high': 7.3, 'color': 'cyan'},
        {'name': '30m+20m', 'f_low': 10.1, 'f_high': 14.35, 'color': 'green'},
        {'name': '17m+15m', 'f_low': 18.0, 'f_high': 21.45, 'color': 'orange'},
        {'name': '12m+10m', 'f_low': 24.9, 'f_high': 29.7, 'color': 'red'},
    ]
    
    print("3-POLE CHEBYSHEV BPF - 6 COMBINED AMATEUR RADIO BANDS")
    print("=" * 70)
    print("Using proven transformer-coupled hybrid tapped-capacitor topology")
    print()
    
    results = []
    
    for i, band in enumerate(ham_bands, 1):
        print(f"Band {i}: {band['name']}")
        design = calculate_3pole_bpf_components(band['f_low'], band['f_high'])
        design['band_num'] = i
        design['color'] = band['color']
        design['ham_name'] = band['name']
        
        # Create netlist and run simulation
        filename = create_3pole_netlist(i, design)
        
        try:
            result = subprocess.run(['ngspice', '-b', filename], 
                                  capture_output=True, text=True, check=True)
            
            frequencies = []
            gains = []
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line or line.startswith('*') or line.startswith('Note:') or line.startswith('Circuit:') or line.startswith('Doing') or line.startswith('No. of') or line.startswith('Index') or '---' in line or line.startswith('Using') or 'analysis' in line.lower():
                    continue
                
                try:
                    parts = line.replace('\t', ' ').split()
                    if len(parts) >= 3:
                        freq_hz = float(parts[1])
                        gain_db = float(parts[2])
                        freq_mhz = freq_hz / 1e6
                        frequencies.append(freq_mhz)
                        gains.append(gain_db)
                except (ValueError, IndexError):
                    continue
            
            if frequencies:
                design['frequencies'] = np.array(frequencies)
                design['gains'] = np.array(gains)
                results.append(design)
                print(f"    ✓ Simulation successful")
            else:
                print(f"    ✗ No simulation data")
                
        except subprocess.CalledProcessError as e:
            print(f"    ✗ Simulation failed")
        
        print()
    
    # Create plot
    if results:
        plt.figure(figsize=(16, 10))
        
        for design in results:
            plt.semilogx(design['frequencies'], design['gains'], 
                        color=design['color'], linewidth=2,
                        label=f"{design['ham_name']}: {design['band_name']}")
            
            # Mark amateur band
            plt.axvspan(design['f_low_mhz'], design['f_high_mhz'], 
                       alpha=0.1, color=design['color'])
        
        plt.axhline(-3, color='gray', linestyle='--', alpha=0.7, label='-3dB')
        plt.axhline(-20, color='gray', linestyle=':', alpha=0.7, label='-20dB')
        plt.axhline(-60, color='gray', linestyle=':', alpha=0.7, label='-60dB')
        
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Gain (dB)')
        plt.title('3-Pole Chebyshev BPF - 6 Combined Amateur Radio Bands (Back to Basics!)')
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xlim(1, 35)
        plt.ylim(-80, 5)
        
        # 5MHz grid marks
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 35])
        for freq in [5, 10, 15, 20, 25, 30]:
            plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('ham_bands_6_combined_response.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved ham_bands_6_combined_response.png")
        
        # Summary table
        print("COMPONENT SUMMARY")
        print("=" * 80)
        print(f"{'Band':<8} | {'Range (MHz)':<12} | {'FBW':<6} | {'L (nH)':<15} | {'C (pF)':<25} | {'Core':<8}")
        print("-" * 80)
        
        for design in results:
            band_str = design['ham_name']
            range_str = f"{design['f_low_mhz']:.1f}-{design['f_high_mhz']:.1f}"
            fbw_str = f"{design['fbw']:.0%}"
            l_str = f"{design['L1_nH']:.0f},{design['L2_nH']:.0f},{design['L3_nH']:.0f}"
            c_str = f"{design['C1a_pF']:.0f}+{design['C1b_pF']:.0f},{design['C2_pF']:.0f},{design['C3a_pF']:.0f}+{design['C3b_pF']:.0f}"
            
            print(f"{band_str:<8} | {range_str:<12} | {fbw_str:<6} | {l_str:<15} | {c_str:<25} | {design['core_type']:<8}")
        
        return True
    
    else:
        print("✗ No successful simulations")
        return False

if __name__ == '__main__':
    design_all_ham_bands()