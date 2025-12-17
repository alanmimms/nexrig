#!/usr/bin/env python3
"""
Simulate and Plot All BPF Bands
================================

Runs ngspice simulations and uses matplotlib to create PNG plots.
"""

import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Band definitions with amateur radio band names
bands = [
    {'num': 1, 'name': '160m', 'low': 1.8,  'high': 2.0},
    {'num': 2, 'name': '80m',  'low': 3.25, 'high': 4.0},
    {'num': 3, 'name': '40m',  'low': 4.5,  'high': 7.4},
    {'num': 4, 'name': '30m',  'low': 9.9,  'high': 10.5},
    {'num': 5, 'name': '20m',  'low': 13.5, 'high': 18.5},
    {'num': 6, 'name': '17m',  'low': 19.5, 'high': 25.1},
    {'num': 7, 'name': '10m',  'low': 28.0, 'high': 32.0},
]

def run_simulation(band):
    """Run ngspice simulation for a band and generate data file."""
    
    band_num = band['num']
    band_name = band['name']
    
    # Create netlist for this band
    with open('bpf-simulation-simple.cir', 'r') as f:
        template = f.read()
    
    netlist = template.replace('BAND_NAME', band_name)
    netlist = netlist.replace('BAND_FILE', f'band{band_num}.mod')
    netlist = netlist.replace('OUTPUT_FILE', f'band{band_num}_data.txt')
    
    netlist_file = f'band{band_num}_sim.cir'
    with open(netlist_file, 'w') as f:
        f.write(netlist)
    
    # Run ngspice
    print(f"Simulating Band {band_num} ({band_name})...")
    result = subprocess.run(
        ['ngspice', '-b', netlist_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:200]}")
        return False
    
    return True

