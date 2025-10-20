#!/usr/bin/env python3
"""
Quick simulation script for the Chebyshev filter
Automatically calculates, simulates, and plots the response
"""

import sys
sys.path.append('.')
exec(open('coupled-resonator-filter.py').read())

# Calculate filter values
print("Calculating filter values...")
results = calculate_chebyshev_filter()

# Run simulation and plot
print("\nRunning SPICE simulation...")
plot_frequency_response(results, simulate=True)

print("\nSimulation complete! Check filter_response.png for the plot.")