#!/usr/bin/env python3
"""
Compare the calculated filter values with your KiCad schematic values
to identify potential topology differences
"""

def compare_designs():
    """Compare calculated vs schematic values"""
    
    print("FILTER DESIGN COMPARISON")
    print("=" * 50)
    
    # Our calculated values
    calculated = {
        'C_hot_input': 202.41,
        'C_cold_input': 101.20,
        'C_hot_output': 202.41,
        'C_cold_output': 101.20,
        'C_tank': 101.42,
        'C_coupling': 20.147,
        'L_tank': 1000.0
    }
    
    # Values from your KiCad schematic (as seen in screenshot)
    schematic = {
        'C_hot_input': 202.8,   # C7951 (from screenshot)
        'C_cold_input': 100.71,  # C7974 (from screenshot)  
        'C_hot_output': 202.8,   # C7939 (from screenshot)
        'C_cold_output': 100.71, # C7940 (from screenshot)
        'C_tank': 101.42,        # C7938 (from screenshot)
        'C_coupling': 20.147,    # C7936, C7933 (from screenshot)
        'L_tank': 1000.0         # L7805, L7807, L7809 (1uH = 1000nH)
    }
    
    print(f"{'Component':<15} {'Calculated':<12} {'Schematic':<12} {'Diff %':<8}")
    print("-" * 55)
    
    for key in calculated:
        calc_val = calculated[key]
        schem_val = schematic[key]
        diff_pct = abs(calc_val - schem_val) / schem_val * 100
        
        status = "✓" if diff_pct < 5 else "⚠" if diff_pct < 10 else "✗"
        
        print(f"{key:<15} {calc_val:<12.2f} {schem_val:<12.2f} {diff_pct:<8.1f}% {status}")
    
    print("\n" + "=" * 50)
    print("ANALYSIS:")
    print("✓ = Good match (<5% difference)")
    print("⚠ = Acceptable (5-10% difference)")  
    print("✗ = Poor match (>10% difference)")
    
    print("\nVALUE MATCH QUALITY:")
    print("- Tank components: Perfect match")
    print("- Coupling caps: Perfect match") 
    print("- Matching caps: Near-perfect match (~0.5% error)")
    print("\nCONCLUSION:")
    print("The calculated values match your schematic very well!")
    print("The component values are NOT the problem.")
    
    print("\n" + "=" * 50)
    print("LIKELY ISSUES CAUSING BAD SIMULATION:")
    print("\n1. SIMULATION SETUP PROBLEMS:")
    print("   • Wrong frequency range in simulation")
    print("   • Incorrect AC analysis setup")
    print("   • Missing ground connections")
    print("   • Wrong probe points")
    
    print("\n2. SCHEMATIC TOPOLOGY ISSUES:")
    print("   • Check if C_cold caps are actually connected to ground")
    print("   • Verify the tapped-capacitor configuration")  
    print("   • Make sure all grounds are properly connected")
    print("   • Check that coupling caps are in the right places")
    
    print("\n3. COMPONENT MODEL PROBLEMS:")
    print("   • Inductor parasitic resistance/Q")
    print("   • Capacitor ESR or parasitic inductance")
    print("   • Non-ideal component models")
    
    print("\nRECOMMENDATIONS:")
    print("1. Double-check your schematic topology against the ASCII art above")
    print("2. Verify ground connections for C_cold capacitors")
    print("3. Check simulation frequency range (should be 1-100 MHz)")
    print("4. Try ideal components first (R=0, perfect L/C)")
    print("5. Make sure you're probing the right output node")

if __name__ == "__main__":
    compare_designs()