#!/usr/bin/env python3
"""
PCB Parasitic Capacitance Design Calculator
===========================================

Calculate and design PCB trace capacitors for RF filters.
Use controlled PCB geometry to create stable, repeatable capacitance values.

Especially useful for:
- Small coupling capacitors (< 10 pF)
- Trimming/padding existing capacitors
- Temperature-stable capacitance (PCB FR4 has good temp coefficient)

Author: Claude
"""

import math
import numpy as np

# PCB Material Constants
EPSILON_0 = 8.854e-12  # F/m, permittivity of free space
EPSILON_FR4 = 4.4      # Typical FR4 relative permittivity at 10-20 MHz
EPSILON_ROGERS = 3.0   # Rogers 4003C for better RF performance

# Standard PCB Parameters
STANDARD_THICKNESSES_MM = {
    "2-layer": 1.6,
    "4-layer_outer": 0.36,  # Typical 4-layer stackup outer prepreg
    "4-layer_inner": 0.71,  # Typical 4-layer stackup inner core
    "thin": 0.2,            # Thin PCB or close spacing
}

def calculate_parallel_plate_capacitance(area_mm2, thickness_mm, epsilon_r=EPSILON_FR4):
    """
    Calculate capacitance of parallel plate capacitor on PCB.
    
    Args:
        area_mm2: Overlap area in mm²
        thickness_mm: Dielectric thickness in mm
        epsilon_r: Relative permittivity
    
    Returns:
        Capacitance in pF
    """
    area_m2 = area_mm2 * 1e-6
    thickness_m = thickness_mm * 1e-3
    
    C_farads = EPSILON_0 * epsilon_r * area_m2 / thickness_m
    C_pF = C_farads * 1e12
    
    return C_pF

def calculate_interdigital_capacitance(n_fingers, length_mm, width_mm, gap_mm, epsilon_r=EPSILON_FR4):
    """
    Calculate capacitance of interdigital capacitor on PCB surface.
    
    Args:
        n_fingers: Number of fingers
        length_mm: Length of each finger
        width_mm: Width of each finger  
        gap_mm: Gap between fingers
        epsilon_r: Relative permittivity
    
    Returns:
        Capacitance in pF (approximate)
    """
    # Approximate formula for interdigital capacitors
    # Based on empirical data and conformal mapping
    
    # Number of gaps
    n_gaps = n_fingers - 1
    
    # Capacitance per unit length (pF/mm)
    # Simplified model - more accurate models exist but are complex
    C_per_mm = epsilon_r * 0.1 * (width_mm / gap_mm) ** 0.5
    
    # Total capacitance
    C_pF = C_per_mm * length_mm * n_gaps
    
    return C_pF

def calculate_edge_capacitance(length_mm, gap_mm, trace_width_mm, epsilon_r=EPSILON_FR4):
    """
    Calculate edge-to-edge capacitance between parallel traces.
    
    Args:
        length_mm: Length of parallel run
        gap_mm: Gap between traces
        trace_width_mm: Width of traces
        epsilon_r: Relative permittivity
    
    Returns:
        Capacitance in pF
    """
    # Approximate edge capacitance
    # Based on microstrip coupled line theory
    
    # Effective epsilon (accounting for air above PCB)
    epsilon_eff = (epsilon_r + 1) / 2
    
    # Capacitance per unit length (rough approximation)
    C_per_mm = epsilon_eff * EPSILON_0 * 1e12 * (trace_width_mm / gap_mm) * 0.7
    
    # Total capacitance
    C_pF = C_per_mm * length_mm
    
    return C_pF

