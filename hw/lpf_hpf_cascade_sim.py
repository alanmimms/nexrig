#!/usr/bin/env python3
"""
Create ngspice simulation files and plots for LPF+HPF cascade filters
"""

import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def create_ngspice_netlist(band_num, band_name, L1_pri_nH, L1_sec_nH, C1_lpf_pF, L2_lpf_nH, 
                          C1_hpf_pF, L1_hpf_sec_nH, L1_hpf_pri_nH, C2_hpf_pF):
    """Create ngspice netlist for LPF+HPF cascade."""
    
    netlist = f"""* LPF+HPF Cascade Filter - {band_name}
* 3rd-order LPF followed by 3rd-order HPF with integrated transformers

.param L1_pri={L1_pri_nH}n
.param L1_sec={L1_sec_nH}n  
.param C1_lpf={C1_lpf_pF}p
.param L2_lpf={L2_lpf_nH}n
.param C1_hpf={C1_hpf_pF}p
.param L1_hpf_sec={L1_hpf_sec_nH}n
.param L1_hpf_pri={L1_hpf_pri_nH}n
.param C2_hpf={C2_hpf_pF}p

* === INPUT STAGE ===
V1 in 0 AC 1 0
Rs in n1 50

* === INPUT TRANSFORMER (50Ω → 200Ω) ===
L_T1_pri n1 0 {{L1_pri}}
L_T1_sec n2 n3 {{L1_sec}}
K_T1 L_T1_pri L_T1_sec 0.98

* === LPF SECTION (3rd-order Chebyshev at 200Ω) ===
* L1 is the input transformer secondary
C_lpf1 n3 0 {{C1_lpf}}
L_lpf2 n3 n4 {{L2_lpf}}
C_lpf2 n4 0 {{C1_lpf}}
L_lpf3 n4 n5 {{L1_sec}}

* === HPF SECTION (3rd-order Chebyshev at 200Ω) ===
C_hpf1 n5 n6 {{C1_hpf}}
L_hpf1 n6 0 {{L1_hpf_sec}}
C_hpf2 n6 n7 {{C2_hpf}}
L_hpf2 n7 0 {{L1_hpf_sec}}
C_hpf3 n7 n8 {{C1_hpf}}

* === OUTPUT TRANSFORMER (200Ω → 50Ω) ===
L_T2_sec n8 0 {{L1_hpf_pri}}
L_T2_pri n7 0 {{L1_hpf_pri}}
K_T2 L_T2_sec L_T2_pri 0.98

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
    
    filename = f"lpf_hpf_band{band_num}.cir"
    with open(filename, 'w') as f:
        f.write(netlist)
    
    return filename

def run_simulation_and_plot():
    """Create simulations for all 4 bands and generate combined plot."""
    
    # Band parameters from the calculation
    bands = [
        {
            'num': 1, 'name': 'HF-Low (1.8-4.6 MHz)',
            'L1_pri_nH': 1633.2, 'L1_sec_nH': 6533.0, 'C1_lpf_pF': 243.3, 'L2_lpf_nH': 6533.0,
            'C1_hpf_pF': 468.3, 'L1_hpf_sec_nH': 24872.4, 'L1_hpf_pri_nH': 6218.1, 'C2_hpf_pF': 468.3,
            'f_low': 1.8, 'f_high': 4.6, 'color': 'blue'
        },
        {
            'num': 2, 'name': 'HF-Mid (4.4-10.1 MHz)', 
            'L1_pri_nH': 743.9, 'L1_sec_nH': 2975.4, 'C1_lpf_pF': 110.8, 'L2_lpf_nH': 2975.4,
            'C1_hpf_pF': 191.6, 'L1_hpf_sec_nH': 10175.1, 'L1_hpf_pri_nH': 2543.8, 'C2_hpf_pF': 191.6,
            'f_low': 4.4, 'f_high': 10.1, 'color': 'red'
        },
        {
            'num': 3, 'name': 'HF-High (9.9-18.1 MHz)',
            'L1_pri_nH': 415.1, 'L1_sec_nH': 1660.3, 'C1_lpf_pF': 61.8, 'L2_lpf_nH': 1660.3,
            'C1_hpf_pF': 85.1, 'L1_hpf_sec_nH': 4522.3, 'L1_hpf_pri_nH': 1130.6, 'C2_hpf_pF': 85.1,
            'f_low': 9.9, 'f_high': 18.1, 'color': 'green'
        },
        {
            'num': 4, 'name': 'HF-VHF (17.9-30.0 MHz)',
            'L1_pri_nH': 250.4, 'L1_sec_nH': 1001.7, 'C1_lpf_pF': 37.3, 'L2_lpf_nH': 1001.7,
            'C1_hpf_pF': 47.1, 'L1_hpf_sec_nH': 2501.1, 'L1_hpf_pri_nH': 625.3, 'C2_hpf_pF': 47.1,
            'f_low': 17.9, 'f_high': 30.0, 'color': 'orange'
        }
    ]
    
    # Create simulation files and run
    results = []
    
    for band in bands:
        print(f"Creating simulation for {band['name']}...")
        
        # Create netlist
        filename = create_ngspice_netlist(
            band['num'], band['name'],
            band['L1_pri_nH'], band['L1_sec_nH'], band['C1_lpf_pF'], band['L2_lpf_nH'],
            band['C1_hpf_pF'], band['L1_hpf_sec_nH'], band['L1_hpf_pri_nH'], band['C2_hpf_pF']
        )
        
        # Run ngspice
        try:
            result = subprocess.run(['ngspice', '-b', filename], 
                                  capture_output=True, text=True, check=True)
            
            lines = result.stdout.split('\n')
            
            # Parse output
            frequencies = []
            gains = []
            
            # Look for the data section - find lines with tab-separated numeric data
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                # Skip headers, empty lines, and text lines
                if not line or line.startswith('*') or line.startswith('Note:') or line.startswith('Circuit:') or line.startswith('Doing') or line.startswith('No. of') or line.startswith('Index') or '---' in line or line.startswith('Using') or 'analysis' in line.lower():
                    continue
                
                # Try to parse numeric data (tab or space separated)
                try:
                    parts = line.replace('\t', ' ').split()  # Handle tabs and spaces
                    if len(parts) >= 3:  # Index, frequency, vdb
                        idx = int(parts[0])  # Index
                        freq = float(parts[1])  # Frequency in Hz
                        gain = float(parts[2])  # Gain in dB
                        
                        # Convert frequency to MHz
                        freq_mhz = freq / 1e6
                        
                        frequencies.append(freq_mhz)
                        gains.append(gain)
                        
                except (ValueError, IndexError):
                    # Skip lines that don't parse as numeric data
                    continue
            
            if frequencies:
                band['frequencies'] = np.array(frequencies)
                band['gains'] = np.array(gains)
                results.append(band)
                print(f"✓ Band {band['num']}: {len(frequencies)} points")
            else:
                print(f"✗ Band {band['num']}: No data points")
                
        except subprocess.CalledProcessError as e:
            print(f"✗ Band {band['num']}: Simulation failed")
            print(f"Error: {e.stderr}")
    
    # Create combined plot
    if results:
        plt.figure(figsize=(14, 10))
        
        # Main plot
        plt.subplot(2, 1, 1)
        for band in results:
            plt.semilogx(band['frequencies'], band['gains'], 
                        color=band['color'], linewidth=2, 
                        label=f"Band {band['num']}: {band['name']}")
            
            # Mark passband
            plt.axvspan(band['f_low'], band['f_high'], 
                       alpha=0.1, color=band['color'])
        
        plt.axhline(-3, color='gray', linestyle='--', alpha=0.7, label='-3dB')
        plt.axhline(-20, color='gray', linestyle=':', alpha=0.7, label='-20dB')
        plt.axhline(-60, color='gray', linestyle=':', alpha=0.7, label='-60dB')
        
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Gain (dB)')
        plt.title('LPF+HPF Cascade Filters - 4 Wide Bands with 200kHz Overlap')
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xlim(1, 50)
        plt.ylim(-80, 5)
        
        # Set X-axis ticks every 5MHz
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
        
        # Detail plot - passband region
        plt.subplot(2, 1, 2)
        for band in results:
            # Focus on passband ±20%
            f_center = np.sqrt(band['f_low'] * band['f_high'])
            f_span = band['f_high'] - band['f_low']
            f_min = max(0.8 * band['f_low'], 1.0)
            f_max = min(1.2 * band['f_high'], 50.0)
            
            mask = (band['frequencies'] >= f_min) & (band['frequencies'] <= f_max)
            if np.any(mask):
                plt.semilogx(band['frequencies'][mask], band['gains'][mask], 
                            color=band['color'], linewidth=2,
                            label=f"Band {band['num']}")
                
                # Mark target passband
                plt.axvspan(band['f_low'], band['f_high'], 
                           alpha=0.2, color=band['color'])
        
        plt.axhline(-3, color='gray', linestyle='--', alpha=0.7)
        plt.axhline(-0.1, color='red', linestyle=':', alpha=0.7, label='0.1dB Ripple')
        
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Gain (dB)')
        plt.title('Passband Detail - Chebyshev Response Verification')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xlim(1, 35)
        plt.ylim(-5, 1)
        
        plt.tight_layout()
        plt.savefig('lpf_hpf_cascade_response.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✓ Saved lpf_hpf_cascade_response.png")
        return True
    
    else:
        print("✗ No successful simulations")
        return False

if __name__ == '__main__':
    print("LPF+HPF CASCADE SIMULATION")
    print("=" * 50)
    success = run_simulation_and_plot()
    if success:
        print("\n✓ All simulations completed successfully")
    else:
        print("\n✗ Some simulations failed")