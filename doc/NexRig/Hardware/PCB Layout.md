# PCB Layout and Routing Constraints
This document outlines the rules and specific dimensions for PCB layout based on the NexRig architecture. All dimensions are in millimeters unless otherwise noted.
1. Stackup and Layer Use
The design uses a 6-Layer Stackup.

| Layer | Type | General Use | RF/Control Function |
|---|---|---|---|
| L1 | F.Cu | Primary Component, RF | 50Ω, 200Ω, 800Ω Signals, H-Bridge |
| L2 | In1.Cu.gnd | Solid Ground Plane | Reference for L1 (50Ω), Voided for High-Z/High-Power |
| L3 | In2.Cu | Signal / Reference | 200Ω Reference (via L2 cutout), Control Signals |
| L4 | In3.Cu.pwr | Power Rails | EER/Veer Supply, +3.3V, +5V |
| L5 | In4.Cu.gnd | Solid Ground Plane | Reference for L6, Robust Shield for L1/L6 isolation |
| L6 | B.Cu | Control Signals | RMII, SPI, Logic Signals, External Shield |
2. Impedance Domain Routing
All traces must be routed as transmission lines referencing the layer specified below.
A. 50Ω Traces (Standard)
 * Use: RMII, Input/Output Ports, Low-power RF Interconnects.
 * Reference: L2 (In1.Cu.gnd).
 * Trace Width (L1/L6): 0.16 mm (approx. 6.3 mils).
B. 200Ω Traces (LPF/PA Tank)
The 200Ω impedance domain operates at 0.5 A RMS and 100 V RMS nominal.
 * Goal: Minimize parasitic capacitance and handle current.
 * Trace Width: 0.40 mm (16 mils). This handles the required current load and minimizes resistive loss.
 * Reference & Canyon: L3 (In2.Cu). The L2 Ground Plane MUST be voided (cut out) directly underneath the 200Ω signal path to increase the distance to ground and reduce parasitic capacitance.
C. 800Ω Traces (RX Preselector)
The 800Ω domain is extremely sensitive to parasitic capacitance (C_p) and is not routed as a controlled transmission line.
 * Goal: Absolute minimum C_p (reduce detuning).
 * Trace Width: 0.2 mm (8 mils).
 * The Canyon Strategy (Full Void):
   * L2, L3, L4: MUST BE VOIDED under the 800Ω signal trace.
   * Reference: L5 (In4.Cu.gnd). The L5 plane provides the final continuous ground reference and shield.
   * Cutout Size: The rule area (canyon) must extend at least 1.0 mm to 1.5 mm on either side of the 0.2 mm trace (total width \approx 2.2 \text{ mm} to 3.2 \text{ mm}) to minimize fringing fields.
3. Magnetics and Coupling Prevention
A. Toroid Spacing (Bruene & Output Transformers)
 * Toroids: Dual-stacked FT140 cores.
 * Orientation: All critical, high-power toroids must be oriented with their magnetic axes perpendicular (90 degrees) to the nearest magnetic component.
 * Minimum Spacing: Maintain a minimum distance of 1.5 inches (38 mm) edge-to-edge between the Bruene Coupler and the 200Ω-to-50Ω Output Transformer to preserve the coupler's directivity.
B. LPF Inductor Isolation (RX Preselector)
 * Inductors: Coilcraft 0805CS series (unshielded).
 * Arrangement: Inductors must be placed in a single row with 90-degree rotation between adjacent parts (e.g., L1 vertical, L2 horizontal, L3 vertical).
 * Minimum Pitch: Maintain a minimum center-to-center pitch of 4.0 mm (8.0 mm between same-orientation neighbors) to prevent mutual inductance from shifting the filter's frequency response.
 * Relays: Keep ferrous components (like the TQ2-5V relay) away from the main flux path of the center toroids (i.e., not looking down the hole/axis).
4. Design for Manufacturing (DFM) and Components
A. Via Specifications
 * Standard Signal Via (Cost-Effective): 0.3 mm Hole / 0.6 mm Pad Diameter. This is the standard minimum plated through-hole size.
 * GND Stitching Vias: Place GND vias adjacent (within 1-2 mm) to signal vias when traces transition between Layer 1 (Ref L2) and Layer 6 (Ref L5) to maintain a tight return path loop.
B. QFP144 Routing and Clearance
 * Heel Routing: Acceptable to route from the inner heel of a QFP144 pad underneath the package body to connect to opposite pins, provided there is no Exposed Thermal Pad (E-Pad) in the center.
 * Trace Width: When traces enter any QFP pad, they must be necked down to the pad width for the last \mathbf{0.25 \text{ mm}} to mitigate thermal sinking and prevent component skewing during reflow.
C. Shunt Resistor (Kelvin Pads)
 * The 4-pad Kelvin shunt resistor footprint (e.g., R2021) must be modified to prevent DRC errors:
   * Change the Pad Number of the Force and Sense pads on the same side to match (e.g., Pin 1 and Pin 2 both become "1").
   * This merges them into the same net and removes the unnecessary clearance violation, allowing the sense trace to be routed from the narrow pad.
D. Digital Signals (RMII)
 * 10mm Break: Breaks in differential coupling (e.g., 10 mm separation) for 100Base-TX (50 MHz) are acceptable due to the signal's slow rise time.
 * Solid Reference: The most critical requirement is maintaining a solid ground plane (L2 or L5) underneath the trace, even when the traces separate.