def design_pcb_capacitor(target_pF, method="parallel_plate", constraints=None):
    """
    Design PCB capacitor geometry for target capacitance.
    
    Args:
        target_pF: Target capacitance in pF
        method: "parallel_plate", "interdigital", or "edge"
        constraints: Dict with design constraints
    
    Returns:
        Dict with design parameters
    """
    
    if constraints is None:
        constraints = {}
    
    designs = []
    
    if method == "parallel_plate" or method == "all":
        # Parallel plate design (overlapping pads on opposite layers)
        for thickness_name, thickness_mm in STANDARD_THICKNESSES_MM.items():
            # Calculate required area
            area_mm2 = target_pF * thickness_mm / (EPSILON_0 * EPSILON_FR4 * 1e12 * 1e-3)
            
            # Convert to square pad
            side_mm = math.sqrt(area_mm2)
            
            if side_mm < 50:  # Reasonable size limit
                designs.append({
                    "method": "parallel_plate",
                    "stackup": thickness_name,
                    "thickness_mm": thickness_mm,
                    "area_mm2": area_mm2,
                    "dimensions": f"{side_mm:.1f}×{side_mm:.1f} mm square pads",
                    "capacitance_pF": target_pF,
                    "tolerance": "±10% (depends on PCB εr tolerance)",
                    "temp_coef": "~100 ppm/°C (FR4)",
                    "advantages": "Simple, predictable, good for 5-50pF",
                })
    
    if method == "interdigital" or method == "all":
        # Interdigital design (fingers on same layer)
        gap_mm = constraints.get("min_gap", 0.15)  # Typical PCB min gap
        width_mm = constraints.get("trace_width", 0.3)
        
        for n_fingers in [3, 5, 7, 10]:
            for length_mm in [5, 10, 15, 20]:
                C_calc = calculate_interdigital_capacitance(n_fingers, length_mm, width_mm, gap_mm)
                
                if abs(C_calc - target_pF) / target_pF < 0.2:  # Within 20%
                    designs.append({
                        "method": "interdigital",
                        "n_fingers": n_fingers,
                        "finger_length_mm": length_mm,
                        "finger_width_mm": width_mm,
                        "gap_mm": gap_mm,
                        "dimensions": f"{n_fingers} fingers, {length_mm}mm long",
                        "capacitance_pF": C_calc,
                        "tolerance": "±15% (can be laser trimmed)",
                        "temp_coef": "~100 ppm/°C",
                        "advantages": "Single layer, tunable, good for 0.5-10pF",
                    })
    
    if method == "edge" or method == "all":
        # Edge coupling (parallel traces)
        gap_mm = constraints.get("min_gap", 0.15)
        width_mm = constraints.get("trace_width", 0.5)
        
        # Calculate required length
        length_mm = target_pF / (EPSILON_FR4 * EPSILON_0 * 1e12 * (width_mm / gap_mm) * 0.7 / 2)
        
        if length_mm < 100:  # Reasonable length
            designs.append({
                "method": "edge_coupling", 
                "length_mm": length_mm,
                "gap_mm": gap_mm,
                "trace_width_mm": width_mm,
                "dimensions": f"{length_mm:.1f}mm parallel run, {gap_mm}mm gap",
                "capacitance_pF": target_pF,
                "tolerance": "±20% (varies with routing)",
                "temp_coef": "~100 ppm/°C",
                "advantages": "No vias needed, good for 0.1-5pF",
            })
    
    return designs

def calculate_pcb_coupling_network(system_impedance, coupling_pF, f_center_MHz):
    """
    Design complete coupling network using PCB capacitance.
    
    For very small coupling caps, use PCB traces.
    For trimming, use PCB in parallel with chip capacitor.
    """
    print(f"\nPCB COUPLING NETWORK DESIGN")
    print(f"System Impedance: {system_impedance}Ω")
    print(f"Required Coupling: {coupling_pF:.2f} pF")
    print(f"Center Frequency: {f_center_MHz:.1f} MHz")
    print("-" * 60)
    
    if coupling_pF < 5:
        print("RECOMMENDATION: Use PCB-only capacitor")
        print("This value is small enough for stable PCB implementation")
        
        designs = design_pcb_capacitor(coupling_pF, method="all")
        print("\nPCB Design Options:")
        for i, design in enumerate(designs[:3], 1):  # Show top 3
            print(f"\nOption {i}: {design['method']}")
            print(f"  Geometry: {design['dimensions']}")
            print(f"  Calculated: {design['capacitance_pF']:.2f} pF")
            print(f"  Tolerance: {design['tolerance']}")
            print(f"  Advantages: {design['advantages']}")
            
    elif coupling_pF < 20:
        print("RECOMMENDATION: Hybrid approach")
        
        # Use nearest standard chip capacitor
        standard_caps = [6.8, 8.2, 10, 12, 15, 18, 22]
        chip_cap = max([c for c in standard_caps if c < coupling_pF], default=0)
        
        if chip_cap > 0:
            pcb_cap_needed = coupling_pF - chip_cap
            print(f"  Chip capacitor: {chip_cap} pF (standard value)")
            print(f"  PCB trimming: {pcb_cap_needed:.2f} pF")
            
            if pcb_cap_needed > 0:
                designs = design_pcb_capacitor(pcb_cap_needed, method="all")
                if designs:
                    design = designs[0]
                    print(f"  PCB geometry: {design['dimensions']}")
                    print(f"  Method: {design['method']}")
        else:
            print("  Use PCB-only design")
            
    else:
        print("RECOMMENDATION: Use chip capacitor")
        print(f"  Value > 20pF is better suited for discrete components")
        print(f"  Consider PCB pad capacitance (~0.3pF) in final value")

