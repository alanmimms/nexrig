#!/usr/bin/env python3
"""
Debug single band filter to see what's going wrong
Test with 40m band first since it has reasonable FBW
"""

import subprocess
import numpy as np
import matplotlib.pyplot as plt

def create_simple_40m_filter():
    """Create a simple 40m filter to debug the topology."""
    
    # Use the EXACT working values from your original design
    # 40m band: 7.0-7.3 MHz
    
    netlist = """* Simple 40m 3-Pole BPF Debug
* Using transformer-coupled hybrid topology

* Component values (from working design)
.param L1=100n
.param L2=133n  
.param L3=100n
.param C1a=4p
.param C1b=1p
.param C2=2425p
.param C3a=4p
.param C3b=1p

* === SOURCE ===
V1 in 0 AC 1 0
Rs in n1 50

* === HYBRID TAPPED-CAPACITOR TOPOLOGY ===
* Tank 1: Tapped capacitor for input matching
L1 n1 n2 {L1}
C1a n2 0 {C1a}
C1b n1 0 {C1b}

* Tank 2: Standard parallel tank
L2 n2 n3 {L2}
C2 n3 0 {C2}

* Tank 3: Tapped capacitor for output matching
L3 n3 n4 {L3}  
C3a n4 0 {C3a}
C3b n3 0 {C3b}

* === LOAD ===
RL n4 0 50

* === ANALYSIS ===
.ac dec 100 1meg 100meg
.control
run
print frequency vdb(n4)
.endc
.end
"""
    
    with open('debug_40m.cir', 'w') as f:
        f.write(netlist)
    
    # Run simulation
    try:
        result = subprocess.run(['ngspice', '-b', 'debug_40m.cir'], 
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
            plt.semilogx(frequencies, gains, 'b-', linewidth=2, label='40m Debug Filter')
            
            # Mark 40m band
            plt.axvspan(7.0, 7.3, alpha=0.2, color='cyan', label='40m Band')
            
            plt.axhline(-3, color='gray', linestyle='--', alpha=0.7)
            plt.axhline(-20, color='gray', linestyle=':', alpha=0.7)
            plt.axhline(-60, color='gray', linestyle=':', alpha=0.7)
            
            plt.xlabel('Frequency (MHz)')
            plt.ylabel('Gain (dB)')
            plt.title('40m BPF Debug - Should Show Clean Chebyshev Response')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.xlim(1, 32)
            plt.ylim(-80, 5)
            
            # X-axis ticks every 5MHz
            plt.xticks([1, 5, 10, 15, 20, 25, 30, 32])
            for freq in [5, 10, 15, 20, 25, 30]:
                plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
            
            plt.tight_layout()
            plt.savefig('debug_40m_response.png', dpi=150)
            plt.close()
            
            print("✓ Debug simulation completed")
            print(f"Frequency range: {min(frequencies):.1f} - {max(frequencies):.1f} MHz")
            print(f"Peak gain: {max(gains):.1f} dB")
            
            # Find response in 40m band
            band_mask = (np.array(frequencies) >= 7.0) & (np.array(frequencies) <= 7.3)
            if np.any(band_mask):
                band_gains = np.array(gains)[band_mask]
                print(f"40m band response: {min(band_gains):.1f} to {max(band_gains):.1f} dB")
            
            return True
        else:
            print("✗ No simulation data")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Simulation failed: {e}")
        print("STDOUT:", e.stdout if hasattr(e, 'stdout') else 'None')
        print("STDERR:", e.stderr if hasattr(e, 'stderr') else 'None')
        return False

if __name__ == '__main__':
    print("DEBUGGING 40m FILTER TOPOLOGY")
    print("=" * 40)
    create_simple_40m_filter()