#!/usr/bin/env python3
"""
Individual 3rd-order Chebyshev BPF for each narrow ham band
Keep fractional bandwidths reasonable (<10% where possible)
"""

import math
import numpy as np
import subprocess
import matplotlib.pyplot as plt

def design_3rd_order_bpf(f_low_mhz, f_high_mhz, band_name):
    """Design 3rd-order Chebyshev BPF for specific ham band."""
    
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    f0 = math.sqrt(f_low * f_high)
    bw = f_high - f_low
    fbw = bw / f0
    
    print(f"  {band_name}: {f_low_mhz:.2f}-{f_high_mhz:.2f} MHz")
    print(f"    f0 = {f0/1e6:.2f} MHz, BW = {bw/1e3:.0f} kHz, FBW = {fbw:.1%}")
    
    # 3rd-order Chebyshev prototype (0.1dB ripple)
    g1 = 0.9441
    g2 = 1.4065
    g3 = 0.9441
    
    # Design impedance
    Z0 = 50  # Keep it simple - 50Ω throughout
    omega0 = 2 * math.pi * f0
    
    # Bandpass transformation for 3rd-order
    # Series resonators (L1, C1 and L3, C3)
    L1 = g1 * Z0 / (omega0 * fbw)
    C1 = fbw / (g1 * omega0 * Z0)
    
    L3 = g3 * Z0 / (omega0 * fbw) 
    C3 = fbw / (g3 * omega0 * Z0)
    
    # Parallel resonator (L2, C2)
    L2 = fbw * Z0 / (g2 * omega0)
    C2 = g2 / (omega0 * fbw * Z0)
    
    # Convert to practical units
    L1_nH = L1 * 1e9
    C1_pF = C1 * 1e12
    L2_nH = L2 * 1e9
    C2_pF = C2 * 1e12
    L3_nH = L3 * 1e9
    C3_pF = C3 * 1e12
    
    print(f"    L1={L1_nH:.0f}nH, C1={C1_pF:.0f}pF (series)")
    print(f"    L2={L2_nH:.0f}nH, C2={C2_pF:.0f}pF (parallel)")
    print(f"    L3={L3_nH:.0f}nH, C3={C3_pF:.0f}pF (series)")
    
    return {
        'band_name': band_name,
        'f_low_mhz': f_low_mhz,
        'f_high_mhz': f_high_mhz,
        'f0_mhz': f0 / 1e6,
        'fbw': fbw,
        'L1_nH': L1_nH,
        'C1_pF': C1_pF,
        'L2_nH': L2_nH,
        'C2_pF': C2_pF,
        'L3_nH': L3_nH,
        'C3_pF': C3_pF
    }