def plot_response(band):
    """Plot frequency response from simulation data."""
    
    band_num = band['num']
    band_name = band['name']
    data_file = f'band{band_num}_data.txt'
    
    if not os.path.exists(data_file):
        print(f"  No data file for Band {band_num}")
        return False
    
    # Read the data - handle ngspice's multi-column format
    try:
        data = []
        with open(data_file, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # Skip header
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    freq_val = float(parts[0])  # First column is frequency
                    gain_val = float(parts[3])  # Fourth column is gain in dB
                    data.append([freq_val, gain_val])
        
        if not data:
            print(f"  No valid data in {data_file}")
            return False
            
        data = np.array(data)
        freq = data[:, 0] / 1e6  # Convert to MHz
        gain = data[:, 1]  # Already in dB
    except Exception as e:
        print(f"  Error reading data: {e}")
        return False
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the frequency response
    ax.plot(freq, gain, 'b-', linewidth=2, label=f'Band {band_num} ({band_name})')
    
    # Mark the target passband
    ax.axvline(band['low'], color='r', linestyle='--', alpha=0.5, label='Target band')
    ax.axvline(band['high'], color='r', linestyle='--', alpha=0.5)
    
    # Add a shaded region for the target band
    ax.axvspan(band['low'], band['high'], alpha=0.1, color='green')
    
    # Find and mark -3dB points
    try:
        max_gain = np.max(gain)
        cutoff_level = max_gain - 3
        
        # Find -3dB frequencies
        idx_above = np.where(gain > cutoff_level)[0]
        if len(idx_above) > 0:
            f_low_3db = freq[idx_above[0]]
            f_high_3db = freq[idx_above[-1]]
            
            ax.axhline(cutoff_level, color='g', linestyle=':', alpha=0.5, label='-3dB level')
            ax.axvline(f_low_3db, color='g', linestyle=':', alpha=0.5)
            ax.axvline(f_high_3db, color='g', linestyle=':', alpha=0.5)
            
            # Add text annotations
            ax.text(f_low_3db, cutoff_level-2, f'{f_low_3db:.1f} MHz', 
                   rotation=90, ha='right', va='top', fontsize=8)
            ax.text(f_high_3db, cutoff_level-2, f'{f_high_3db:.1f} MHz', 
                   rotation=90, ha='left', va='top', fontsize=8)
    except:
        pass
    
    # Set axis properties
    ax.set_xlabel('Frequency (MHz)', fontsize=12)
    ax.set_ylabel('Gain (dB)', fontsize=12)
    ax.set_title(f'Band {band_num} ({band_name}): {band["low"]}-{band["high"]} MHz BPF Response', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    # Set frequency range to show a bit beyond the band
    center = (band['low'] + band['high']) / 2
    span = (band['high'] - band['low']) * 2
    ax.set_xlim(max(0.5, center - span), min(50, center + span))
    ax.set_ylim(-60, 10)
    
    # Save the plot
    output_file = f'band{band_num}_response.png'
    try:
        plt.tight_layout()
    except:
        pass  # Ignore tight_layout warnings
    plt.savefig(output_file, dpi=100)
    plt.close()
    
    print(f"  ✓ Saved {output_file}")
    return True

def create_combined_plot():
    """Create a single plot showing all bands."""
    
    fig, axes = plt.subplots(4, 2, figsize=(14, 16))
    axes = axes.flatten()
    
    for i, band in enumerate(bands):
        ax = axes[i]
        band_num = band['num']
        band_name = band['name']
        data_file = f'band{band_num}_data.txt'
        
        if os.path.exists(data_file):
            try:
                data = []
                with open(data_file, 'r') as f:
                    for i, line in enumerate(f):
                        if i == 0:
                            continue
                        parts = line.split()
                        if len(parts) >= 4:
                            data.append([float(parts[0]), float(parts[3])])
                
                if data:
                    data = np.array(data)
                    freq = data[:, 0] / 1e6
                    gain = data[:, 1]
                    
                    ax.plot(freq, gain, 'b-', linewidth=1.5)
                ax.axvline(band['low'], color='r', linestyle='--', alpha=0.5)
                ax.axvline(band['high'], color='r', linestyle='--', alpha=0.5)
                ax.axvspan(band['low'], band['high'], alpha=0.1, color='green')
                
                ax.set_xlabel('Frequency (MHz)')
                ax.set_ylabel('Gain (dB)')
                ax.set_title(f'Band {band_num} ({band_name}): {band["low"]}-{band["high"]} MHz')
                ax.grid(True, alpha=0.3)
                
                # Set appropriate x-axis limits
                center = (band['low'] + band['high']) / 2
                span = (band['high'] - band['low']) * 3
                ax.set_xlim(max(0.5, center - span), center + span)
                ax.set_ylim(-60, 10)
            except:
                ax.text(0.5, 0.5, f'Band {band_num}: No data', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f'Band {band_num} ({band_name})')
        else:
            ax.text(0.5, 0.5, f'Band {band_num}: No data', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'Band {band_num} ({band_name})')
    
    # Hide the 8th subplot (we only have 7 bands)
    axes[7].axis('off')
    
    plt.suptitle('All Band BPF Frequency Responses', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig('all_bands_response.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("\n✓ Created all_bands_response.png")

def main():
    """Main function."""
    
    print("BPF SIMULATION AND PLOTTING")
    print("=" * 60)
    
    # Check dependencies
    try:
        import matplotlib
        import numpy
    except ImportError:
        print("ERROR: matplotlib or numpy not installed")
        print("Run: pip install matplotlib numpy")
        return
    
    # Check for band files
    missing = []
    for band in bands:
        if not os.path.exists(f'band{band["num"]}.mod'):
            missing.append(f'band{band["num"]}.mod')
    
    if missing:
        print(f"ERROR: Missing files: {', '.join(missing)}")
        return
    
    # Simulate and plot each band
    successful = []
    for band in bands:
        if run_simulation(band):
            if plot_response(band):
                successful.append(band['num'])
    
    # Create combined plot
    if successful:
        create_combined_plot()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Successfully plotted: {len(successful)}/{len(bands)} bands")
    print("\nGenerated files:")
    print("  - band[1-7]_response.png - Individual band plots")
    print("  - all_bands_response.png - Combined plot of all bands")
    print("  - band[1-7]_data.txt - Simulation data files")

if __name__ == '__main__':
    main()