def analyze_environmental_stability():
    """
    Analyze environmental stability including humidity, temperature, and manufacturing variations.
    """
    print("\nENVIRONMENTAL STABILITY ANALYSIS")
    print("=" * 80)
    
    print("\n1. TEMPERATURE COEFFICIENT COMPARISON:")
    print("-" * 60)
    temp_data = [
        ("PCB FR4", 100, "±50", "Predictable linear"),
        ("PCB Rogers 4003", 50, "±25", "Better RF material"),
        ("NP0/C0G ceramic", 30, "±15", "Excellent but expensive"),
        ("X7R ceramic", 1500, "±750", "Poor for filters"),
        ("X5R ceramic", 2500, "±1250", "Avoid for RF"),
    ]
    
    print(f"{'Type':<18} {'Typ (ppm/°C)':<15} {'Tol (ppm/°C)':<15} {'Notes'}")
    print("-" * 70)
    for typ, tempco, tol, notes in temp_data:
        print(f"{typ:<18} {tempco:<15} {tol:<15} {notes}")
    
    print("\n2. HUMIDITY EFFECTS ON FR4:")
    print("-" * 60)
    humidity_data = [
        ("Dry (0% RH)", 4.3, "Baseline"),
        ("Normal (50% RH)", 4.4, "Typical spec"),
        ("High (85% RH)", 4.6, "Worst case"),
        ("Saturated (95% RH)", 4.8, "Extreme humidity"),
    ]
    
    print(f"{'Condition':<20} {'εr':<8} {'Notes'}")
    print("-" * 40)
    for condition, er, notes in humidity_data:
        delta_pct = (er - 4.4) / 4.4 * 100
        print(f"{condition:<20} {er:<8.1f} {notes} ({delta_pct:+.1f}%)")
    
    print("\n3. BATCH-TO-BATCH VARIATIONS:")
    print("-" * 60)
    batch_data = [
        ("εr tolerance", "±10%", "Typical PCB fab spec"),
        ("Thickness tol", "±10%", "Prepreg manufacturing"),
        ("Resin content", "±5%", "Affects εr significantly"),
        ("Glass weave", "Varies", "Different weave patterns"),
        ("Cure cycle", "±3%", "Time/temp variations"),
    ]
    
    print(f"{'Parameter':<20} {'Variation':<12} {'Impact'}")
    print("-" * 50)
    for param, var, impact in batch_data:
        print(f"{param:<20} {var:<12} {impact}")
    
    print("\n4. TOTAL CAPACITANCE VARIATION ANALYSIS:")
    print("-" * 60)
    
    # Example calculation for 10pF nominal PCB capacitor
    nominal_pF = 10.0
    
    variations = {
        "εr batch tolerance": 10.0,    # ±10% typical
        "Thickness tolerance": 10.0,   # ±10% typical
        "Humidity (50→85% RH)": 4.5,   # 4.4→4.6 εr
        "Temperature (-40→85°C)": 12.5, # 125°C × 100ppm/°C
        "Manufacturing process": 5.0,   # Etching, drilling variations
    }
    
    print(f"Analysis for {nominal_pF} pF PCB capacitor:")
    print(f"{'Source':<25} {'±%':<8} {'±pF':<8} {'Correlation'}")
    print("-" * 55)
    
    for source, pct_var, correl in [
        ("εr batch tolerance", 10.0, "Independent"),
        ("Thickness tolerance", 10.0, "Independent"), 
        ("Humidity variation", 4.5, "Environmental"),
        ("Temperature swing", 12.5, "Environmental"),
        ("Process variation", 5.0, "Independent"),
    ]:
        pf_var = nominal_pF * pct_var / 100
        print(f"{source:<25} {pct_var:<8.1f} {pf_var:<8.2f} {correl}")
    
    # RSS calculation (assuming independence where appropriate)
    independent_vars = [10.0, 10.0, 5.0]  # εr, thickness, process
    environmental_vars = [4.5, 12.5]       # humidity, temperature
    
    rss_independent = math.sqrt(sum(v**2 for v in independent_vars))
    rss_environmental = math.sqrt(sum(v**2 for v in environmental_vars))
    
    print(f"\nStatistical Analysis (RSS):")
    print(f"  Manufacturing (3σ): ±{rss_independent:.1f}%")
    print(f"  Environmental:      ±{rss_environmental:.1f}%")
    print(f"  Total worst-case:   ±{rss_independent + rss_environmental:.1f}%")
    
    total_var_pF = nominal_pF * (rss_independent + rss_environmental) / 100
    print(f"  For 10pF cap:       ±{total_var_pF:.2f} pF variation")
    
    return rss_independent, rss_environmental

