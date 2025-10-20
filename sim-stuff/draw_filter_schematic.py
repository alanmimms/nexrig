#!/usr/bin/env python3
"""
Draw the schematic topology for the calculated Chebyshev bandpass filter
This shows the exact circuit that the Python calculations are designed for
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

def draw_filter_schematic():
    """Draw the filter schematic with component values"""
    
    # Component values from our calculations
    values = {
        'L': 1000.0,      # Tank inductors (nH)
        'C_tank': 101.42, # Tank capacitors (pF) 
        'C_coupling': 20.147, # Coupling caps (pF)
        'C_hot': 202.41,  # Hot side matching caps (pF)
        'C_cold': 101.20  # Cold side matching caps (pF)
    }
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    
    # Colors
    wire_color = 'black'
    component_color = 'blue'
    value_color = 'red'
    ground_color = 'green'
    
    # Draw ground symbols
    def draw_ground(x, y, size=0.3):
        # Ground symbol
        for i, length in enumerate([0.6, 0.4, 0.2]):
            y_pos = y - i*0.1
            ax.plot([x-length/2, x+length/2], [y_pos, y_pos], 'k-', linewidth=2)
    
    # Draw inductor symbol
    def draw_inductor(x1, y1, x2, y2, turns=4):
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        
        # Create coil shape
        t = np.linspace(0, turns*2*np.pi, 100)
        coil_x = np.linspace(0, length, 100)
        coil_y = 0.15 * np.sin(t)
        
        # Rotate and translate
        angle = np.arctan2(dy, dx)
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        
        rot_x = coil_x * cos_a - coil_y * sin_a + x1
        rot_y = coil_x * sin_a + coil_y * cos_a + y1
        
        ax.plot(rot_x, rot_y, component_color, linewidth=2)
    
    # Draw capacitor symbol  
    def draw_capacitor(x1, y1, x2, y2, vertical=False):
        if vertical:
            # Vertical capacitor
            mid_y = (y1 + y2) / 2
            gap = 0.1
            ax.plot([x1, x1], [y1, mid_y-gap], wire_color, linewidth=1.5)
            ax.plot([x2, x2], [mid_y+gap, y2], wire_color, linewidth=1.5)
            # Capacitor plates
            ax.plot([x1-0.15, x1+0.15], [mid_y-gap, mid_y-gap], component_color, linewidth=3)
            ax.plot([x2-0.15, x2+0.15], [mid_y+gap, mid_y+gap], component_color, linewidth=3)
        else:
            # Horizontal capacitor
            mid_x = (x1 + x2) / 2
            gap = 0.1
            ax.plot([x1, mid_x-gap], [y1, y1], wire_color, linewidth=1.5)
            ax.plot([mid_x+gap, x2], [y2, y2], wire_color, linewidth=1.5)
            # Capacitor plates
            ax.plot([mid_x-gap, mid_x-gap], [y1-0.15, y1+0.15], component_color, linewidth=3)
            ax.plot([mid_x+gap, mid_x+gap], [y2-0.15, y2+0.15], component_color, linewidth=3)
    
    # Main circuit horizontal line
    main_y = 5
    
    # Input section
    # Voltage source
    ax.add_patch(Circle((1, main_y), 0.3, fill=False, edgecolor='black', linewidth=2))
    ax.text(1, main_y, 'V', ha='center', va='center', fontsize=10, weight='bold')
    ax.text(1, main_y-0.6, '50Ω AC', ha='center', va='center', fontsize=8)
    
    # Input resistor
    rect = FancyBboxPatch((1.8, main_y-0.15), 0.6, 0.3, 
                         boxstyle="round,pad=0.02", 
                         facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(2.1, main_y, '50Ω', ha='center', va='center', fontsize=9)
    
    # Wires from source
    ax.plot([1.3, 1.8], [main_y, main_y], wire_color, linewidth=1.5)  # To resistor
    ax.plot([2.4, 3], [main_y, main_y], wire_color, linewidth=1.5)    # From resistor
    
    # Input matching network - Tapped capacitor
    ax.text(3.5, main_y+1, 'INPUT MATCHING', ha='center', fontsize=10, weight='bold', color='purple')
    ax.text(3.5, main_y+0.7, '(Tapped Capacitor)', ha='center', fontsize=9, color='purple')
    
    # C_hot (series capacitor)
    draw_capacitor(3, main_y, 4, main_y)
    ax.text(3.5, main_y+0.4, f'C_hot\n{values["C_hot"]:.1f}pF', 
            ha='center', va='center', fontsize=8, color=value_color, weight='bold')
    
    # Connection point (tap)
    tap_x = 4
    ax.plot([tap_x, tap_x], [main_y, main_y-1], wire_color, linewidth=1.5)
    
    # C_cold (shunt capacitor to ground)
    draw_capacitor(tap_x, main_y-1, tap_x, main_y-2, vertical=True)
    ax.text(tap_x+0.3, main_y-1.5, f'C_cold\n{values["C_cold"]:.1f}pF', 
            ha='left', va='center', fontsize=8, color=value_color, weight='bold')
    
    # Ground
    ax.plot([tap_x, tap_x], [main_y-2, main_y-2.3], wire_color, linewidth=1.5)
    draw_ground(tap_x, main_y-2.6)
    
    # Tank 1
    tank1_x = 5.5
    ax.plot([tap_x, tank1_x], [main_y, main_y], wire_color, linewidth=1.5)
    ax.plot([tank1_x, tank1_x], [main_y, main_y-1.5], wire_color, linewidth=1.5)
    
    # Tank 1 inductor (vertical)
    draw_inductor(tank1_x, main_y-1.5, tank1_x, main_y-2.5)
    ax.text(tank1_x-0.4, main_y-2, f'L1\n{values["L"]:.0f}nH', 
            ha='center', va='center', fontsize=8, color=value_color, weight='bold')
    
    # Tank 1 capacitor (vertical, parallel to inductor)
    draw_capacitor(tank1_x+0.3, main_y-1.5, tank1_x+0.3, main_y-2.5, vertical=True)
    ax.text(tank1_x+0.7, main_y-2, f'C1\n{values["C_tank"]:.1f}pF', 
            ha='left', va='center', fontsize=8, color=value_color, weight='bold')
    
    # Connect parallel components
    ax.plot([tank1_x, tank1_x+0.3], [main_y-1.5, main_y-1.5], wire_color, linewidth=1.5)
    ax.plot([tank1_x, tank1_x+0.3], [main_y-2.5, main_y-2.5], wire_color, linewidth=1.5)
    
    # Ground for tank 1
    ax.plot([tank1_x, tank1_x], [main_y-2.5, main_y-2.8], wire_color, linewidth=1.5)
    draw_ground(tank1_x, main_y-3.1)
    
    # Coupling capacitor C12
    coupling1_x = 7
    ax.plot([tank1_x, coupling1_x-0.5], [main_y, main_y], wire_color, linewidth=1.5)
    draw_capacitor(coupling1_x-0.5, main_y, coupling1_x+0.5, main_y)
    ax.text(coupling1_x, main_y+0.4, f'C12\n{values["C_coupling"]:.1f}pF', 
            ha='center', va='center', fontsize=8, color=value_color, weight='bold')
    ax.plot([coupling1_x+0.5, coupling1_x+1], [main_y, main_y], wire_color, linewidth=1.5)
    
    # Tank 2 (same as Tank 1)
    tank2_x = 8.5
    ax.plot([tank2_x, tank2_x], [main_y, main_y-1.5], wire_color, linewidth=1.5)
    
    draw_inductor(tank2_x, main_y-1.5, tank2_x, main_y-2.5)
    ax.text(tank2_x-0.4, main_y-2, f'L2\n{values["L"]:.0f}nH', 
            ha='center', va='center', fontsize=8, color=value_color, weight='bold')
    
    draw_capacitor(tank2_x+0.3, main_y-1.5, tank2_x+0.3, main_y-2.5, vertical=True)
    ax.text(tank2_x+0.7, main_y-2, f'C2\n{values["C_tank"]:.1f}pF', 
            ha='left', va='center', fontsize=8, color=value_color, weight='bold')
    
    ax.plot([tank2_x, tank2_x+0.3], [main_y-1.5, main_y-1.5], wire_color, linewidth=1.5)
    ax.plot([tank2_x, tank2_x+0.3], [main_y-2.5, main_y-2.5], wire_color, linewidth=1.5)
    ax.plot([tank2_x, tank2_x], [main_y-2.5, main_y-2.8], wire_color, linewidth=1.5)
    draw_ground(tank2_x, main_y-3.1)
    
    # Coupling capacitor C23
    coupling2_x = 10
    ax.plot([tank2_x, coupling2_x-0.5], [main_y, main_y], wire_color, linewidth=1.5)
    draw_capacitor(coupling2_x-0.5, main_y, coupling2_x+0.5, main_y)
    ax.text(coupling2_x, main_y+0.4, f'C23\n{values["C_coupling"]:.1f}pF', 
            ha='center', va='center', fontsize=8, color=value_color, weight='bold')
    ax.plot([coupling2_x+0.5, coupling2_x+1], [main_y, main_y], wire_color, linewidth=1.5)
    
    # Tank 3
    tank3_x = 11.5
    ax.plot([tank3_x, tank3_x], [main_y, main_y-1.5], wire_color, linewidth=1.5)
    
    draw_inductor(tank3_x, main_y-1.5, tank3_x, main_y-2.5)
    ax.text(tank3_x-0.4, main_y-2, f'L3\n{values["L"]:.0f}nH', 
            ha='center', va='center', fontsize=8, color=value_color, weight='bold')
    
    draw_capacitor(tank3_x+0.3, main_y-1.5, tank3_x+0.3, main_y-2.5, vertical=True)
    ax.text(tank3_x+0.7, main_y-2, f'C3\n{values["C_tank"]:.1f}pF', 
            ha='left', va='center', fontsize=8, color=value_color, weight='bold')
    
    ax.plot([tank3_x, tank3_x+0.3], [main_y-1.5, main_y-1.5], wire_color, linewidth=1.5)
    ax.plot([tank3_x, tank3_x+0.3], [main_y-2.5, main_y-2.5], wire_color, linewidth=1.5)
    ax.plot([tank3_x, tank3_x], [main_y-2.5, main_y-2.8], wire_color, linewidth=1.5)
    draw_ground(tank3_x, main_y-3.1)
    
    # Output matching network - Tapped capacitor (mirror of input)
    ax.text(12.5, main_y+1, 'OUTPUT MATCHING', ha='center', fontsize=10, weight='bold', color='purple')
    ax.text(12.5, main_y+0.7, '(Tapped Capacitor)', ha='center', fontsize=9, color='purple')
    
    # Connection from Tank 3
    tap2_x = 12
    ax.plot([tank3_x, tap2_x], [main_y, main_y], wire_color, linewidth=1.5)
    
    # C_cold (shunt capacitor to ground) - on tank side
    ax.plot([tap2_x, tap2_x], [main_y, main_y-1], wire_color, linewidth=1.5)
    draw_capacitor(tap2_x, main_y-1, tap2_x, main_y-2, vertical=True)
    ax.text(tap2_x-0.3, main_y-1.5, f'C_cold\n{values["C_cold"]:.1f}pF', 
            ha='right', va='center', fontsize=8, color=value_color, weight='bold')
    ax.plot([tap2_x, tap2_x], [main_y-2, main_y-2.3], wire_color, linewidth=1.5)
    draw_ground(tap2_x, main_y-2.6)
    
    # C_hot (series capacitor) - to load
    draw_capacitor(tap2_x, main_y, tap2_x+1, main_y)
    ax.text(tap2_x+0.5, main_y+0.4, f'C_hot\n{values["C_hot"]:.1f}pF', 
            ha='center', va='center', fontsize=8, color=value_color, weight='bold')
    
    # Output load
    ax.plot([tap2_x+1, tap2_x+1.5], [main_y, main_y], wire_color, linewidth=1.5)
    rect2 = FancyBboxPatch((tap2_x+1.5, main_y-0.15), 0.6, 0.3, 
                          boxstyle="round,pad=0.02", 
                          facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(rect2)
    ax.text(tap2_x+1.8, main_y, '50Ω', ha='center', va='center', fontsize=9)
    ax.text(tap2_x+1.8, main_y-0.6, 'LOAD', ha='center', va='center', fontsize=8)
    
    # Title and descriptions
    ax.text(8, 7.5, 'CALCULATED CHEBYSHEV BANDPASS FILTER SCHEMATIC', 
            ha='center', va='center', fontsize=14, weight='bold')
    ax.text(8, 7, '3rd Order, 0.1dB Ripple, 13.5-18.5 MHz (f₀=15.8MHz, BW=5MHz)', 
            ha='center', va='center', fontsize=11)
    
    # Add explanation box
    explanation = """KEY FEATURES:
• Three LC tank resonators (all tuned to f₀)
• Capacitive coupling between tanks
• Tapped-capacitor input/output matching
• 50Ω impedance matching
• Values calculated to match your schematic"""
    
    ax.text(1, 2.5, explanation, fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8),
            verticalalignment='top')
    
    # Add circuit analysis
    analysis = """IMPEDANCE MATCHING:
• C_hot provides series reactance
• C_cold provides shunt loading  
• 2:1 ratio gives 50Ω→100Ω transform
• Total series C sets external coupling"""
    
    ax.text(14, 2.5, analysis, fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
            verticalalignment='top')
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('calculated_filter_schematic.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("\\nSchematic drawn for the calculated filter topology!")
    print("This shows the exact circuit that the Python script calculates component values for.")
    print("Compare this with your KiCad schematic to identify any differences.")
    print("Schematic saved as 'calculated_filter_schematic.png'")

if __name__ == "__main__":
    draw_filter_schematic()