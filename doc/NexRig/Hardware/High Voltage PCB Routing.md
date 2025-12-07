The transition to an 80V DC rail and high-impedance RF domains (where voltage peaks can exceed 500V) requires specific PCB layout rules to prevent arcing, dielectric breakdown, and carbon tracking.

The following rules apply to your **Veer Supply Output (80V DC)**, **PA H-Bridge Output**, and **Tuner/Filter High-Z sections (RF HV)**.

### 1. Clearance & Creepage Rules

Voltage breakdown is determined by the spacing between conductors. We must adhere to **IPC-2221B** standards for high reliability.

**Definitions:**

- **Clearance:** The shortest distance through _air_.
- **Creepage:** The shortest distance along the _surface_ of the insulation.

#### A. 80V DC Rail (Veer Output)

For the 0-80V DC domain, the risk is low but constant.

- **External Layers (Air/Mask):** **0.6 mm (24 mils)** minimum.
    - _Why:_ Standard IPC for up to 100V is smaller (0.13mm), but 0.6mm provides a safety factor against dust accumulation and solder mask imperfections.
- **Internal Layers (FR4):** **0.25 mm (10 mils)** minimum.
    - _Why:_ FR4 has excellent dielectric strength (~500V/mil), but manufacturing defects (voids) require margin.

#### B. RF High-Voltage (Tuner & Filter Capacitors)

In the 200Ω domain at 100W, voltages nominally hit 141V peak. In the Tuner, high-Q resonance can spike voltages to **>800V**.

- **External Layers (Critical):** **1.5 mm (60 mils)** minimum clearance.
    - _Why:_ RF energy can arc more easily than DC due to ionization potential at sharp points. 1.5mm prevents arcing across component pads even if the solder mask is scratched.
- **Internal Layers:** **0.5 mm (20 mils)** minimum.
- **Board Edge:** Keep HV traces at least **2.0 mm** from the PCB edge to prevent arcing to the chassis.

### 2. Layer Stack & Reference Planes (The "Canyon" Strategy)

High voltage traces on inner layers are safer from arcing but suffer from capacitance. High voltage traces on outer layers are better for capacitance but prone to surface arcing.

**Rule:** Route High-Z RF HV on **External Layers (Top/Bottom)** whenever possible.

#### The "Canyon" Voiding Rule (Crucial for 200Ω Domain)

To minimize parasitic capacitance and prevent dielectric breakdown to the ground plane:

1. **Identify the HV Trace:** (e.g., The trace connecting the Tuner L and C banks).
2. **Void L2 (GND):** Do **not** place a solid ground plane directly under this trace on Layer 2.
3. **Void L3/L4:** Remove copper on intermediate layers.
4. **Reference L5 or Chassis:** Let the trace reference a deeper ground plane (like Layer 5 or 6) to increase the dielectric thickness ($d$).
    - _Impact:_ Capacitance $C \propto A/d$. Doubling the distance ($d$) halves the parasitic capacitance, preserving filter Q-factor.

### 3. Trace Geometry & Shape

Sharp corners concentrate electric fields (E-fields), becoming launch points for arcs (Corona discharge).

- **No 90° Bends:** All HV traces must use **45° miters** or, ideally, **curved routing**.
- **Teardrops:** Use teardrops on all pads connecting to HV traces. This smooths the transition from the thin trace to the wide pad, reducing E-field stress.
- **Polygon Pours:** If using a copper pour for HV (e.g., the drain node of the H-Bridge):
    - Set **Corner Smoothing / Radius** to at least 0.5mm.
    - Do not leave "dead copper" islands near HV nets; they can float up in potential and arc.

### 4. Component Placement & Slots

#### A. Milling Slots (Isolation)

For areas with extreme voltage differentials (e.g., across the contacts of the Tuner Relays or the primary/secondary of the PA transformer):

- **Rule:** Place a **milled slot (air gap)** between the high-voltage pins and the ground/control pins.
- **Width:** 1.0 mm to 2.0 mm wide slot.
- **Benefit:** This forces the arc to travel through air (Clearance) rather than along the PCB surface (Creepage), effectively doubling the isolation voltage rating of the gap.

#### B. Solder Mask

- **Do NOT rely on Solder Mask:** Solder mask is not considered a reliable insulator by safety standards (it can pinhole or scratch). Design your clearances as if the mask does not exist.
- **Mask Dam:** Ensure there is a solder mask dam between HV pads to prevent solder bridging, which drastically reduces clearance.

### Summary Table for KiCad Setup

|**Domain**|**Voltage (Peak)**|**Clearance (Outer)**|**Clearance (Inner)**|**Trace Width**|**GND Plane**|
|---|---|---|---|---|---|
|**Veer DC**|80V|0.6 mm|0.25 mm|>1.5 mm (Current)|Solid L2|
|**PA Output**|80V + Ringing|0.8 mm|0.3 mm|Polygon Pour|Solid L2|
|**Filter (200Ω)**|~200V|1.0 mm|0.4 mm|0.4 mm|Void L2 (Ref L3)|
|**Tuner (High-Z)**|>800V|**2.0 mm**|**0.8 mm**|0.5 mm|Void L2-L4|

Use the **Net Class** feature in KiCad to assign these specific clearance rules to the `Net_Veer_Out`, `Net_PA_Drain`, and `Net_Tuner_HighZ` nets to automate the DRC checks.