def mitigation_strategies():
    """
    Provide strategies to minimize environmental and manufacturing variations.
    """
    print("\n" + "=" * 80)
    print("MITIGATION STRATEGIES FOR PCB CAPACITOR VARIATIONS")
    print("=" * 80)
    
    print("\n1. DESIGN STRATEGIES:")
    print("-" * 50)
    strategies = [
        ("Use hybrid approach", "PCB + chip cap reduces sensitivity"),
        ("Controlled impedance PCB", "Better εr control and documentation"),
        ("Inner layer placement", "More stable environment, less moisture"),
        ("Symmetrical layout", "Matching cancels some variations"),
        ("Larger geometries", "Reduces edge effects and tolerance impact"),
        ("Guard rings", "Shields from external variations"),
    ]
    
    for strategy, benefit in strategies:
        print(f"  • {strategy:<25} → {benefit}")
    
    print("\n2. MATERIAL SELECTION:")
    print("-" * 50)
    materials = [
        ("Rogers 4003C", "εr=3.38±0.05", "Much tighter tolerance, lower humidity"),
        ("Rogers 4350B", "εr=3.48±0.05", "Good compromise cost/performance"),
        ("Isola I-Tera MT40", "εr=3.45±0.03", "Very low moisture absorption"),
        ("Standard FR4", "εr=4.4±0.4", "Cheapest but highest variation"),
    ]
    
    print(f"{'Material':<20} {'εr Tolerance':<15} {'Notes'}")
    print("-" * 60)
    for material, er_tol, notes in materials:
        print(f"{material:<20} {er_tol:<15} {notes}")
    
    print("\n3. MANUFACTURING CONTROLS:")
    print("-" * 50)
    controls = [
        ("Specify εr tolerance", "±5% instead of ±10%", "Costs ~20% more"),
        ("Controlled dielectric", "Specify exact thickness", "±5% achievable"),
        ("Material certification", "Request εr test data", "Know actual values"),
        ("Environmental preconditioning", "Bake before assembly", "Removes moisture"),
        ("Test coupons", "Measure actual capacitance", "Verify design"),
    ]
    
    for control, method, cost in controls:
        print(f"  • {control:<25} → {method:<25} ({cost})")
    
    print("\n4. CIRCUIT DESIGN COMPENSATION:")
    print("-" * 50)
    
    # Calculate coupling sensitivity for filter
    print("Coupling capacitor sensitivity analysis:")
    print("For 3rd order Chebyshev filter:")
    
    sensitivities = [
        ("Center frequency", "Moderate", "±10% cap → ±5% freq shift"),
        ("Bandwidth", "High", "±10% coupling → ±15% bandwidth"),
        ("Ripple", "Very high", "±10% coupling → ripple distortion"),
        ("Return loss", "High", "Matching degrades with coupling errors"),
    ]
    
    for param, sensitivity, impact in sensitivities:
        print(f"  {param:<18} {sensitivity:<12} {impact}")
    
    print("\n5. PRACTICAL RECOMMENDATIONS BY SYSTEM IMPEDANCE:")
    print("-" * 50)
    
    recommendations = [
        ("50-100Ω systems", "Use chip capacitors", "Large values, less sensitive"),
        ("200Ω systems", "Hybrid PCB+chip", "5-10pF PCB trimming works well"),
        ("300-500Ω systems", "Consider all-chip", "Variations too critical for PCB-only"),
        ("All systems", "Add tuning options", "Series/parallel trim caps"),
    ]
    
    for system, recommendation, reason in recommendations:
        print(f"  {system:<18} {recommendation:<20} {reason}")
    
    return strategies

