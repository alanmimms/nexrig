#!/usr/bin/env python3
"""
Fine-tuned 3rd-order Chebyshev BPF - keep what works, fix frequency centering only
"""

import math
import numpy as np
import subprocess
import matplotlib.pyplot as plt

def design_fine_tuned_bpf(f_low_mhz, f_high_mhz, band_name):
    """Fine-tune the original working design with better frequency control."""
    
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    f0 = math.sqrt(f_low * f_high)  # Keep geometric center - it was working
    bw = f_high - f_low
    fbw = bw / f0
    
    print(f"  {band_name}: {f_low_mhz:.2f}-{f_high_mhz:.2f} MHz")
    print(f"    f0 = {f0/1e6:.2f} MHz, BW = {bw/1e3:.0f} kHz, FBW = {fbw:.1%}")
    
    # Use original 0.1dB ripple g-values that were working
    g1 = 0.9441
    g2 = 1.4065
    g3 = 0.9441
    
    # Apply frequency correction factors based on what we observed:
    # 20m was ~0.3 MHz low, 10m was ~0.3 MHz low  
    if band_name == '20m':
        freq_correction = 1.02  # Small upward correction for 20m
    elif band_name == '10m':  
        freq_correction = 1.01  # Small upward correction for 10m
    else:
        freq_correction = 1.0   # 40m was good as-is
    
    Z0 = 50
    omega0 = 2 * math.pi * f0 * freq_correction
    
    # Same calculation as before but with frequency correction
    L1 = g1 * Z0 / (omega0 * fbw)
    C1 = fbw / (g1 * omega0 * Z0)
    
    L3 = g3 * Z0 / (omega0 * fbw)
    C3 = fbw / (g3 * omega0 * Z0)
    
    C2 = g2 / (omega0 * fbw * Z0)
    L2 = fbw * Z0 / (g2 * omega0)
    
    # Convert to practical units
    L1_uH = L1 * 1e6
    C1_pF = C1 * 1e12
    L2_uH = L2 * 1e6
    C2_pF = C2 * 1e12
    L3_uH = L3 * 1e6
    C3_pF = C3 * 1e12
    
    print(f"    Freq correction: {freq_correction:.2f}")
    print(f"    Series L1={L1_uH:.2f}µH, C1={C1_pF:.0f}pF")
    print(f"    Shunt  L2={L2_uH:.3f}µH, C2={C2_pF:.0f}pF")
    print(f"    Series L3={L3_uH:.2f}µH, C3={C3_pF:.0f}pF")
    
    return {
        'band_name': band_name,
        'f_low_mhz': f_low_mhz,
        'f_high_mhz': f_high_mhz,
        'f0_mhz': f0 / 1e6,
        'fbw': fbw,
        'freq_correction': freq_correction,
        'L1_uH': L1_uH,
        'C1_pF': C1_pF,
        'L2_uH': L2_uH,
        'C2_pF': C2_pF,
        'L3_uH': L3_uH,
        'C3_pF': C3_pF
    }

def create_fine_tuned_netlist(design, band_num):
    """Create netlist with fine-tuned component values."""
    
    netlist = f"""* Fine-Tuned 3rd-Order Chebyshev BPF - {design['band_name']}
* Original topology with frequency correction
* Target: {design['f_low_mhz']:.2f}-{design['f_high_mhz']:.2f} MHz

.param f0={design['f0_mhz']:.3f}meg
.param fbw={design['fbw']:.4f}
.param correction={design['freq_correction']:.3f}

* Fine-tuned component values
.param L1={design['L1_uH']:.3f}u
.param C1={design['C1_pF']:.1f}p
.param L2={design['L2_uH']:.4f}u
.param C2={design['C2_pF']:.1f}p
.param L3={design['L3_uH']:.3f}u
.param C3={design['C3_pF']:.1f}p

* === SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === FINE-TUNED CHEBYSHEV BPF ===
* Series branch 1
L1 n1 n2 {{L1}}
C1 n2 n3 {{C1}}

* Shunt branch
L2 n3 0 {{L2}}
C2 n3 0 {{C2}}

* Series branch 3
L3 n3 n4 {{L3}}
C3 n4 n5 {{C3}}

* === LOAD ===
RL n5 0 50

* === ANALYSIS ===
.ac dec 1000 100k 100meg
.control
run
print frequency vdb(n5)
.endc
.end
"""
    
    filename = f'fine_tuned_{band_num}_{design["band_name"]}.cir'
    with open(filename, 'w') as f:
        f.write(netlist)
    
    return filename

