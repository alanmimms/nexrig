import math

def calculate_filter_components(f_low_mhz, f_high_mhz, ripple_db, impedance_z):
    """
    Calculates component values and coil winding data for a 3-pole
    capacitively-coupled Chebyshev bandpass filter.

    Args:
        f_low_mhz (float): Lower cutoff frequency in MHz.
        f_high_mhz (float): Upper cutoff frequency in MHz.
        ripple_db (float): Passband ripple in dB.
        impedance_z (int): Filter characteristic impedance in Ohms.
    """

    # --- 1. Basic Filter Parameters ---
    f_low = f_low_mhz * 1e6
    f_high = f_high_mhz * 1e6
    f0 = math.sqrt(f_low * f_high)
    bw = f_high - f_low
    fbw = bw / f0

    print("-" * 50)
    print(f"Filter Design for {f_low_mhz:.2f} MHz to {f_high_mhz:.2f} MHz")
    print(f"Impedance: {impedance_z} Ohms, Ripple: {ripple_db} dB")
    print("-" * 50)
    print(f"Center Frequency (f0): {f0 / 1e6:.3f} MHz")
    print(f"Bandwidth (BW):       {bw / 1e6:.3f} MHz")
    print(f"Fractional BW (fbw):  {fbw:.4f}")
    print("-" * 50)

    # --- 2. Chebyshev g-value Calculation for n=3 ---
    # These are the standard formulas for the low-pass prototype elements.
    beta = math.log(1 / math.tanh(ripple_db / 17.37))
    gamma = math.sinh(beta / (2 * 3)) # n=3 for a 3-pole filter
    a1 = math.sin(math.pi / (2 * 3))
    b1 = gamma**2 + math.sin(math.pi / 3)**2

    g1 = (2 * a1) / gamma
    g2 = (4 * a1 * math.sin(3 * math.pi / 6)) / (b1 * g1)
    g3 = g1 # Symmetrical filter

    # --- 3. Bandpass Component Calculation (CORRECTED FORMULAS) ---
    # Calculate the ideal inductor value required for this response
    L = (impedance_z * fbw) / (g1 * 2 * math.pi * f0)
    L_nH = L * 1e9

    # Calculate the initial tank capacitor value to resonate L at f0
    C_tank_initial = 1 / ((2 * math.pi * f0)**2 * L)
    C_tank_initial_pF = C_tank_initial * 1e12

    # Calculate the coupling capacitor values
    C12 = (C_tank_initial * fbw) / math.sqrt(g1 * g2)
    C23 = (C_tank_initial * fbw) / math.sqrt(g2 * g3) # Same as C12 for symmetrical
    C12_pF = C12 * 1e12
    C23_pF = C23 * 1e12

    # --- 4. Adjust Tank Capacitors for Coupling Cap Loading ---
    # The coupling caps add to the total capacitance at each node,
    # so the physical tank caps must be reduced.
    C1_adj = C_tank_initial - C12
    C2_adj = C_tank_initial - C12 - C23
    C3_adj = C_tank_initial - C23

    C1_adj_pF = C1_adj * 1e12
    C2_adj_pF = C2_adj * 1e12
    C3_adj_pF = C3_adj * 1e12

    print("COMPONENT VALUES:")
    print(f"  Inductors (L1, L2, L3):      {L_nH:.2f} nH")
    print(f"  Coupling Caps (C12, C23):    {C12_pF:.2f} pF")
    print("\nADJUSTED TANK CAPACITOR VALUES (for assembly):")
    print(f"  Tank Cap C1 (End):           {C1_adj_pF:.2f} pF")
    print(f"  Tank Cap C2 (Middle):        {C2_adj_pF:.2f} pF")
    print(f"  Tank Cap C3 (End):           {C3_adj_pF:.2f} pF")
    print("-" * 50)

    # --- 5. Toroid Winding Calculation ---
    # Data for Micrometals T37 cores. AL is in nH/turns^2.
    toroid_data = {
        'T37-2': {'material': '2 (Red)', 'AL': 5.5, 'freq_range_mhz': (2, 30)},
        'T37-6': {'material': '6 (Yellow)', 'AL': 4.0, 'freq_range_mhz': (10, 50)},
        'T37-10': {'material': '10 (Black)', 'AL': 2.5, 'freq_range_mhz': (30, 100)},
    }

    # Select the best core for the center frequency
    f0_mhz = f0 / 1e6
    best_core_name = None
    for name, data in toroid_data.items():
        if data['freq_range_mhz'][0] <= f0_mhz <= data['freq_range_mhz'][1]:
            best_core_name = name
            break

    if not best_core_name:
        print("COIL WINDING INFO:\n  No suitable T37 core found for this frequency range.")
        return

    core_info = toroid_data[best_core_name]
    AL = core_info['AL']

    # Calculate turns for the secondary (main inductor)
    turns_secondary_ideal = math.sqrt(L_nH / AL)
    turns_secondary = round(turns_secondary_ideal)

    # Recalculate inductance based on the actual whole number of turns
    L_actual_nH = AL * (turns_secondary**2)

    # Calculate primary turns for a 1:2 ratio (50 -> 200 Ohm)
    turns_primary = round(turns_secondary / 2)

    print("COIL WINDING INFO:")
    print(f"  Selected Core:               {best_core_name} (Material {core_info['material']})")
    print(f"  Core AL Value:               {AL} nH/N^2")
    print(f"  Target Inductance:           {L_nH:.2f} nH")
    print("\n  WINDING (for L1 and L3 matching transformers):")
    print(f"    Primary Turns (50 Ohm):    {turns_primary} turns")
    print(f"    Secondary Turns (200 Ohm): {turns_secondary} turns")
    print("\n  WINDING (for L2 center inductor):")
    print(f"    Total Turns:               {turns_secondary} turns")
    print(f"\n  Actual Inductance:           ~{L_actual_nH:.2f} nH with {turns_secondary} turns")
    print("  (Note: Adjust tank capacitors slightly to tune for this actual inductance)")
    print("-" * 50)


if __name__ == '__main__':
    # --- USER PARAMETERS ---
    # Change these values to design a new filter.
    F_LOW_MHZ   = 13.5
    F_HIGH_MHZ  = 18.5
    RIPPLE_DB   = 0.1
    IMPEDANCE_Z = 200

    calculate_filter_components(F_LOW_MHZ, F_HIGH_MHZ, RIPPLE_DB, IMPEDANCE_Z)

    # --- Example for another band ---
    # print("\n\n")
    # calculate_filter_components(f_low_mhz=6.8, f_high_mhz=7.4, ripple_db=0.1, impedance_z=200)

