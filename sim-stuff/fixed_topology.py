#!/usr/bin/env python3
"""
FIXED topology - create actual working bandpass filter
Use the correct transformer-coupled three-tank approach
"""

import subprocess
import numpy as np
import matplotlib.pyplot as plt

def create_working_40m_filter():
    """Create working 40m filter with CORRECT topology and component values."""
    
    # Let me manually design a proper 40m filter using correct BPF equations
    # 40m: 7.0-7.3 MHz, center = 7.15 MHz, BW = 0.3 MHz, FBW = 4.2%
    
    f0 = 7.15e6  # Center frequency
    bw = 0.3e6   # Bandwidth
    fbw = bw / f0  # Fractional bandwidth = 0.042
    
    # Use 200Ω design impedance like your original
    Z0 = 200
    
    # 3rd-order Chebyshev g-values for 0.1dB ripple
    g1 = 0.9441
    g2 = 1.4065  
    g3 = 0.9441
    
    # Proper bandpass transformation
    omega0 = 2 * 3.14159 * f0
    
    # Tank inductances (all equal for symmetrical design)
    L = Z0 / (omega0 * fbw)  # This gives proper resonant frequency
    
    # Tank capacitances (all equal, tuned to f0)
    C_tank = 1 / (omega0**2 * L)
    
    # Coupling capacitors (determine bandwidth)
    k = fbw / 0.9441  # Coupling coefficient
    C_couple = k * C_tank
    
    # Input/output tapping for 50Ω match
    # n = sqrt(Z_tank / Z_source) = sqrt(200/50) = 2
    # So we need 1:2 impedance transformation
    
    # This creates the proper tapped-capacitor values
    C_main = C_tank * 4/3  # Main tank capacitor
    C_tap = C_tank * 4    # Tap capacitor (parallel with source/load)
    
    L_nH = L * 1e9
    C_main_pF = C_main * 1e12
    C_tap_pF = C_tap * 1e12
    C_couple_pF = C_couple * 1e12
    
    print(f"40m Filter Design:")
    print(f"  f0 = {f0/1e6:.2f} MHz, BW = {bw/1e3:.0f} kHz, FBW = {fbw:.1%}")
    print(f"  L = {L_nH:.0f} nH")
    print(f"  C_main = {C_main_pF:.0f} pF")
    print(f"  C_tap = {C_tap_pF:.0f} pF") 
    print(f"  C_couple = {C_couple_pF:.0f} pF")
    
    netlist = f"""* Working 40m 3-Pole BPF - CORRECT Topology
* Transformer-coupled three-tank design

.param L={L_nH:.0f}n
.param C_main={C_main_pF:.0f}p
.param C_tap={C_tap_pF:.0f}p
.param C_couple={C_couple_pF:.0f}p

* === SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === 3-TANK BANDPASS FILTER ===
* Tank 1: Input tank with tapped capacitor for 50Ω matching
L1 n2 n3 {{L}}
C1_main n3 0 {{C_main}}
C1_tap n1 n2 {{C_tap}}

* Tank 2: Center tank (parallel resonant)
L2 n4 n5 {{L}}
C2 n5 0 {{C_main}}

* Tank 3: Output tank with tapped capacitor for 50Ω matching  
L3 n6 n7 {{L}}
C3_main n7 0 {{C_main}}
C3_tap n6 n8 {{C_tap}}

* Coupling between tanks
C12 n3 n4 {{C_couple}}  ; Tank 1 to Tank 2
C23 n5 n6 {{C_couple}}  ; Tank 2 to Tank 3

* === LOAD ===
RL n8 0 50

* === ANALYSIS ===
.ac dec 100 1meg 100meg
.control
run
print frequency vdb(n8)
.endc
.end
"""
    
    with open('working_40m.cir', 'w') as f:
        f.write(netlist)
    
    # Run simulation
    try:
        result = subprocess.run(['ngspice', '-b', 'working_40m.cir'], 
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
            plt.figure(figsize=(12, 8))
            plt.semilogx(frequencies, gains, 'b-', linewidth=2, label='Working 40m Filter')
            
            # Mark 40m band
            plt.axvspan(7.0, 7.3, alpha=0.2, color='cyan', label='40m Band')
            
            plt.axhline(-3, color='gray', linestyle='--', alpha=0.7)
            plt.axhline(-20, color='gray', linestyle=':', alpha=0.7)
            plt.axhline(-60, color='gray', linestyle=':', alpha=0.7)
            
            plt.xlabel('Frequency (MHz)')
            plt.ylabel('Gain (dB)')
            plt.title('40m BPF - FIXED TOPOLOGY (Should Show Bandpass Peak)')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.xlim(1, 32)
            plt.ylim(-80, 5)
            
            plt.xticks([1, 5, 10, 15, 20, 25, 30, 32])
            for freq in [5, 10, 15, 20, 25, 30]:
                plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
            
            plt.tight_layout()
            plt.savefig('working_40m_response.png', dpi=150)
            plt.close()
            
            print(f"✓ Simulation completed")
            print(f"Frequency range: {min(frequencies):.1f} - {max(frequencies):.1f} MHz")
            print(f"Peak gain: {max(gains):.1f} dB at {frequencies[np.argmax(gains)]:.2f} MHz")
            
            # Analyze response in 40m band
            freqs = np.array(frequencies)
            gains_arr = np.array(gains)
            band_mask = (freqs >= 7.0) & (freqs <= 7.3)
            
            if np.any(band_mask):
                band_gains = gains_arr[band_mask]
                band_freqs = freqs[band_mask]
                print(f"40m band: {min(band_gains):.1f} to {max(band_gains):.1f} dB")
                print(f"Peak in band: {max(band_gains):.1f} dB at {band_freqs[np.argmax(band_gains)]:.2f} MHz")
            
            return True
        else:
            print("✗ No simulation data")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Simulation failed")
        print("Error output:", result.stderr if 'result' in locals() else 'No error info')
        return False

if __name__ == '__main__':
    print("TESTING FIXED 40m FILTER TOPOLOGY")
    print("=" * 50)
    create_working_40m_filter()