def test_fine_tuned_filters():
    """Test fine-tuned filters with minimal changes."""
    
    test_bands = [
        {'name': '40m', 'f_low': 7.00, 'f_high': 7.30, 'color': 'blue'},
        {'name': '20m', 'f_low': 14.00, 'f_high': 14.35, 'color': 'red'},
        {'name': '10m', 'f_low': 28.00, 'f_high': 29.70, 'color': 'green'}
    ]
    
    print("FINE-TUNED 3RD-ORDER CHEBYSHEV BPF")
    print("=" * 50)
    print("Keeping working topology, adjusting frequency centering only")
    print()
    
    results = []
    
    for i, band in enumerate(test_bands, 1):
        print(f"Band {i}:")
        design = design_fine_tuned_bpf(band['f_low'], band['f_high'], band['name'])
        design['color'] = band['color']
        
        filename = create_fine_tuned_netlist(design, i)
        
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
                
                # Analyze response
                freqs = np.array(frequencies)
                gains_arr = np.array(gains)
                
                # Check band coverage
                band_mask = (freqs >= design['f_low_mhz']) & (freqs <= design['f_high_mhz'])
                if np.any(band_mask):
                    band_gains = gains_arr[band_mask]
                    max_gain = np.max(band_gains)
                    min_gain = np.min(band_gains)
                    ripple = max_gain - min_gain
                    
                    # Find peak
                    peak_idx = np.argmax(gains_arr)
                    peak_freq = freqs[peak_idx]
                    target_center = math.sqrt(design['f_low_mhz'] * design['f_high_mhz'])
                    freq_error = abs(peak_freq - target_center)
                    
                    print(f"    Peak at {peak_freq:.2f} MHz (target: {target_center:.2f} MHz)")
                    print(f"    Frequency error: {freq_error:.2f} MHz")
                    print(f"    Passband: {min_gain:.2f} to {max_gain:.2f} dB")
                    print(f"    Ripple: {ripple:.2f} dB")
                    
                    if freq_error < 0.15:
                        print(f"    ✓ Good frequency centering")
                    else:
                        print(f"    ⚠️  Needs more frequency adjustment")
                        
                    if ripple < 1.0:
                        print(f"    ✓ Acceptable ripple")
                    else:
                        print(f"    ⚠️  High ripple")
                
            else:
                print(f"    ✗ No simulation data")
                
        except subprocess.CalledProcessError as e:
            print(f"    ✗ Simulation failed: {e}")
        
        print()
    
    # Create plots
    if results:
        for design in results:
            plt.figure(figsize=(12, 8))
            
            plt.semilogx(design['frequencies'], design['gains'], 
                        color=design['color'], linewidth=2,
                        label=f"{design['band_name']} BPF (Fine-Tuned)")
            
            plt.axvspan(design['f_low_mhz'], design['f_high_mhz'], 
                       alpha=0.2, color=design['color'], 
                       label=f"Target: {design['f_low_mhz']:.2f}-{design['f_high_mhz']:.2f} MHz")
            
            plt.axhline(-3, color='gray', linestyle='--', alpha=0.7, label='-3dB')
            plt.axhline(-20, color='gray', linestyle=':', alpha=0.5, label='-20dB')
            plt.axhline(-60, color='gray', linestyle=':', alpha=0.5, label='-60dB')
            
            # Set axis limits
            f_center = math.sqrt(design['f_low_mhz'] * design['f_high_mhz'])
            f_span = design['f_high_mhz'] - design['f_low_mhz']
            f_min = max(0.5, f_center - 5 * f_span)
            f_max = f_center + 5 * f_span
            
            plt.xlim(f_min, f_max)
            plt.ylim(-80, 5)
            
            # Ticks
            if f_max <= 5:
                tick_step = 0.5
            elif f_max <= 15:
                tick_step = 1
            elif f_max <= 35:
                tick_step = 2
            else:
                tick_step = 5
                
            ticks = np.arange(int(f_min), int(f_max) + 1, tick_step)
            plt.xticks(ticks)
            
            for tick in ticks:
                if tick >= f_min and tick <= f_max:
                    plt.axvline(tick, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
            
            plt.xlabel('Frequency (MHz)')
            plt.ylabel('Gain (dB)')
            plt.title(f'Fine-Tuned 3rd-Order Chebyshev BPF - {design["band_name"]} Band\n' + 
                     f'Frequency Correction: {design["freq_correction"]:.2f}')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plt.tight_layout()
            filename = f'fine_tuned_{design["band_name"]}_detailed.png'
            plt.savefig(filename, dpi=150)
            plt.close()
            
            print(f"✓ Saved {filename}")
        
        return True
    
    return False

if __name__ == '__main__':
    test_fine_tuned_filters()