def calculate_filter_sensitivity_analysis(nominal_coupling_pF):
    """
    Analyze how PCB capacitor variations affect filter performance.
    """
    print(f"\n" + "=" * 80)
    print(f"FILTER SENSITIVITY ANALYSIS FOR {nominal_coupling_pF} pF COUPLING")
    print("=" * 80)
    
    # Variation scenarios
    scenarios = [
        ("Best case", -15.0, "Dry, cold, tight tolerance batch"),
        ("Nominal", 0.0, "Room temp, 50% RH, typical batch"),
        ("Worst case", +25.0, "Hot, humid, loose tolerance batch"),
    ]
    
    print(f"{'Scenario':<15} {'Coupling':<12} {'Freq Shift':<12} {'BW Change':<12} {'Impact'}")
    print("-" * 75)
    
    for scenario, var_pct, description in scenarios:
        actual_coupling = nominal_coupling_pF * (1 + var_pct/100)
        freq_shift_pct = -var_pct * 0.5  # Approximate
        bw_change_pct = var_pct * 1.5    # More sensitive
        
        if abs(var_pct) < 5:
            impact = "Acceptable"
        elif abs(var_pct) < 15:
            impact = "Marginal"
        else:
            impact = "Poor"
            
        print(f"{scenario:<15} {actual_coupling:<6.1f} pF    {freq_shift_pct:+5.1f}%     {bw_change_pct:+6.1f}%     {impact}")
    
    print(f"\nCRITICAL INSIGHT:")
    print(f"• {nominal_coupling_pF} pF coupling caps are {'CRITICAL' if nominal_coupling_pF < 15 else 'MODERATE'} to variations")
    print(f"• Environmental variations can cause significant filter degradation")
    print(f"• Manufacturing control becomes essential for small coupling values")
    
    # Recommend mitigation
    if nominal_coupling_pF < 10:
        print(f"\nRECOMMENDATION for {nominal_coupling_pF} pF:")
        print("• Use controlled-impedance PCB with Rogers material")
        print("• Specify ±5% εr tolerance")
        print("• Add environmental testing to verification")
        print("• Consider tunable elements for production adjustment")
    else:
        print(f"\nRECOMMENDATION for {nominal_coupling_pF} pF:")
        print("• Standard FR4 acceptable with good design practices")
        print("• Use hybrid PCB+chip approach for fine tuning")
        print("• Guard rings and controlled layout important")

