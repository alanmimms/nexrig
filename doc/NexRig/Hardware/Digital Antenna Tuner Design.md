# NexRig Digital Antenna Tuner: Component Specification

## 1. 📡 Design Overview

This document specifies the component ratings and selections for the NexRig 50W HF Digital Antenna Tuner.

* **Architecture:** Fully configurable L-Network.
* **Power Rating:** 50W continuous.
* **Frequency Range:** 1.8 - 30 MHz.
* **Target Match:** Up to 4:1 VSWR (12.5Ω to 200Ω).
* **Switching:** Relays are "cold-switched" with no RF present, per the EER architecture's zero-volt switching capability.



---

## 2. ⚡ Component Stress Analysis (The "Why")

All component ratings are derived from the worst-case 4:1 VSWR matching scenarios.

### 2.1 Worst-Case Load Conditions

* **TX Side:** 50W into 50Ω = 50 $V_{rms}$, 1.0 $A_{rms}$.
* **High-Z Load:** Matching 50W to 200Ω.
* **Low-Z Load:** Matching 50W to 12.5Ω.

### 2.2 Maximum Voltage (Capacitor Requirement)

The maximum voltage occurs when matching the **High-Z load (200Ω)**.

* The tuner configures as L-series, C-shunt.
* The shunt capacitor bank is placed across the 200Ω antenna load.
* Voltage: $V_{rms} = \sqrt{P \times R} = \sqrt{50W \times 200\Omega} = \textbf{100 V}_{\textbf{rms}}$
* Peak Voltage: $V_{peak} = 100 \times \sqrt{2} = \textbf{141 V}_{\textbf{peak}}$

> **Rating Derived:** All capacitors must withstand a minimum of 141V peak.

### 2.3 Maximum Current (Inductor & Capacitor Requirement)

The maximum current occurs when matching the **Low-Z load (12.5Ω)**.

* The tuner configures as C-series, L-shunt (or L-series, C-shunt).
* The series component (either L or C) must carry the full antenna current.
* Current: $I_{rms} = \sqrt{P / R} = \sqrt{50W / 12.5\Omega} = \textbf{2.0 A}_{\textbf{rms}}$

> **Rating Derived:** All inductors and all capacitors must be able to carry 2.0 $A_{rms}$ without overheating or saturating.

---

## 3. 🧲 Inductor Bank Specification

### 3.1 Requirement Summary
* **Values:** Binary weighted, 0.5 µH to 64 µH.
* **Current:** **2.0 $A_{rms}$** continuous carry.

### 3.2 Design Rationale (Hybrid Approach)
A single inductor technology is not practical for the entire HF range. We adopt a hybrid approach, similar to the PA Tank design, to optimize for performance by band.

* **High-Inductance (16-64 µH):**
    * **Problem:** Air-core inductors for these values are physically enormous and have low Self-Resonant Frequencies (SRFs) that fall within the HF band, making them useless.
    * **Solution:** Use **THT Powdered-Iron Toroids**. The core material concentrates the magnetic field, allowing high inductance with fewer turns. This keeps the SRF high and the physical size manageable. The large T130 core is required to fit the thick #18 AWG wire and dissipate heat from $I^2R$ losses at 2.0A.

* **Mid-Inductance (2-8 µH):**
    * **Solution:** Use a smaller **THT Powdered-Iron Toroid (T106)**. The wire length is shorter, so less heat is generated, and a smaller core is sufficient.

* **Low-Inductance (0.5-1 µH):**
    * **Problem:** At high frequencies (15m, 12m, 10m), powdered-iron cores become lossy (lower Q).
    * **Solution:** Use **THT Air-Core Inductors**. This matches the design of the high-band PA tank inductors (Coilcraft 132-L series). Air-cores have zero core loss, resulting in a much higher Q and SRF, which is critical for high-band efficiency.



### 3.3 Inductor Component Table
* **Wire:** #18 AWG Enameled Copper (for all toroids)

| Required (µH) | Selected Component | Core                           | Windings         |
| :------------ | :----------------- | :----------------------------- | :--------------- |
| 64 µH         | Hand-wound Toroid  | **Amidon T130-2** (Red)        | 21 turns #18AWG  |
| 32 µH         | Hand-wound Toroid  | **Amidon T130-2** (Red)        | 15 turns  #18AWG |
| 16 µH         | Hand-wound Toroid  | **Amidon T130-2** (Red)        | 11 turns  #18AWG |
| 8 µH          | Hand-wound Toroid  | **Amidon T106-2** (Red)        | 10 turns  #18AWG |
| 4 µH          | Hand-wound Toroid  | **Amidon T106-2** (Red)        | 7 turns  #18AWG  |
| 2 µH          | Hand-wound Toroid  | **Amidon T106-2** (Red)        | 5 turns  #18AWG  |
| 1 µH          | Air-Core Inductor  | **Coilcraft 132-10L**          | N/A (THT)        |
| 0.5 µH        | Air-Core Inductor  | **Coilcraft 132-08L** (0.56µH) | N/A (THT)        |

---

## 4. 🔋 Capacitor Bank Specification

### 4.1 Requirement Summary
* **Values:** Binary weighted, 5 pF to 1280 pF.
* **Voltage:** **141 $V_{peak}$** (100 $V_{rms}$) withstand.
* **Current:** **2.0 $A_{rms}$** continuous carry.

### 4.2 Component Selection
* **Type:** **SMT High-Q, Low-ESR RF Capacitors** (e.g., ATC 100B, Vishay RF, Knowles High-Q).
* **Dielectric:** C0G (NP0).
* **Voltage Rating:** **500V DC**. This provides a >3x safety margin over the 141V peak operating voltage and is a standard rating for this class of component.
* **Warning:** Standard C0G capacitors are *not* suitable. They are rated for DC voltage, not RF current. They will fail from $I^2R$ thermal stress.

### 4.3 Parallel Implementation
To safely handle the **2.0 $A_{rms}$** current, higher-value bits will be built by paralleling multiple capacitors. This is the same strategy used in the PA Tank and LPF array for reliability.

* **Benefit:** Paralleling $N$ capacitors splits the current, reducing the heat dissipated *per component* by a factor of $N^2$.
* **Example:** The 1280 pF bit can be made of four 320 pF caps. This quarters the current and reduces the thermal stress on each part by 16x.
* **Layout:** A symmetrical PCB layout is critical to ensure equal current sharing.



---

## 5.  relays: Switching System Specification

### 5.1 Requirement Summary
* **Switching Method:** "Cold-switching" only. Relays **never** switch under RF load.
* **Contact Carry Current:** Must handle **2.0 $A_{rms}$** while closed.
* **Dielectric Withstand:** Must handle **100 $V_{rms}$** while open.

### 5.2 Component Selection (Relay)
* **Part:** **Panasonic TQ2-5V**.
* **Rationale:**
    1.  **BOM Simplification:** This is the *exact same relay* used for the LPF array. Using it here is a perfect example of the "Active Simplification" philosophy.
    2.  **Exceeds Specs:** The TQ2-5V is rated for **2A carry current** and **1000V RMS dielectric strength**.
    3.  **Safety Margin:** This provides a 1:1 match for our current needs and a massive 10x safety margin on voltage withstand.