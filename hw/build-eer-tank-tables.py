import math
import csv
from collections import defaultdict

# --- Configuration Constants ---

# Optimal load impedance for the PA
R_L_OHMS = 3.125

# E24 standard values for the 8-bit binary weighted capacitor bank (MSB to LSB)
CAP_BANK_PF = [1800, 620, 330, 160, 82, 39, 20, 10]

# Band plan definition: [Name, F_low_MHz, F_high_MHz]
BAND_PLAN = [
    ["160m", 1.8, 2.0],
    ["80m", 3.5, 4.0],
    ["60m", 5.0, 5.5],
    ["40m", 6.9, 7.5],
    ["30m", 9.9, 10.5],
    ["20m", 13.9, 15.1],
    ["17m", 17.85, 18.35],
    ["15m", 20.0, 21.5],
    ["12m", 24.5, 25.1],
    ["10m", 28.0, 29.7]
]

# Assigned inductor for each band from the band plan
INDUCTOR_ASSIGNMENTS_NH = [500, 500, 500, 300, 300, 82, 82, 82, 82, 47]

# Number of intermediate tuning steps to calculate within each band
TUNING_STEPS_PER_BAND = 5

# --- Helper Functions ---

def calculate_c_pf(f_mhz, l_nh):
    """Calculates capacitance in pF for a given frequency and inductance."""
    omega = 2 * math.pi * f_mhz * 1e6
    l_h = l_nh * 1e-9
    c_f = 1 / (l_h * omega**2)
    return c_f * 1e12

def calculate_f_mhz(c_pf, l_nh):
    """Calculates resonant frequency in MHz for a given capacitance and inductance."""
    c_f = c_pf * 1e-12
    l_h = l_nh * 1e-9
    f_hz = 1 / (2 * math.pi * math.sqrt(l_h * c_f))
    return f_hz / 1e6

def find_best_cap_combo(target_delta_c, cap_bank):
    """
    Finds the combination of capacitors from the bank that produces the
    capacitance closest to the target delta_C.
    Iterates through all 256 possible combinations.
    """
    best_sum = 0
    best_combo_index = 0
    min_error = float('inf')

    for i in range(256):
        current_sum = 0
        for j in range(8):
            if (i >> j) & 1:
                current_sum += cap_bank[7 - j]
        
        error = abs(current_sum - target_delta_c)

        if error < min_error:
            min_error = error
            best_sum = current_sum
            best_combo_index = i
            
    return best_sum, best_combo_index

# --- Main Script Logic ---

def generate_tuning_table():
    """Generates the full tuning table data, including switch points."""
    
    # This dictionary will hold the calculated tuning points, grouped by band
    tuning_points_by_band = defaultdict(list)
    
    # First, calculate all the discrete tuning points for each band
    for i, band in enumerate(BAND_PLAN):
        name, f_low, f_high = band
        l_nh = INDUCTOR_ASSIGNMENTS_NH[i]
        c_fixed_pf = calculate_c_pf(f_high, l_nh)
        f_center_mhz = (f_low + f_high) / 2
        q_factor = (2 * math.pi * f_center_mhz * 1e6 * (l_nh * 1e-9)) / R_L_OHMS


        for step in range(TUNING_STEPS_PER_BAND):
            if TUNING_STEPS_PER_BAND <= 1:
                target_f = f_low
            else:
                 target_f = f_high - (step * (f_high - f_low) / (TUNING_STEPS_PER_BAND - 1))

            if step == 0:
                tuned_delta_c = 0
                combo_index = 0
                tuned_f = f_high
            else:
                ideal_total_c = calculate_c_pf(target_f, l_nh)
                ideal_delta_c = ideal_total_c - c_fixed_pf
                tuned_delta_c, combo_index = find_best_cap_combo(ideal_delta_c, CAP_BANK_PF)
                tuned_total_c = c_fixed_pf + tuned_delta_c
                tuned_f = calculate_f_mhz(tuned_total_c, l_nh)

            tuning_points_by_band[name].append({
                "Tuned_F_center": tuned_f,
                "Tuning_Code": combo_index,
                "Tuned_Delta_C": tuned_delta_c,
                "L_nH": l_nh,
                "Q": q_factor,
                "C_fixed": c_fixed_pf,
                "F_low": f_low,
                "F_high": f_high,
            })

    # Now, process the points to calculate the switchover frequencies
    final_csv_data = []
    header = [
        "Band", "L (nH)", "Q", "Cfixed (pF)", 
        "Tuning (hex)", "Delta C (pF)", "Fcenter (MHz)",
        "Fhigh (MHz)", "Flow (MHz)"
    ]
    final_csv_data.append(header)
    
    for band_name, points in tuning_points_by_band.items():
        # Sort points by frequency descending to make calculations easier
        points.sort(key=lambda p: p["Tuned_F_center"], reverse=True)
        
        for i, point in enumerate(points):
            # The highest frequency for this setting is the band edge or midpoint with the step above
            if i == 0:
                switch_high = point["F_high"]
            else:
                midpoint = (point["Tuned_F_center"] + points[i-1]["Tuned_F_center"]) / 2
                switch_high = midpoint

            # The lowest frequency for this setting is the band edge or midpoint with the step below
            if i == len(points) - 1:
                switch_low = point["F_low"]
            else:
                midpoint = (point["Tuned_F_center"] + points[i+1]["Tuned_F_center"]) / 2
                switch_low = midpoint

            row = [
                band_name,
                point["L_nH"],
                f"{point['Q']:.1f}",
                f"{point['C_fixed']:.1f}",
                f"{point['Tuning_Code']:02X}",
                point["Tuned_Delta_C"],
                f"{point['Tuned_F_center']:.3f}",
                f"{switch_high:.3f}",
                f"{switch_low:.3f}"
            ]
            final_csv_data.append(row)
            
    return final_csv_data

def write_csv_file(data, filename="eer-tank-tables.csv"):
    """Writes the provided data to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    print(f"Successfully generated '{filename}'")


if __name__ == "__main__":
    table_data = generate_tuning_table()
    write_csv_file(table_data)