def environmental_test_plan():
    """
    Provide test plan for characterizing PCB capacitors across environmental conditions.
    """
    print(f"\n" + "=" * 80)
    print("PCB CAPACITOR CHARACTERIZATION TEST PLAN")
    print("=" * 80)
    
    print("\n1. TEST STRUCTURE DESIGN:")
    print("-" * 50)
    print("Include on every PCB:")
    test_structures = [
        ("Parallel plate caps", "5, 10, 20 pF", "Different sizes"),
        ("Interdigital caps", "1, 2, 5 pF", "Different finger counts"),
        ("Edge coupling", "0.5, 1, 2 pF", "Different trace lengths"),
        ("Reference resistors", "50Ω, 100Ω", "Process monitoring"),
    ]
    
    for structure, values, purpose in test_structures:
        print(f"  • {structure:<20} {values:<15} ({purpose})")
    
    print("\n2. MEASUREMENT PROTOCOL:")
    print("-" * 50)
    measurements = [
        ("As-received", "Measure baseline", "Network analyzer S11"),
        ("After bake (125°C, 4h)", "Moisture removal", "Compare to baseline"),
        ("Temperature sweep", "-40°C to +85°C", "10°C steps, 30min soak"),
        ("Humidity aging", "85°C/85% RH, 168h", "JEDEC standard"),
        ("Thermal cycling", "100 cycles -40/+85°C", "Mechanical stress"),
    ]
    
    for test, condition, method in measurements:
        print(f"  • {test:<20} {condition:<20} ({method})")
    
    print("\n3. EXPECTED RESULTS & ACCEPTANCE:")
    print("-" * 50)
    
    acceptance = [
        ("Initial tolerance", "±15%", "Includes all manufacturing variation"),
        ("Temperature drift", "±10%", "Over full temperature range"),
        ("Humidity change", "±5%", "After 168h at 85/85"),
        ("Long-term stability", "±3%", "After thermal cycling"),
    ]
    
    for parameter, limit, condition in acceptance:
        print(f"  • {parameter:<20} {limit:<10} {condition}")
    
    print(f"\n4. PRODUCTION MONITORING:")
    print("-" * 50)
    print("  • Measure test structures on every panel")
    print("  • Plot control charts for process monitoring") 
    print("  • Flag batches outside ±10% from nominal")
    print("  • Archive data for traceability")
    print("  • Correlate with PCB supplier's εr measurements")

def calculate_q_factor_comparison(f_MHz, C_pF):
    """
    Compare Q factors of PCB vs discrete capacitors.
    """
    omega = 2 * math.pi * f_MHz * 1e6
    X_c = 1 / (omega * C_pF * 1e-12)
    
    print(f"\nQ FACTOR COMPARISON at {f_MHz} MHz, {C_pF} pF")
    print("-" * 60)
    
    # Typical loss tangents
    q_data = [
        ("PCB FR4", 0.02, 50),        # tan δ = 0.02 typical for FR4
        ("PCB Rogers", 0.002, 500),   # Low-loss PCB material
        ("NP0 Ceramic", 0.001, 1000), # High-Q ceramic
        ("X7R Ceramic", 0.025, 40),   # Lower Q ceramic
    ]
    
    print(f"{'Type':<15} {'Loss Tangent':<15} {'Q Factor':<10} {'ESR (Ω)'}")
    print("-" * 60)
    
    for typ, tan_delta, q in q_data:
        esr = X_c / q
        print(f"{typ:<15} {tan_delta:<15.3f} {q:<10} {esr:<.2f}")
    
    print("\nKEY INSIGHT: PCB capacitors have moderate Q (~50)")
    print("Acceptable for coupling but not for high-Q tank circuits.")

def design_guard_ring(cap_pF, guard_spacing_mm=0.5):
    """
    Design guard ring to shield PCB capacitor from external fields.
    """
    print(f"\nGUARD RING DESIGN for {cap_pF} pF capacitor")
    print("-" * 60)
    
    # Estimate capacitor dimensions
    if cap_pF < 5:
        cap_size_mm = 5
    elif cap_pF < 20:
        cap_size_mm = 10
    else:
        cap_size_mm = 15
    
    guard_outer_mm = cap_size_mm + 2 * guard_spacing_mm
    
    print(f"Capacitor area: {cap_size_mm}×{cap_size_mm} mm")
    print(f"Guard spacing: {guard_spacing_mm} mm")
    print(f"Guard ring outer: {guard_outer_mm}×{guard_outer_mm} mm")
    print("\nGuard ring connections:")
    print("  - Connect to GND for shielding")
    print("  - Use vias every λ/20 (every 5mm at 15MHz)")
    print("  - Keep symmetrical to avoid coupling imbalance")
    
    # Calculate parasitic to guard
    edge_length = 4 * cap_size_mm  # Perimeter
    parasitic_pF = calculate_edge_capacitance(edge_length, guard_spacing_mm, 0.5)
    print(f"\nEstimated parasitic to guard: {parasitic_pF:.2f} pF")
    print(f"This adds to tank capacitance - account for it!")

