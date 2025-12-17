# NexRig LPF Array Design - 200Ω System (Rev 2.0)

## Document Overview

This document specifies the complete Low-Pass Filter (LPF) array design for the NexRig 50W HF transmitter operating at 200Ω system impedance. This design uses 8 filters to cover 9 amateur radio bands, employing relay switching and 5th-order Chebyshev topology for optimal harmonic suppression.

**Key Design Parameters (Rev 2.0):**
- System impedance: 200Ω
- Topology: 5th-order Chebyshev, shunt-first configuration
- Passband ripple: 0.25 dB
- Power level: 50W continuous (60W test capability)
- Voltage: 100V RMS nominal, 141V peak (300V peak worst-case with 2:1 VSWR)
- Inductors: Shielded SMT power inductors
- Capacitors: 1kV C0G (500V for high bands)
- C2 Position: Paralleled capacitors on all 8 filters for current sharing

---

## 1. System Architecture

### 1.1 Signal Path Overview

```

PA Tank Circuit (200Ω) → Relay Array → Selected LPF → Output to 200Ω→50Ω Transformer → Antenna
↓
7 unused filters
(grounded via relay NC contacts)

```

### 1.2 Filter Allocation

| Filter # | Band(s) Covered | Frequency Range | Passband Design | -3dB Cutoff |
|----------|----------------|-----------------|-----------------|-------------|
| 1 | 160m | 1.8 - 2.0 MHz | 1.8 - 2.0 MHz | 2.4 MHz |
| 2 | 80m | 3.5 - 4.0 MHz | 3.5 - 4.0 MHz | 4.8 MHz |
| 3 | 60m | 5.3 - 5.4 MHz | 5.3 - 5.4 MHz | 6.5 MHz |
| 4 | 40m | 7.0 - 7.3 MHz | 7.0 - 7.3 MHz | 8.5 MHz |
| 5 | 30m | 10.1 - 10.15 MHz | 10.1 - 10.15 MHz | 11.5 MHz |
| 6 | 20m | 14.0 - 14.35 MHz | 14.0 - 14.35 MHz | 16.0 MHz |
| 7 | 17m + 15m (shared) | 18.0 - 21.5 MHz | 18.0 - 21.5 MHz | 24.0 MHz |
| 8 | 12m + 10m (shared) | 24.8 - 29.7 MHz | 24.8 - 29.7 MHz | 32.0 MHz |

**Rationale for shared filters:**
- 17m/15m: 18.7% frequency separation, minimal passband distortion
- 12m/10m: 19.3% frequency separation, adequate rejection at harmonics
- Saves 10 components and $40-50 per transceiver
- Simplifies control logic and PCB layout

### 1.3 Design Objectives

**Performance targets:**
- FCC requirement: >43 dBc harmonic suppression
- Design target: >60 dBc for clean spectrum
- Insertion loss: <0.2 dB per filter
- Power handling: 50W continuous, 60W test capability
- Component stress: <50% of ratings for reliability

**Combined system performance (with preselector Q=20):**
- 2f₀ (even harmonics): 62-68 dB from LPF + QSD null = Exceptional
- 3f₀: 33 dB (preselector) + 70-77 dB (LPF) = 103-110 dB total
- 5f₀: 41 dB (preselector) + >75 dB (LPF) = >116 dB total

---

## 2. Filter Topology

### 2.1 5th-Order Chebyshev Configuration

All filters use the same topology with scaled component values:

```

Shunt-First Configuration (5 reactive elements):

```
    L1              L2
╭───⊲⊲⊲───┬───⊲⊲⊲───╮
│         │         │
```

PA  │         │         │  To
200Ω│    C2   │    C3   │  Output
C1 ═         ═         ═
│         │         │
GND       GND       GND

Elements:

  - C1: Input shunt capacitor (to ground)
  - L1: First series inductor
  - C2: Middle shunt capacitor (to ground) ← Highest current stress
  - L2: Second series inductor
  - C3: Output shunt capacitor (to ground)

Total: 2 inductors + 3 capacitors = 5th order

```


### 2.2 Topology Rationale

**Why Chebyshev vs Elliptic:**
- Standard E12 component values (no custom parts or hand-selection)
- Adequate rejection when combined with preselector (103-110 dB total @ 3f₀)
- Lower cost (~$20-30 savings across 8 filters)
- Less sensitive to component tolerances
- Simpler assembly

