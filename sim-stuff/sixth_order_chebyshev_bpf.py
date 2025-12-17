#!/usr/bin/env python3
"""
6th-Order Chebyshev Bandpass Filter Design
Proper implementation using coupled resonator topology
"""

import math
import numpy as np
import subprocess
import matplotlib.pyplot as plt

def design_6th_order_chebyshev_bpf(f_low_mhz, f_high_mhz, ripple_db=0.1):
    """
    Design 6th-order Chebyshev bandpass filter.
    Uses capacitively-coupled resonator topology.
    """
    
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    f0 = math.sqrt(f_low * f_high)  # Geometric center frequency
    bw = f_high - f_low
    fbw = bw / f0  # Fractional bandwidth
    
    omega0 = 2 * math.pi * f0
    
    print(f"  Center frequency: {f0/1e6:.2f} MHz")
    print(f"  Bandwidth: {bw/1e6:.2f} MHz")
    print(f"  Fractional BW: {fbw:.1%}")
    
    # 6th-order Chebyshev g-values (0.1dB ripple)
    g0 = 1.0
    g1 = 1.0315
    g2 = 1.1474
    g3 = 1.9841
    g4 = 1.1474
    g5 = 1.0315
    g6 = 1.0000
    
    # System impedances
    Z_source = 50      # Source impedance
    Z_filter = 200     # Filter design impedance
    Z_load = 50        # Load impedance
    
    # Transform to bandpass using standard BPF transformation
    # For coupled resonator topology
    
    # Resonator values (all tuned to f0)
    L_res = Z_filter / (omega0 * fbw)  # Resonator inductance
    C_res = 1 / (omega0**2 * L_res)   # Resonator capacitance
    
    # Coupling capacitors (between resonators)
    # These determine the bandwidth and shape
    k12 = fbw * math.sqrt(g1 * g2) / g1  # Coupling 1-2
    k23 = fbw * math.sqrt(g2 * g3) / g2  # Coupling 2-3
    k34 = fbw * math.sqrt(g3 * g4) / g3  # Coupling 3-4
    k45 = fbw * math.sqrt(g4 * g5) / g4  # Coupling 4-5
    k56 = fbw * math.sqrt(g5 * g6) / g5  # Coupling 5-6
    
    # Convert coupling coefficients to capacitance values
    C12 = k12 * C_res
    C23 = k23 * C_res
    C34 = k34 * C_res
    C45 = k45 * C_res
    C56 = k56 * C_res
    
    # Input/output coupling
    # Source and load coupling determine input/output matching
    k_source = fbw / math.sqrt(g0 * g1)
    k_load = fbw / math.sqrt(g5 * g6)
    
    C_source = k_source * C_res
    C_load = k_load * C_res
    
    # Transform for impedance matching (50Ω to 200Ω)
    # Need 4:1 impedance transformation = 2:1 turns ratio
    L_trans_pri = L_res / 4  # Primary side (50Ω)
    L_trans_sec = L_res      # Secondary side (200Ω)
    
    results = {
        'f0_mhz': f0 / 1e6,
        'f_low_mhz': f_low_mhz,
        'f_high_mhz': f_high_mhz,
        'fbw': fbw,
        
        # Resonator components (all identical, tuned to f0)
        'L_res_nH': L_res * 1e9,
        'C_res_pF': C_res * 1e12,
        
        # Coupling capacitors
        'C12_pF': C12 * 1e12,
        'C23_pF': C23 * 1e12,
        'C34_pF': C34 * 1e12,
        'C45_pF': C45 * 1e12,
        'C56_pF': C56 * 1e12,
        
        # I/O coupling
        'C_source_pF': C_source * 1e12,
        'C_load_pF': C_load * 1e12,
        
        # Transformer values
        'L_trans_pri_nH': L_trans_pri * 1e9,
        'L_trans_sec_nH': L_trans_sec * 1e9,
    }
    
    print(f"  Resonator: L={L_res*1e9:.0f}nH, C={C_res*1e12:.0f}pF")
    print(f"  Coupling caps: {C12*1e12:.1f}, {C23*1e12:.1f}, {C34*1e12:.1f}, {C45*1e12:.1f}, {C56*1e12:.1f} pF")
    print(f"  I/O coupling: {C_source*1e12:.1f}, {C_load*1e12:.1f} pF")
    
    return results

