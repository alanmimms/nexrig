#!/usr/bin/env python3
"""
Simulate All 7 BPF Bands with ngspice
=====================================

Generates individual netlists for each band and runs ngspice simulations.
Produces PNG frequency response plots for each band.
"""

import subprocess
import os
import sys

# Band definitions
bands = [
    {'num': 1, 'name': 'Band 1 (160m)', 'low': 1.8,  'high': 2.0},
    {'num': 2, 'name': 'Band 2 (80m)',  'low': 3.25, 'high': 4.0},
    {'num': 3, 'name': 'Band 3 (40m)',  'low': 4.5,  'high': 7.4},
    {'num': 4, 'name': 'Band 4 (30m)',  'low': 9.9,  'high': 10.5},
    {'num': 5, 'name': 'Band 5 (20m)',  'low': 13.5, 'high': 18.5},
    {'num': 6, 'name': 'Band 6 (17m)',  'low': 19.5, 'high': 25.1},
    {'num': 7, 'name': 'Band 7 (10m)',  'low': 28.0, 'high': 32.0},
]

def generate_netlist(band):
    """Generate a netlist for a specific band."""
    
    band_num = band['num']
    band_name = band['name']
    band_file = f'band{band_num}.mod'
    netlist_file = f'band{band_num}.cir'
    output_png = f'band{band_num}_response.png'
    output_csv = f'band{band_num}_data.csv'
    
    # Read the template
    with open('bpf-simulation-template.cir', 'r') as f:
        template = f.read()
    
    # Replace placeholders
    netlist = template.replace('BAND_NAME', band_name)
    netlist = netlist.replace('BAND_FILE', band_file)
    netlist = netlist.replace('OUTPUT_FILE', output_png)
    netlist = netlist.replace('CSV_FILE', output_csv)
    
    # Write the netlist
    with open(netlist_file, 'w') as f:
        f.write(netlist)
    
    print(f"Generated {netlist_file} for {band_name}")
    return netlist_file, output_png

def run_simulation(netlist_file):
    """Run ngspice simulation on a netlist."""
    
    print(f"Simulating {netlist_file}...")
    
    try:
        # Run ngspice in batch mode
        result = subprocess.run(
            ['ngspice', '-b', netlist_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check for errors
        if result.returncode != 0:
            print(f"  ERROR: Simulation failed!")
            print(f"  stderr: {result.stderr[:500]}")
            return False
        
        # Print relevant output
        for line in result.stdout.split('\n'):
            if 'Filter Response' in line:
                print(f"  {line}")
            elif 'fc =' in line or 'flo =' in line or 'fhi =' in line or 'bw =' in line:
                print(f"  {line}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"  ERROR: Simulation timed out!")
        return False
    except FileNotFoundError:
        print(f"  ERROR: ngspice not found. Please install ngspice.")
        return False

def main():
    """Main function to simulate all bands."""
    
    print("BPF MULTI-BAND SIMULATION")
    print("=" * 60)
    
    # Check if template exists
    if not os.path.exists('bpf-simulation-template.cir'):
        print("ERROR: bpf-simulation-template.cir not found!")
        sys.exit(1)
    
    # Check if band files exist
    missing_bands = []
    for band in bands:
        band_file = f"band{band['num']}.mod"
        if not os.path.exists(band_file):
            missing_bands.append(band_file)
    
    if missing_bands:
        print(f"ERROR: Missing band files: {', '.join(missing_bands)}")
        print("Run transformer-coupled-three-tank-bpf-minimal-fix.py first!")
        sys.exit(1)
    
    # Simulate each band
    successful = []
    failed = []
    
    for band in bands:
        netlist_file, output_png = generate_netlist(band)
        
        if run_simulation(netlist_file):
            if os.path.exists(output_png):
                file_size = os.path.getsize(output_png)
                print(f"  ✓ Generated {output_png} ({file_size} bytes)")
                successful.append(band['name'])
            else:
                print(f"  ⚠ Simulation ran but {output_png} not created")
                failed.append(band['name'])
        else:
            failed.append(band['name'])
        
        print()
    
    # Summary
    print("=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    
    if successful:
        print(f"✓ Successful: {len(successful)} bands")
        for name in successful:
            print(f"  - {name}")
    
    if failed:
        print(f"✗ Failed: {len(failed)} bands")
        for name in failed:
            print(f"  - {name}")
    
    print()
    print("Output files:")
    print("  - band[1-7]_response.png - Frequency response plots")
    print("  - band[1-7]_data.csv - Raw frequency/gain data")
    print("  - band[1-7].cir - Generated netlists")

if __name__ == '__main__':
    main()