#!/usr/bin/env python3
"""
Realistic 40m filter using proven component values
Start with known-good values and verify response
"""

import subprocess
import numpy as np
import matplotlib.pyplot as plt

def create_realistic_40m():
    """Use realistic component values for 40m band."""
    
    # Use component values that make physical sense
    # 40m band needs inductors in µH range, capacitors in 10s-100s pF
    
    netlist = """* Realistic 40m BPF - Known Good Values
* 3-pole bandpass for 7.0-7.3 MHz

.param L1=1.8u
.param L2=1.8u  
.param L3=1.8u
.param C1=390p
.param C2=390p
.param C3=390p
.param C_couple=68p

* === SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === 3-POLE COUPLED RESONATOR BPF ===
* Tank 1
L1 n1 n2 {L1}
C1 n2 0 {C1}

* Tank 2  
L2 n3 n4 {L2}
C2 n4 0 {C2}

* Tank 3
L3 n5 n6 {L3}
C3 n6 0 {C3}

* Coupling between tanks
C12 n2 n3 {C_couple}
C23 n4 n5 {C_couple}

* === LOAD ===
RL n6 0 50

* === ANALYSIS ===
.ac dec 100 1meg 100meg
.control
run
print frequency vdb(n6)
.endc
.end
"""
    
    with open('realistic_40m.cir', 'w') as f:
        f.write(netlist)
    
    try:
        result = subprocess.run(['ngspice', '-b', 'realistic_40m.cir'], 
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
            # Calculate resonant frequency
            freqs = np.array(frequencies)
            gains_arr = np.array(gains)
            peak_idx = np.argmax(gains_arr)
            f_peak = freqs[peak_idx]
            gain_peak = gains_arr[peak_idx]
            
            print(f"✓ Realistic 40m simulation successful")
            print(f"Peak: {gain_peak:.1f} dB at {f_peak:.2f} MHz")
            
            # Check theoretical resonant frequency
            L = 1.8e-6  # 1.8µH
            C = 390e-12  # 390pF
            f_theory = 1 / (2 * 3.14159 * (L * C)**0.5) / 1e6
            print(f"Theoretical f0: {f_theory:.2f} MHz")
            
            plt.figure(figsize=(12, 8))
            plt.semilogx(frequencies, gains, 'b-', linewidth=2, label=f'Realistic 40m (peak at {f_peak:.2f} MHz)')
            
            plt.axvspan(7.0, 7.3, alpha=0.2, color='cyan', label='40m Target Band')
            plt.axhline(-3, color='gray', linestyle='--', alpha=0.7)
            plt.axhline(-20, color='gray', linestyle=':', alpha=0.7)
            plt.axhline(-60, color='gray', linestyle=':', alpha=0.7)
            
            plt.xlabel('Frequency (MHz)')
            plt.ylabel('Gain (dB)')
            plt.title('Realistic 40m BPF - Should Show Bandpass Peak')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.xlim(1, 32)
            plt.ylim(-80, 10)
            
            plt.xticks([1, 5, 10, 15, 20, 25, 30, 32])
            for freq in [5, 10, 15, 20, 25, 30]:
                plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
            
            plt.tight_layout()
            plt.savefig('realistic_40m_response.png', dpi=150)
            plt.close()
            
            return True
        else:
            print("✗ No simulation data")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Simulation failed: {e}")
        return False

if __name__ == '__main__':
    print("REALISTIC 40m FILTER TEST")
    print("=" * 30)
    create_realistic_40m()