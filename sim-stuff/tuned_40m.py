#!/usr/bin/env python3
"""
Tune component values to get 40m peak at correct frequency
"""

import subprocess
import numpy as np
import matplotlib.pyplot as plt

def test_40m_values(L_uH, C_pF, C_couple_pF, test_name):
    """Test specific component values for 40m."""
    
    netlist = f"""* Tuned 40m BPF - {test_name}
* Target: 7.0-7.3 MHz

.param L1={L_uH}u
.param L2={L_uH}u  
.param L3={L_uH}u
.param C1={C_pF}p
.param C2={C_pF}p
.param C3={C_pF}p
.param C_couple={C_couple_pF}p

V1 in 0 AC 1 0
Rs in n1 50

L1 n1 n2 {{L1}}
C1 n2 0 {{C1}}

L2 n3 n4 {{L2}}
C2 n4 0 {{C2}}

L3 n5 n6 {{L3}}
C3 n6 0 {{C3}}

C12 n2 n3 {{C_couple}}
C23 n4 n5 {{C_couple}}

RL n6 0 50

.ac dec 100 1meg 100meg
.control
run
print frequency vdb(n6)
.endc
.end
"""
    
    filename = f'tuned_40m_{test_name.replace(" ", "_")}.cir'
    with open(filename, 'w') as f:
        f.write(netlist)
    
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
            freqs = np.array(frequencies)
            gains_arr = np.array(gains)
            peak_idx = np.argmax(gains_arr)
            f_peak = freqs[peak_idx]
            gain_peak = gains_arr[peak_idx]
            
            # Calculate theoretical f0
            L = L_uH * 1e-6
            C = C_pF * 1e-12
            f_theory = 1 / (2 * 3.14159 * (L * C)**0.5) / 1e6
            
            print(f"{test_name}:")
            print(f"  L={L_uH}µH, C={C_pF}pF, Ccoup={C_couple_pF}pF")
            print(f"  Theoretical f0: {f_theory:.2f} MHz")
            print(f"  Actual peak: {gain_peak:.1f} dB at {f_peak:.2f} MHz")
            print(f"  Target: 7.0-7.3 MHz")
            print()
            
            return frequencies, gains, f_peak, gain_peak
        else:
            print(f"{test_name}: No simulation data")
            return None, None, 0, 0
            
    except subprocess.CalledProcessError:
        print(f"{test_name}: Simulation failed")
        return None, None, 0, 0

def find_correct_40m_values():
    """Try different component combinations to hit 7.15 MHz."""
    
    print("TUNING 40m FILTER COMPONENTS")
    print("=" * 40)
    print("Target: Peak around 7.15 MHz")
    print()
    
    # Try different L/C combinations that give f0 around 7.15 MHz
    # f = 1/(2π√LC), so for 7.15 MHz: LC ≈ 4.9e-15
    
    test_cases = [
        # L(µH), C(pF), C_couple(pF), name
        (3.3, 150, 22, "Test 1"),   # LC = 4.95e-15
        (2.7, 180, 27, "Test 2"),   # LC = 4.86e-15  
        (2.2, 220, 33, "Test 3"),   # LC = 4.84e-15
        (4.7, 100, 15, "Test 4"),   # LC = 4.7e-15
        (5.6, 82,  12, "Test 5"),   # LC = 4.59e-15
    ]
    
    results = []
    for L, C, Cc, name in test_cases:
        freq, gain, f_peak, g_peak = test_40m_values(L, C, Cc, name)
        if freq is not None:
            results.append((freq, gain, f_peak, g_peak, name, L, C, Cc))
    
    if results:
        # Plot all results
        plt.figure(figsize=(14, 10))
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, (freq, gain, f_peak, g_peak, name, L, C, Cc) in enumerate(results):
            plt.semilogx(freq, gain, color=colors[i % len(colors)], linewidth=2,
                        label=f'{name}: L={L}µH C={C}pF (peak at {f_peak:.2f}MHz)')
        
        # Mark 40m target band
        plt.axvspan(7.0, 7.3, alpha=0.2, color='cyan', label='40m Target')
        plt.axhline(-3, color='gray', linestyle='--', alpha=0.7)
        plt.axhline(-20, color='gray', linestyle=':', alpha=0.7)
        
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Gain (dB)')
        plt.title('40m BPF Component Tuning - Finding Correct Values')
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xlim(1, 32)
        plt.ylim(-80, 10)
        
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 32])
        for freq in [5, 10, 15, 20, 25, 30]:
            plt.axvline(freq, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('40m_tuning_results.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✓ Saved 40m_tuning_results.png")
        
        # Find best result (closest to 7.15 MHz)
        target = 7.15
        errors = [abs(f_peak - target) for _, _, f_peak, _, _, _, _, _ in results]
        best_idx = np.argmin(errors)
        best = results[best_idx]
        
        print(f"BEST RESULT: {best[4]}")
        print(f"  Components: L={best[5]}µH, C={best[6]}pF, C_couple={best[7]}pF")  
        print(f"  Peak: {best[3]:.1f} dB at {best[2]:.2f} MHz (error: {errors[best_idx]:.2f} MHz)")
        
        return best[5], best[6], best[7]  # Return L, C, C_couple
    
    else:
        print("✗ No successful simulations")
        return None, None, None

if __name__ == '__main__':
    find_correct_40m_values()