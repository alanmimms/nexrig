#!/usr/bin/env python3
"""
CORRECTED 3-Pole Chebyshev BPF for Amateur Radio Bands
Uses the EXACT working equations from transformer-coupled-three-tank-bpf.py
"""

import math
import numpy as np
import subprocess
import matplotlib.pyplot as plt

def calculate_filter_components(f_low_mhz, f_high_mhz, ripple_db, impedance_z):
    """
    EXACT copy of the working calculation from transformer-coupled-three-tank-bpf.py
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
    # This 0.65 correction factor was proven to work correctly
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

    # --- 5. Toroid Selection ---
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
    
    # Package results
    results = {
        "f_low_mhz": f_low_mhz,
        "f_high_mhz": f_high_mhz,
        "f0_mhz": f0_mhz,
        "fbw": fbw,
        "L_nH": L_nH,
        "C_couple_pF": C12 * 1e12,
        "C1_adj_pF": C1_adj * 1e12,
        "C2_adj_pF": C2_adj * 1e12,
        "C3_adj_pF": C3_adj * 1e12,
        "core_name": best_core_name,
        "AL": AL
    }
    
    return results

def create_corrected_netlist(band_num, band_name, design):
    """Create ngspice netlist using the CORRECT working topology."""
    
    netlist = f"""* 3-Pole Chebyshev BPF - {band_name}
* CORRECTED - Using exact working equations from transformer-coupled design

.param f0={design['f0_mhz']:.3f}meg
.param fbw={design['fbw']:.4f}

* Component values (CORRECTED)
.param L={design['L_nH']:.1f}n
.param C_couple={design['C_couple_pF']:.2f}p
.param C1_adj={design['C1_adj_pF']:.2f}p
.param C2_adj={design['C2_adj_pF']:.2f}p
.param C3_adj={design['C3_adj_pF']:.2f}p

* === SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === 3-POLE COUPLED RESONATOR FILTER ===
* Tank 1
L1 n1 n2 {{L}}
C1 n2 0 {{C1_adj}}

* Tank 2 (coupled to Tank 1 and Tank 3)
L2 n3 n4 {{L}}
C2 n4 0 {{C2_adj}}

* Tank 3  
L3 n5 n6 {{L}}
C3 n6 0 {{C3_adj}}

* Coupling capacitors
C12 n2 n3 {{C_couple}}  ; Tank 1 to Tank 2
C23 n4 n5 {{C_couple}}  ; Tank 2 to Tank 3

* === LOAD ===
RL n6 0 50

* === ANALYSIS ===
.ac dec 100 100k 100meg
.control
run
print frequency vdb(n6)
.endc
.end
"""
    
    filename = f"corrected_band_{band_num}.cir"
    with open(filename, 'w') as f:
        f.write(netlist)
    
    return filename

def design_corrected_ham_bands():
    """Design CORRECTED 3-pole BPFs using proven working equations."""
    
    # Combined amateur radio bands 
    ham_bands = [
        {'name': '160m', 'f_low': 1.8, 'f_high': 2.0, 'color': 'navy'},
        {'name': '80m', 'f_low': 3.5, 'f_high': 4.0, 'color': 'blue'}, 
        {'name': '40m', 'f_low': 7.0, 'f_high': 7.3, 'color': 'cyan'},
        {'name': '30m+20m', 'f_low': 10.1, 'f_high': 14.35, 'color': 'green'},
        {'name': '17m+15m', 'f_low': 18.0, 'f_high': 21.45, 'color': 'orange'},
        {'name': '12m+10m', 'f_low': 24.9, 'f_high': 29.7, 'color': 'red'},
    ]
    
    print("CORRECTED 3-POLE CHEBYSHEV BPF - 6 AMATEUR RADIO BANDS")
    print("=" * 70)
    print("Using EXACT working equations from proven transformer-coupled design")
    print()
    
    results = []
    
    for i, band in enumerate(ham_bands, 1):
        print(f"Band {i}: {band['name']} ({band['f_low']:.1f}-{band['f_high']:.1f} MHz)")
        
        # Use the exact working calculation
        design = calculate_filter_components(band['f_low'], band['f_high'], 0.1, 200)
        
        if design:
            design['band_num'] = i
            design['color'] = band['color']
            design['ham_name'] = band['name']
            
            print(f"  FBW: {design['fbw']:.1%}")
            print(f"  L: {design['L_nH']:.0f} nH")
            print(f"  C: {design['C1_adj_pF']:.1f}, {design['C2_adj_pF']:.1f}, {design['C3_adj_pF']:.1f} pF")
            print(f"  C_couple: {design['C_couple_pF']:.1f} pF")
            print(f"  Core: {design['core_name']}")
            
            # Create netlist and simulate
            filename = create_corrected_netlist(i, band['name'], design)
            
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
                    print(f"  ✓ Simulation successful")
                else:
                    print(f"  ✗ No simulation data")
                    
            except subprocess.CalledProcessError:
                print(f"  ✗ Simulation failed")
        else:
            print(f"  ✗ No suitable core found")
        
        print()
    
    # Create CORRECTED plot with proper formatting
    if results:
        plt.figure(figsize=(16, 10))
        
        for design in results:
            plt.semilogx(design['frequencies'], design['gains'], 
                        color=design['color'], linewidth=2,
                        label=f"{design['ham_name']}: {design['f_low_mhz']:.1f}-{design['f_high_mhz']:.1f} MHz")
            
            # Mark amateur band with colored box
            plt.axvspan(design['f_low_mhz'], design['f_high_mhz'], 
                       alpha=0.15, color=design['color'])
        
        # Remove Y-axis reference lines from legend (keep only on axis)
        plt.axhline(-3, color='gray', linestyle='--', alpha=0.7)
        plt.axhline(-20, color='gray', linestyle=':', alpha=0.7)
        plt.axhline(-60, color='gray', linestyle=':', alpha=0.7)
        
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Gain (dB)')
        plt.title('3-Pole Chebyshev BPF - 6 Amateur Radio Bands (CORRECTED)')
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # CORRECTED axis range: 1-32MHz with 5MHz grid marks
        plt.xlim(1, 32)
        plt.ylim(-80, 5)
        
        # X-axis ticks every 5MHz from 5 to 30, plus 1 and 32
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 32])
        
        # Vertical grid lines every 5MHz
        for freq in [5, 10, 15, 20, 25, 30]:
            plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('corrected_ham_bands_response.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved corrected_ham_bands_response.png")
        
        return True
    
    else:
        print("✗ No successful simulations")
        return False

if __name__ == '__main__':
    design_corrected_ham_bands()