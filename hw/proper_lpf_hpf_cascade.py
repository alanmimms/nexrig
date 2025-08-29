#!/usr/bin/env python3
"""
Create proper LPF+HPF cascade with correct topology
"""

import subprocess
import numpy as np
import matplotlib.pyplot as plt

def create_proper_cascade_netlist(band_num, band_name, f_low_mhz, f_high_mhz):
    """Create properly designed LPF+HPF cascade."""
    
    # Use the same design approach as the original working design
    import math
    
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    omega_low = 2 * math.pi * f_low
    omega_high = 2 * math.pi * f_high
    
    # 3rd-order Chebyshev g-values (0.1dB ripple)
    g1 = 0.9441
    g2 = 1.4065
    g3 = 0.9441
    
    Z_filter = 200  # Filter impedance
    
    # === LPF DESIGN ===
    L1_lpf = g1 * Z_filter / omega_high
    C1_lpf = g2 / (omega_high * Z_filter)
    L2_lpf = g3 * Z_filter / omega_high
    
    # === HPF DESIGN === 
    C1_hpf = 1 / (g1 * omega_low * Z_filter)
    L1_hpf = g2 * Z_filter / omega_low
    C2_hpf = 1 / (g3 * omega_low * Z_filter)
    
    # Convert to convenient units
    L1_lpf_nH = L1_lpf * 1e9
    C1_lpf_pF = C1_lpf * 1e12
    L2_lpf_nH = L2_lpf * 1e9
    
    C1_hpf_pF = C1_hpf * 1e12
    L1_hpf_nH = L1_hpf * 1e9
    C2_hpf_pF = C2_hpf * 1e12
    
    # Input/output transformer values (4:1 impedance ratio = 2:1 turns)
    L_pri = L1_lpf / 4  # Primary inductance
    L_sec = L1_lpf      # Secondary inductance
    
    L_pri_nH = L_pri * 1e9
    L_sec_nH = L_sec * 1e9
    
    netlist = f"""* Proper LPF+HPF Cascade - {band_name}
* Input transformer + 3rd-order LPF + 3rd-order HPF + output transformer

.param f_low={f_low_mhz}meg
.param f_high={f_high_mhz}meg

* Component values
.param L_in_pri={L_pri_nH:.1f}n
.param L_in_sec={L_sec_nH:.1f}n
.param L1_lpf={L1_lpf_nH:.1f}n
.param C1_lpf={C1_lpf_pF:.1f}p
.param L2_lpf={L2_lpf_nH:.1f}n

.param C1_hpf={C1_hpf_pF:.1f}p
.param L1_hpf={L1_hpf_nH:.1f}n
.param C2_hpf={C2_hpf_pF:.1f}p
.param L_out_pri={L_pri_nH:.1f}n
.param L_out_sec={L_sec_nH:.1f}n

* === SIGNAL SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === INPUT TRANSFORMER (50Ω → 200Ω) ===
L_Tin_pri n1 0 {{L_in_pri}}
L_Tin_sec n2 0 {{L_in_sec}}
K_Tin L_Tin_pri L_Tin_sec 0.95

* === 3rd-ORDER LOW-PASS FILTER (200Ω) ===
L_lpf1 n2 n3 {{L1_lpf}}
C_lpf1 n3 0 {{C1_lpf}}
L_lpf2 n3 n4 {{L2_lpf}}

* === 3rd-ORDER HIGH-PASS FILTER (200Ω) ===
C_hpf1 n4 n5 {{C1_hpf}}
L_hpf1 n5 0 {{L1_hpf}}
C_hpf2 n5 n6 {{C2_hpf}}

* === OUTPUT TRANSFORMER (200Ω → 50Ω) ===
L_Tout_sec n6 0 {{L_out_sec}}
L_Tout_pri n7 0 {{L_out_pri}}
K_Tout L_Tout_sec L_Tout_pri 0.95

* === OUTPUT LOAD ===
Rload n7 0 50

* === ANALYSIS ===
.ac dec 100 100k 100meg
.control
run
print frequency vdb(n7)
.endc
.end
"""
    
    filename = f"proper_cascade_band{band_num}.cir"
    with open(filename, 'w') as f:
        f.write(netlist)
    
    return filename

def run_proper_simulation():
    """Run simulation with proper LPF+HPF cascade topology."""
    
    bands = [
        {'num': 1, 'name': 'HF-Low', 'f_low': 1.8, 'f_high': 4.6, 'color': 'blue'},
        {'num': 2, 'name': 'HF-Mid', 'f_low': 4.4, 'f_high': 10.1, 'color': 'red'},
        {'num': 3, 'name': 'HF-High', 'f_low': 9.9, 'f_high': 18.1, 'color': 'green'},
        {'num': 4, 'name': 'HF-VHF', 'f_low': 17.9, 'f_high': 30.0, 'color': 'orange'}
    ]
    
    results = []
    
    for band in bands:
        print(f"Simulating {band['name']} ({band['f_low']}-{band['f_high']} MHz)...")
        
        filename = create_proper_cascade_netlist(
            band['num'], band['name'], band['f_low'], band['f_high']
        )
        
        try:
            result = subprocess.run(['ngspice', '-b', filename], 
                                  capture_output=True, text=True, check=True)
            
            frequencies = []
            gains = []
            
            # Parse ngspice output
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
                band['frequencies'] = np.array(frequencies)
                band['gains'] = np.array(gains)
                results.append(band)
                print(f"✓ {len(frequencies)} data points")
            else:
                print("✗ No data")
                
        except subprocess.CalledProcessError as e:
            print(f"✗ Simulation failed: {e}")
    
    # Plot results
    if results:
        plt.figure(figsize=(14, 8))
        
        for band in results:
            plt.semilogx(band['frequencies'], band['gains'], 
                        color=band['color'], linewidth=2,
                        label=f"Band {band['num']}: {band['name']} ({band['f_low']}-{band['f_high']} MHz)")
            
            # Mark passband
            plt.axvspan(band['f_low'], band['f_high'], alpha=0.1, color=band['color'])
        
        plt.axhline(-3, color='gray', linestyle='--', alpha=0.7, label='-3dB')
        plt.axhline(-20, color='gray', linestyle=':', alpha=0.7, label='-20dB') 
        plt.axhline(-60, color='gray', linestyle=':', alpha=0.7, label='-60dB')
        
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Gain (dB)')
        plt.title('LPF+HPF Cascade Filters - 4 Wide Bands (CORRECTED TOPOLOGY)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xlim(1, 50)
        plt.ylim(-100, 10)
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
        
        # Add vertical grid lines at 5MHz intervals
        for freq in [5, 10, 15, 20, 25, 30, 35, 40, 45]:
            plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('lpf_hpf_cascade_response_corrected.png', dpi=150)
        plt.close()
        
        print("✓ Saved proper_cascade_response.png")
        return True
    
    return False

if __name__ == '__main__':
    print("PROPER LPF+HPF CASCADE TEST")
    print("=" * 40)
    run_proper_simulation()