def create_6th_order_bpf_netlist(band_num, band_name, design):
    """Create ngspice netlist for 6th-order coupled resonator BPF."""
    
    netlist = f"""* 6th-Order Chebyshev Bandpass Filter - {band_name}
* Coupled resonator topology with transformers

.param f0={design['f0_mhz']}meg
.param fbw={design['fbw']:.4f}

* Resonator components (all identical, tuned to f0)
.param L_res={design['L_res_nH']:.1f}n
.param C_res={design['C_res_pF']:.1f}p

* Coupling capacitors
.param C12={design['C12_pF']:.2f}p
.param C23={design['C23_pF']:.2f}p
.param C34={design['C34_pF']:.2f}p
.param C45={design['C45_pF']:.2f}p
.param C56={design['C56_pF']:.2f}p

* I/O coupling
.param C_src={design['C_source_pF']:.2f}p
.param C_load={design['C_load_pF']:.2f}p

* Transformer values
.param L_pri={design['L_trans_pri_nH']:.1f}n
.param L_sec={design['L_trans_sec_nH']:.1f}n

* === SIGNAL SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === INPUT TRANSFORMER (50Ω → 200Ω) ===
L_T1_pri n1 0 {{L_pri}}
L_T1_sec n2 0 {{L_sec}}
K_T1 L_T1_pri L_T1_sec 0.95

* === 6th-ORDER COUPLED RESONATOR BPF ===
* Tank 1
L1 n3 n4 {{L_res}}
C1 n4 0 {{C_res}}
* Tank 2  
L2 n5 n6 {{L_res}}
C2 n6 0 {{C_res}}
* Tank 3
L3 n7 n8 {{L_res}}
C3 n8 0 {{C_res}}
* Tank 4
L4 n9 n10 {{L_res}}
C4 n10 0 {{C_res}}
* Tank 5
L5 n11 n12 {{L_res}}
C5 n12 0 {{C_res}}
* Tank 6
L6 n13 n14 {{L_res}}
C6 n14 0 {{C_res}}

* Coupling network
C_source n2 n3 {{C_src}}    ; Input coupling
C_12 n4 n5 {{C12}}          ; Tank 1-2 coupling
C_23 n6 n7 {{C23}}          ; Tank 2-3 coupling
C_34 n8 n9 {{C34}}          ; Tank 3-4 coupling
C_45 n10 n11 {{C45}}        ; Tank 4-5 coupling
C_56 n12 n13 {{C56}}        ; Tank 5-6 coupling
C_load n14 n15 {{C_load}}   ; Output coupling

* === OUTPUT TRANSFORMER (200Ω → 50Ω) ===
L_T2_sec n15 0 {{L_sec}}
L_T2_pri n16 0 {{L_pri}}
K_T2 L_T2_sec L_T2_pri 0.95

* === OUTPUT LOAD ===
Rload n16 0 50

* === ANALYSIS ===
.ac dec 100 100k 100meg
.control
run
print frequency vdb(n16)
.endc
.end
"""
    
    filename = f"6th_order_bpf_band{band_num}.cir"
    with open(filename, 'w') as f:
        f.write(netlist)
    
    return filename

def run_6th_order_simulation():
    """Design and simulate 6th-order Chebyshev BPFs for all bands."""
    
    bands = [
        {'num': 1, 'name': 'HF-Low', 'f_low': 1.8, 'f_high': 4.6, 'color': 'blue'},
        {'num': 2, 'name': 'HF-Mid', 'f_low': 4.4, 'f_high': 10.1, 'color': 'red'},
        {'num': 3, 'name': 'HF-High', 'f_low': 9.9, 'f_high': 18.1, 'color': 'green'},
        {'num': 4, 'name': 'HF-VHF', 'f_low': 17.9, 'f_high': 30.0, 'color': 'orange'}
    ]
    
    print("6TH-ORDER CHEBYSHEV BANDPASS FILTER DESIGN")
    print("=" * 60)
    
    results = []
    
    for band in bands:
        print(f"\n{band['name']}: {band['f_low']}-{band['f_high']} MHz")
        print("-" * 40)
        
        # Design the filter
        design = design_6th_order_chebyshev_bpf(band['f_low'], band['f_high'])
        
        # Create netlist
        filename = create_6th_order_bpf_netlist(band['num'], band['name'], design)
        
        # Run simulation
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
                band['design'] = design
                results.append(band)
                print(f"✓ Simulation successful: {len(frequencies)} points")
            else:
                print("✗ No simulation data")
                
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
        plt.title('6th-Order Chebyshev Bandpass Filters - Clean Response Expected')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xlim(1, 50)
        plt.ylim(-100, 10)
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
        
        # Add vertical grid lines at 5MHz intervals
        for freq in [5, 10, 15, 20, 25, 30, 35, 40, 45]:
            plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('6th_order_chebyshev_bpf_response.png', dpi=150)
        plt.close()
        
        print(f"\n✓ Saved 6th_order_chebyshev_bpf_response.png")
        return True
    
    else:
        print("\n✗ No successful simulations")
        return False

if __name__ == '__main__':
    run_6th_order_simulation()