def create_bpf_netlist(design, band_num):
    """Create ngspice netlist for 3rd-order BPF."""
    
    netlist = f"""* 3rd-Order Chebyshev BPF - {design['band_name']}
* Individual ham band: {design['f_low_mhz']:.2f}-{design['f_high_mhz']:.2f} MHz

.param f0={design['f0_mhz']:.3f}meg
.param fbw={design['fbw']:.4f}

* Component values
.param L1={design['L1_nH']:.1f}n
.param C1={design['C1_pF']:.1f}p
.param L2={design['L2_nH']:.1f}n
.param C2={design['C2_pF']:.1f}p
.param L3={design['L3_nH']:.1f}n
.param C3={design['C3_pF']:.1f}p

* === SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === 3RD-ORDER CHEBYSHEV BANDPASS ===
* Series resonator 1 (L1-C1)
L1 n1 n2 {{L1}}
C1 n2 n3 {{C1}}

* Parallel resonator (L2-C2)
L2 n3 n4 {{L2}}
C2 n3 0 {{C2}}

* Series resonator 3 (L3-C3)
L3 n4 n5 {{L3}}
C3 n5 n6 {{C3}}

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
    
    filename = f'ham_band_{band_num}_{design["band_name"].replace("/", "_")}.cir'
    with open(filename, 'w') as f:
        f.write(netlist)
    
    return filename

def simulate_all_ham_bands():
    """Design and simulate individual BPFs for all ham bands."""
    
    # Individual ham bands with realistic narrow limits
    ham_bands = [
        {'name': '160m', 'f_low': 1.80, 'f_high': 2.00, 'color': 'navy'},
        {'name': '80m', 'f_low': 3.50, 'f_high': 4.00, 'color': 'blue'},
        {'name': '40m', 'f_low': 7.00, 'f_high': 7.30, 'color': 'cyan'},
        {'name': '30m', 'f_low': 10.10, 'f_high': 10.15, 'color': 'green'},
        {'name': '20m', 'f_low': 14.00, 'f_high': 14.35, 'color': 'orange'},
        {'name': '17m', 'f_low': 18.07, 'f_high': 18.17, 'color': 'red'},
        {'name': '15m', 'f_low': 21.00, 'f_high': 21.45, 'color': 'purple'},
        {'name': '12m', 'f_low': 24.89, 'f_high': 24.99, 'color': 'brown'},
        {'name': '10m', 'f_low': 28.00, 'f_high': 29.70, 'color': 'magenta'}
    ]
    
    print("INDIVIDUAL 3RD-ORDER CHEBYSHEV BPF - NARROW HAM BANDS")
    print("=" * 70)
    
    results = []
    
    for i, band in enumerate(ham_bands, 1):
        print(f"\nBand {i}:")
        design = design_3rd_order_bpf(band['f_low'], band['f_high'], band['name'])
        design['color'] = band['color']
        
        # Check if fractional bandwidth is reasonable
        if design['fbw'] > 0.15:  # More than 15% FBW
            print(f"    ⚠️  FBW = {design['fbw']:.1%} is quite wide for 3rd-order!")
        elif design['fbw'] < 0.005:  # Less than 0.5% FBW
            print(f"    ⚠️  FBW = {design['fbw']:.1%} is very narrow - may be hard to build")
        else:
            print(f"    ✓ FBW = {design['fbw']:.1%} is reasonable for 3rd-order")
        
        # Create and run simulation
        filename = create_bpf_netlist(design, i)
        
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
                
                # Find peak and check if it's in the right place
                freqs = np.array(frequencies)
                gains_arr = np.array(gains)
                peak_idx = np.argmax(gains_arr)
                f_peak = freqs[peak_idx]
                g_peak = gains_arr[peak_idx]
                
                expected_f0 = design['f0_mhz']
                error = abs(f_peak - expected_f0)
                
                if error < 0.1:  # Within 100kHz
                    print(f"    ✓ Peak at {f_peak:.2f} MHz (expected {expected_f0:.2f} MHz)")
                else:
                    print(f"    ⚠️  Peak at {f_peak:.2f} MHz (expected {expected_f0:.2f} MHz, error {error:.2f} MHz)")
                
            else:
                print(f"    ✗ No simulation data")
                
        except subprocess.CalledProcessError:
            print(f"    ✗ Simulation failed")
    
    # Create combined plot
    if results:
        plt.figure(figsize=(16, 10))
        
        for design in results:
            plt.semilogx(design['frequencies'], design['gains'], 
                        color=design['color'], linewidth=2,
                        label=f"{design['band_name']}: {design['f_low_mhz']:.1f}-{design['f_high_mhz']:.1f} MHz")
            
            # Mark ham band region
            plt.axvspan(design['f_low_mhz'], design['f_high_mhz'], 
                       alpha=0.1, color=design['color'])
        
        plt.axhline(-3, color='gray', linestyle='--', alpha=0.7)
        plt.axhline(-20, color='gray', linestyle=':', alpha=0.7)
        plt.axhline(-60, color='gray', linestyle=':', alpha=0.7)
        
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Gain (dB)')
        plt.title('Individual 3rd-Order Chebyshev BPF - Each Ham Band')
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xlim(1, 32)
        plt.ylim(-80, 5)
        
        # X-axis every 5MHz
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 32])
        for freq in [5, 10, 15, 20, 25, 30]:
            plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('individual_ham_bands.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\n✓ Saved individual_ham_bands.png")
        
        # Summary
        print(f"\nSUMMARY - {len(results)} bands simulated successfully:")
        for design in results:
            fbw_status = "OK" if 0.005 <= design['fbw'] <= 0.15 else "⚠️"
            print(f"  {design['band_name']}: FBW = {design['fbw']:.1%} {fbw_status}")
        
        return True
    
    else:
        print("\n✗ No successful simulations")
        return False

if __name__ == '__main__':
    simulate_all_ham_bands()