def generate_design_files(design_params, filename_base="pcb_cap"):
    """
    Generate KiCad footprint for PCB capacitor.
    """
    if design_params["method"] == "parallel_plate":
        kicad_footprint = f"""
(module PCB_CAP_{design_params['capacitance_pF']:.1f}pF (layer F.Cu)
  (descr "PCB Parallel Plate Capacitor {design_params['capacitance_pF']:.1f}pF")
  (fp_text reference C? (at 0 -5) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
  (fp_text value {design_params['capacitance_pF']:.1f}pF (at 0 5) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))
  
  # Top plate
  (pad 1 smd rect (at 0 0) (size {design_params['area_mm2']**0.5:.1f} {design_params['area_mm2']**0.5:.1f}) (layers F.Cu F.Paste F.Mask))
  
  # Bottom plate (connected through via)
  (pad 2 thru_hole circle (at {design_params['area_mm2']**0.5/2 + 1:.1f} 0) (size 0.8 0.8) (drill 0.4) (layers *.Cu *.Mask))
  
  # Note: Bottom plate on B.Cu layer must be added manually
  # Size: {design_params['area_mm2']**0.5:.1f} × {design_params['area_mm2']**0.5:.1f} mm
)
"""
        print(f"\nKiCad footprint generated: {filename_base}.kicad_mod")
        print("Remember to:")
        print("1. Add matching pad on bottom layer")
        print("2. Align precisely for correct capacitance")
        print("3. Keep dielectric uniform (no vias in capacitor area)")
        
        return kicad_footprint
    
    return None

# Main calculation example
if __name__ == "__main__":
    print("=" * 80)
    print("PCB CAPACITOR DESIGN FOR RF FILTERS")
    print("=" * 80)
    
    # Example: Design coupling capacitors for different system impedances
    print("\nCOUPLING CAPACITOR DESIGNS FOR 15.8 MHz FILTER:")
    print("-" * 60)
    
    test_cases = [
        (500, 8.0, "500Ω system - tiny coupling"),
        (300, 13.4, "300Ω system - small coupling"),  
        (200, 20.1, "200Ω system - moderate coupling"),
        (100, 40.2, "100Ω system - larger coupling"),
    ]
    
    for z_sys, c_coup, description in test_cases:
        print(f"\n{description}")
        calculate_pcb_coupling_network(z_sys, c_coup, 15.8)
    
    # Environmental stability analysis
    analyze_environmental_stability()
    
    # Q factor comparison
    calculate_q_factor_comparison(15.8, 10)
    
    # Guard ring design
    design_guard_ring(8.0)
    
    # Mitigation strategies
    mitigation_strategies()
    
    # Filter sensitivity analysis
    calculate_filter_sensitivity_analysis(8.0)  # High-Z system example
    
    # Environmental test plan
    environmental_test_plan()
    
    # Example PCB capacitor designs
    print("\n" + "=" * 80)
    print("SPECIFIC PCB CAPACITOR DESIGNS")
    print("=" * 80)
    
    # Design a 5pF coupling capacitor
    print("\nDesigning 5pF coupling capacitor:")
    designs = design_pcb_capacitor(5.0, method="all")
    for design in designs[:3]:
        print(f"\n{design['method']}:")
        print(f"  {design['dimensions']}")
        print(f"  Tolerance: {design['tolerance']}")
    
    # Design a trimming capacitor
    print("\nDesigning 2pF trimming capacitor:")
    designs = design_pcb_capacitor(2.0, method="all")
    for design in designs[:3]:
        print(f"\n{design['method']}:")
        print(f"  {design['dimensions']}")
    
    print("\n" + "=" * 80)
    print("PCB LAYOUT BEST PRACTICES FOR FILTER CAPACITORS:")
    print("-" * 80)
    print("1. Use controlled stackup (specify dielectric thickness)")
    print("2. Keep critical capacitors away from board edges")
    print("3. Use guard rings for isolation")
    print("4. Place on inner layers for better shielding")
    print("5. Avoid vias in capacitor area (changes dielectric)")
    print("6. Consider thermal expansion matching")
    print("7. Use test coupons for characterization")
    print("8. Account for soldermask effects (adds ~5% typically)")
    print("\nFor production:")
    print("• Measure actual εr of your PCB batch")
    print("• Include test structures on panel")
    print("• Use network analyzer for verification")
    print("• Temperature cycle to verify stability")