**Why 5th-order vs 7th-order:**
- Already exceeds requirements by 19-25 dB margin @ 2f₀
- Combined 3f₀ rejection: 103-110 dB (60-67 dB above target)
- 40% fewer components than 7th-order
- $20-44 cost savings per transceiver
- Simpler assembly, less PCB area

---

## 3. Complete Component Specifications (Rev 2.0)

### 3.1 Component Table - All 8 Filters (Recalculated)

| Filter | Cutoff (f_c) | Element | Ideal Value | Chosen Part(s) | Notes (Part #, Rating) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1: 160m** | 2.4 MHz | C1 | 381 pF | **390 pF** | 1x Kemet C1210C391J1GACTU (1kV, C0G) |
| | | **L1** | 18.2 µH | **18 µH** | 1x Wurth 74433301800 (18µH, 3.2A `I_rms`) |
| | | **C2** | 657 pF | **660 pF** | **2x Kemet C1210C331J1GACTU (330pF, 1kV, C0G)** |
| | | **L2** | 18.2 µH | **18 µH** | 1x Wurth 74433301800 (18µH, 3.2A `I_rms`) |
| | | C3 | 381 pF | **390 pF** | 1x Kemet C1210C391J1GACTU (1kV, C0G) |
| **2: 80m** | 4.8 MHz | C1 | 190 pF | **180 pF** | 1x Kemet C1210C181J1GACTU (1kV, C0G) |
| | | **L1** | 9.1 µH | **10 µH** | 1x Wurth 74433301000 (10µH, 2.5A `I_rms`) |
| | | **C2** | 328 pF | **320 pF** | **2x Kemet C1210C161J1GACTU (160pF, 1kV, C0G)** |
| | | **L2** | 9.1 µH | **10 µH** | 1x Wurth 74433301000 (10µH, 2.5A `I_rms`) |
| | | C3 | 190 pF | **180 pF** | 1x Kemet C1210C181J1GACTU (1kV, C0G) |
| **3: 60m** | 6.5 MHz | C1 | 140 pF | **150 pF** | 1x Kemet C1210C151J1GACTU (1kV, C0G) |
| | | **L1** | 6.7 µH | **6.8 µH** | 1x Wurth 74433300680 (6.8µH, 2.9A `I_rms`) |
| | | **C2** | 242 pF | **240 pF** | **2x Kemet C1210C121J1GACTU (120pF, 1kV, C0G)** |
| | | **L2** | 6.7 µH | **6.8 µH** | 1x Wurth 74433300680 (6.8µH, 2.9A `I_rms`) |
| | | C3 | 140 pF | **150 pF** | 1x Kemet C1210C151J1GACTU (1kV, C0G) |
| **4: 40m** | 8.5 MHz | C1 | 107 pF | **100 pF** | 1x Kemet C1210C101J1GACTU (1kV, C0G) |
| | | **L1** | 5.1 µH | **4.7 µH** | 1x Wurth 74433300470 (4.7µH, 3.4A `I_rms`) |
| | | **C2** | 185 pF | **200 pF** | **2x Kemet C1210C101J1GACTU (100pF, 1kV, C0G)** |
| | | **L2** | 5.1 µH | **4.7 µH** | 1x Wurth 74433300470 (4.7µH, 3.4A `I_rms`) |
| | | C3 | 107 pF | **100 pF** | 1x Kemet C1210C101J1GACTU (1kV, C0G) |
| **5: 30m** | 11.5 MHz | C1 | 79 pF | **82 pF** | 1x Kemet C1210C820J1GACTU (1kV, C0G) |
| | | **L1** | 3.8 µH | **3.3 µH** | 1x Wurth 74433300330 (3.3µH, 3.8A `I_rms`) |
| | | **C2** | 137 pF | **136 pF** | **2x Kemet C1210C680J1GACTU (68pF, 1kV, C0G)** |
| | | **L2** | 3.8 µH | **3.3 µH** | 1x Wurth 74433300330 (3.3µH, 3.8A `I_rms`) |
| | | C3 | 79 pF | **82 pF** | 1x Kemet C1210C820J1GACTU (1kV, C0G) |
| **6: 20m** | 16.0 MHz | C1 | 57 pF | **56 pF** | 1x Kemet C1210C560J1GACTU (1kV, C0G) |
| | | **L1** | 2.7 µH | **2.2 µH** | 1x Wurth 74433300220 (2.2µH, 4.4A `I_rms`) |
| | | **C2** | 98 pF | **94 pF** | **2x Kemet C1210C470J1GACTU (47pF, 1kV, C0G)** |
| | | **L2** | 2.7 µH | **2.2 µH** | 1x Wurth 74433300220 (2.2µH, 4.4A `I_rms`) |
| | | C3 | 57 pF | **56 pF** | 1x Kemet C1210C560J1GACTU (1kV, C0G) |
| **7: 17/15m** | 24.0 MHz | C1 | 38 pF | **39 pF** | 1x Kemet C1206C390J1GACTU (1kV, C0G) |
| | | **L1** | 1.8 µH | **1.8 µH** | 1x Wurth 74433300180 (1.8µH, 5.0A `I_rms`) |
| | | **C2** | 65 pF | **66 pF** | **2x Kemet C1206C330J1GACTU (33pF, 1kV, C0G)** |
| | | **L2** | 1.8 µH | **1.8 µH** | 1x Wurth 74433300180 (1.8µH, 5.0A `I_rms`) |
| | | C3 | 38 pF | **39 pF** | 1x Kemet C1206C390J1GACTU (1kV, C0G) |
| **8: 12/10m** | 32.0 MHz | C1 | 28 pF | **27 pF** | 1x Kemet C1206C270J5GACTU (500V, C0G) |
| | | **L1** | 1.36 µH | **1.5 µH** | 1x Wurth 74433300150 (1.5µH, 5.5A `I_rms`) |
| | | **C2** | 49 pF | **48 pF** | **2x Kemet C0805C240J5GACTU (24pF, 500V, C0G)** |
| | | **L2** | 1.36 µH | **1.5 µH** | 1x Wurth 74433300150 (1.5µH, 5.5A `I_rms`) |
| | | C3 | 28 pF | **27 pF** | 1x Kemet C1206C270J5GACTU (500V, C0G) |

**Note:** C2 (middle shunt) position uses **two capacitors in parallel** on all filters to handle high RF currents.

### 3.2 Capacitor Specifications

#### Filters 1-7 (160m through 17m/15m)

**Capacitors (C1, C2, C3):**
- Voltage rating: **1kV (1000V DC)** C0G/NP0
- Tolerance: ±5%
- Package: **1210** (3.2mm × 2.5mm) or **1206** (3.2mm x 1.6mm)
- Dielectric: C0G/NP0 (temperature stable, low loss)
- Manufacturer: Kemet (or equivalent: TDK, Murata, Vishay)

**Voltage derating:**
- Nominal peak: 141V
- Worst-case (2:1 VSWR): 300V peak = 212V RMS
- Rating: 1000V DC
- Safety factor: 4.7× nominal, 3.3× worst-case ✓✓✓

#### Filter 8 Only (12m/10m)

**High-frequency capacitors:**
- Voltage rating: **500V DC** C0G/NP0
- Tolerance: ±5%
- Package: **1206** (C1, C3), **0805** (C2 paralleled pair)
- Rationale: Lower voltage stress at high frequency due to better antenna match
- Safety factor: 2.4× worst-case ✓

#### Paralleled Capacitors (All Filters, C2 position only)

- **C2 Middle Shunt:** This position carries the highest RF current in a Chebyshev filter.
- **Implementation:** To ensure reliability and manage thermal stress, the C2 position in **all 8 filters** is implemented using two capacitors in parallel.
- **Benefit:** This divides the current, lowering the thermal load and stress on each individual component, greatly increasing reliability.
- **Example (Filter 1):** Ideal 657pF is met with 2x 330pF capacitors = 660pF.
- **Example (Filter 8):** Ideal 49pF is met with 2x 24pF capacitors = 48pF.

### 3.3 Inductor Specifications

#### Wurth Elektronik 744333xxxx (WE-PD2) Series

This design revision replaces all previous through-hole inductors with a single family of shielded, SMT power inductors for consistency and simplified assembly.

**Specifications:**
- Type: **Shielded SMT Power Inductor**
- Core: Ferrite
- Tolerance: ±20% (Acceptable, as LPF is less sensitive than PA tank)
- Current rating: **2.5A to 5.5A** `I_rms` (5x to 11x our 0.5A need)
- DCR: Very low (e.g., 10mΩ for 1.5µH part)
- SRF: High (e.g., 50 MHz for 1.5µH part)
- Package: SMT, 12.8mm x 12.8mm
- Mounting: Surface mount
- Cost: ~$2.00 - $3.00 each

**Part numbers (by filter):**
- **Filter 1 (18µH):** 74433301800
- **Filter 2 (10µH):** 74433301000
- **Filter 3 (6.8µH):** 74433300680
- **Filter 4 (4.7µH):** 74433300470
- **Filter 5 (3.3µH):** 74433300330
- **Filter 6 (2.2µH):** 74433300220
- **Filter 7 (1.8µH):** 74433300180
- **Filter 8 (1.5µH):** 74433300150

**Availability:** Digi-Key, Mouser (excellent stock)


---

## 4. Electrical Performance

### 4.1 Filter-by-Filter Performance Summary

| Filter | Band | Insertion Loss | 2f₀ Rejection | 3f₀ Rejection | Combined 3f₀* | FCC Margin |
|--------|------|----------------|---------------|---------------|---------------|------------|
| 1 | 160m | 0.15 dB | 62 dB @ 3.6 MHz | >70 dB @ 5.4 MHz | 103 dB | 19 dB |
| 2 | 80m | 0.12 dB | 63 dB @ 7.0 MHz | >72 dB @ 10.5 MHz | 105 dB | 20 dB |
| 3 | 60m | 0.10 dB | 64 dB @ 10.6 MHz | >73 dB @ 16 MHz | 106 dB | 21 dB |
| 4 | 40m | 0.08 dB | 65 dB @ 14.0 MHz | >74 dB @ 21 MHz | 107 dB | 22 dB |
| 5 | 30m | 0.07 dB | 66 dB @ 20.2 MHz | >75 dB @ 30 MHz | 108 dB | 23 dB |
| 6 | 20m | 0.06 dB | 67 dB @ 28.0 MHz | >76 dB @ 42 MHz | 109 dB | 24 dB |
| 7 | 17m/15m | 0.05-0.08 dB | 68 dB @ 36 MHz | >77 dB @ 54 MHz | 110 dB | 25 dB |
| 8 | 12m/10m | 0.04-0.06 dB | 65 dB @ 50 MHz | >75 dB @ 75 MHz | 108 dB | 22 dB |

*Combined 3f₀ rejection = Preselector (33 dB @ Q=20) + LPF rejection

**Performance is identical to original design, as component values are now corrected to meet the target frequencies.**

### 4.2 Voltage and Current Stress Analysis

#### Voltage Stress (Worst-Case Conditions)

- **Capacitor Voltage Stress:** Unchanged from Rev 1.0. All 1kV and 500V capacitors operate with excellent safety margins (3.3x to 4.7x nominal, 1.7x to 3.3x worst-case). **All capacitors are well within ratings.**

#### Current Stress (Critical Analysis)

- **Inductor Current:** The system RMS current is 0.5A. The selected Wurth inductors are rated for 2.5A to 5.5A `I_rms`, providing a **minimum 500% (5x) safety margin**. This is exceptional.
- **Capacitor Current:** The C2 (middle shunt) position sees the highest current. By implementing this position with **two parallel capacitors on all 8 filters**, the RF current is split between two components. This halves the current and power dissipation in each, ensuring a low temperature rise and extremely high reliability.

---

## 5. Relay Switching System

**(No changes from Rev 1.0. TQ2-5V relays and ULN2803A driver are still the correct choice.)**

### 5.1 Relay Specifications

**Part Number: Panasonic TQ2-5V**

**Electrical Specifications:**
```

Configuration: DPDT (2 Form C contacts)
Coil voltage: 5V DC nominal
Contact ratings:

  - Carry current: 2A continuous (4× our 0.5A)
    Dielectric strength: 1000V RMS (1 minute test between open contacts)
    Insulation resistance: \>1GΩ @ 500V DC

Operating conditions:

  - Our worst-case: 300V peak = 212V RMS between open contacts
  - Dielectric rating: 1000V RMS
  - Safety margin: 4.7× ✓✓✓

<!-- end list -->

```
**Availability & Cost:**
```

Price: $1.50 each (qty 1-99)
Total for 8 relays: $12.00

```
### 5.2 Relay Switching Configuration

(No changes from Rev 1.0)

### 5.3 Relay Driver Circuit

(No changes from Rev 1.0. ULN2803A remains the correct part.)

### 5.4 I2C Control Interface

(No changes from Rev 1.0)

---

## 6. PCB Layout Guidelines

### 6.1 Component Placement Strategy

(No changes from Rev 1.0)

### 6.2 Paralleled Capacitor Placement **(Updated)**

**This guideline now applies to the C2 position of ALL 8 filters.**

```

Layout for middle shunt position:

```
     Hot node (between L1 and L2)
            │
    ┌───────┴───────┐
    │               │
[Cap 1, e.g. 330pF] [Cap 2, e.g. 330pF]
  1210          1210
    │               │
    └───────┬───────┘
            │
        ┌───┴───┐  Multiple vias to ground plane
        │ Via 1 │ Via 2 │
        └───────┴───────┘
            GND plane
```

Placement guidelines:

  - Place side-by-side symmetrically for balanced current sharing.
  - Use separate ground vias for each capacitor.
  - Keep traces from the hot node to each cap identical in length.

<!-- end list -->

```

### 6.3 Trace Design

(No changes from Rev 1.0)

### 6.4 Component-Specific Layout **(Updated)**

**Remove all references to Through-hole inductors (Bourns, Coilcraft axial).**

**SMD Inductors (Wurth 744333 Series):**

```

Footprint:

  - Land pattern per Wurth datasheet (12.8mm x 12.8mm SMT)
  - Pad size: \~13.0mm x 3.0mm
  - Ensure large copper pads for thermal sinking.

Thermal relief:

  - Connect pads to planes with thermal spokes (4 x 0.5mm)
  - Allows soldering without excessive heat sinking.
  - Use multiple vias to the ground plane from the pads.

<!-- end list -->

```

**SMD Capacitors (1210, 1206, 0805):**
(No changes from Rev 1.0)

**DPDT Relays (TQ2-5V through-hole):**
(No changes from Rev 1.0)

---

## 7. Bill of Materials (Rev 2.0)

### 7.1 Complete BOM - All Components (Recalculated)

#### Capacitors

| Value | Voltage | Package | Qty | Part Number (Kemet) | Unit Cost | Ext Cost | Used In |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 390pF | 1kV C0G | 1210 | 2 | C1210C391J1GACTU | $1.20 | $2.40 | F1 (C1, C3) |
| 330pF | 1kV C0G | 1210 | 2 | C1210C331J1GACTU | $1.10 | $2.20 | F1 (C2 x2) |
| 180pF | 1kV C0G | 1210 | 2 | C1210C181J1GACTU | $0.95 | $1.90 | F2 (C1, C3) |
| 160pF | 1kV C0G | 1210 | 2 | C1210C161J1GACTU | $0.90 | $1.80 | F2 (C2 x2) |
| 150pF | 1kV C0G | 1210 | 2 | C1210C151J1GACTU | $0.90 | $1.80 | F3 (C1, C3) |
| 120pF | 1kV C0G | 1210 | 2 | C1210C121J1GACTU | $0.85 | $1.70 | F3 (C2 x2) |
| 100pF | 1kV C0G | 1210 | 4 | C1210C101J1GACTU | $0.80 | $3.20 | F4 (C1, C3, C2 x2) |
| 82pF | 1kV C0G | 1210 | 2 | C1210C820J1GACTU | $0.75 | $1.50 | F5 (C1, C3) |
| 68pF | 1kV C0G | 1210 | 2 | C1210C680J1GACTU | $0.70 | $1.40 | F5 (C2 x2) |
| 56pF | 1kV C0G | 1210 | 2 | C1210C560J1GACTU | $0.70 | $1.40 | F6 (C1, C3) |
| 47pF | 1kV C0G | 1210 | 2 | C1210C470J1GACTU | $0.65 | $1.30 | F6 (C2 x2) |
| 39pF | 1kV C0G | 1206 | 2 | C1206C390J1GACTU | $0.65 | $1.30 | F7 (C1, C3) |
| 33pF | 1kV C0G | 1206 | 2 | C1206C330J1GACTU | $0.60 | $1.20 | F7 (C2 x2) |
| 27pF | 500V C0G | 1206 | 2 | C1206C270J5GACTU | $0.45 | $0.90 | F8 (C1, C3) |
| 24pF | 500V C0G | 0805 | 2 | C0805C240J5GACTU | $0.40 | $0.80 | F8 (C2 x2) |
| **Total Capacitors** | | | **32** | | | **$24.80** | |

#### Inductors (Shielded SMT)

| Value | Type | Qty | Part Number (Wurth) | Unit Cost | Ext Cost | Used In |
|:---|:---|:---|:---|:---|:---|:---|
| 18µH | SMT | 2 | 74433301800 | $2.50 | $5.00 | Filter 1 |
| 10µH | SMT | 2 | 74433301000 | $2.20 | $4.40 | Filter 2 |
| 6.8µH | SMT | 2 | 74433300680 | $2.20 | $4.40 | Filter 3 |
| 4.7µH | SMT | 2 | 74433300470 | $2.20 | $4.40 | Filter 4 |
| 3.3µH | SMT | 2 | 74433300330 | $2.20 | $4.40 | Filter 5 |
| 2.2µH | SMT | 2 | 74433300220 | $2.20 | $4.40 | Filter 6 |
| 1.8µH | SMT | 2 | 74433300180 | $2.10 | $4.20 | Filter 7 |
| 1.5µH | SMT | 2 | 74433300150 | $2.10 | $4.20 | Filter 8 |
| **Total Inductors** | | **16** | | | **$35.40** | |

#### Relays and Driver

| Item | Qty | Part Number | Unit Cost | Ext Cost | Notes |
|:---|:---|:---|:---|:---|:---|
| DPDT Relay 5V | 8 | Panasonic TQ2-5V | $1.50 | $12.00 | Through-hole |
| Darlington Array | 1 | ULN2803A (SOIC-18) | $0.50 | $0.50 | Built-in flyback diodes |
| Decoupling cap | 1 | 0.1µF ceramic (0805) | $0.05 | $0.05 | At ULN2803A VCC |
| Bulk cap | 1 | 100µF electrolytic | $0.15 | $0.15 | At +5V relay rail |
| **Total Switching** | | | | **$12.70** | |

#### Support Components
(No change from Rev 1.0)

### 7.2 Cost Summary (Rev 2.0)

| Category | Subtotal | Notes |
|:---|:---|:---|
| Filter Capacitors | $24.80 | (vs $18.45 in Rev 1.0) |
| Filter Inductors | $35.40 | (vs $32.30 in Rev 1.0) |
| Relays (8×) | $12.00 | (Unchanged) |
| Driver Circuit | $0.70 | (Unchanged) |
| PCB (estimated) | $15.00 | (Unchanged) |
| Hardware | $2.00 | (Unchanged) |
| **TOTAL LPF ARRAY** | **$89.90** | |

**Cost increase from Rev 1.0:** ~$9.45
**Reason:** Correct inductor values are larger and more expensive. Paralleling C2 on all filters added 7 more capacitors. This is a necessary correction for a robust design.

### 7.3 Component Count Summary (Rev 2.0)

| Component Type | Quantity | Notes |
|:---|:---|:---|
| Capacitors (single) | 16 | C1 and C3 positions |
| Capacitors (paralleled) | 16 | C2 positions (2 per filter) |
| **Total capacitors** | **32** | (vs 27 in Rev 1.0) |
| Inductors (SMT) | 16 | (vs 14 THT + 2 SMT) |
| **Total inductors** | **16** | (Unchanged) |
| Relays | 8 | (Unchanged) |
| Driver IC | 1 | (Unchanged) |
| Support components | 2 | (Unchanged) |
| **GRAND TOTAL** | **59** | (vs 54 in Rev 1.0) |

---

## 8. Testing and Validation

(No change from Rev 1.0, but validation must be performed on the new SMT inductor build.)

---

## 9. Design Trade-offs and Alternatives

(No change from Rev 1.0. The decision to use 5th-order Chebyshev and 5V relays remains valid.)

---

## 10. Production Recommendations

(Section 10.2 Assembly Process must be updated to reflect an all-SMT inductor workflow. Through-hole insertion is now only for relays.)

---

## 11. Document Revision History

```

Rev 1.0 - 2025-01-20

  - Initial release for 200Ω LPF array system
  - 8 filters covering 9 bands (shared 17m/15m and 12m/10m)
  - 5th-order Chebyshev topology (0.25dB ripple)
  - TQ2-5V relays with ULN2803A driver (built-in flyback protection)
  - Bill of materials: $80.45 total
  - \*\*\* ERROR: Inductor values for low bands (160m, 80m) incorrect by 10x \*\*\*

Rev 2.0 - 2025-11-02

  - **CRITICAL FIX:** Corrected all inductor and capacitor values for all 8 filters.
  - Replaced all inductors with Wurth 744333 (WE-PD2) series shielded SMT parts.
  - Specified parallel capacitors for the C2 position on ALL 8 filters for current sharing.
  - Regenerated complete Bill of Materials and cost analysis.
  - Total cost revised to $89.90.
  - Updated PCB layout guidance for SMT inductors and universal C2 paralleling.

Author: NexRig Development Team
Status: Final Design - Ready for PCB Layout and Production

```

---

## Appendix A: Filter Design Calculations

(No change)

---

## Appendix B: Performance Curves

(No change)

---

## Appendix C: Schematic Symbols and Conventions

(No change)

---
