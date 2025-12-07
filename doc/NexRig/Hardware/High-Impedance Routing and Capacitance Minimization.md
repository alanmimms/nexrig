# PCB Layout Guidelines: High-Impedance Routing & Capacitance Minimization

**Document ID:** LAYOUT-IMPEDANCE-01  
**Applies To:** NexRig Main Board (6-Layer Stackup)  
**Revision:** 2.0

## 1. The Physics: Traces as Lumped Capacitors

The NexRig PCB utilizes a high-performance 6-layer stackup with a very thin prepreg layer (**approx. 0.1mm**) between the Top Layer (L1) and the first Ground Plane (L2).

While this is excellent for 50Ω RF routing and power distribution, it creates a critical problem for high-impedance circuits. At HF frequencies (1.8–30 MHz), the traces on this board are electrically short ($< \lambda/10$) and do not behave as transmission lines. Instead, they behave as **Lumped Elements**.

Specifically, a copper trace over a nearby ground plane acts as a **Parallel Plate Capacitor**:

$$C \approx \frac{\epsilon A}{d}$$

* **Problem:** With $d$ only 0.1mm, a standard trace creates massive **Parasitic Capacitance ($C_p$)** to ground (approx. 3–4 pF per cm).
* **Impact:** In high-impedance domains (800Ω Preselector, 200Ω LPF), this stray capacitance detunes circuits and shorts out high-frequency signals.

To solve this, we use a **"Canyon" strategy**—selectively removing ground planes beneath specific traces to drastically increase $d$, thereby minimizing $C_p$.

---

## 2. The 800Ω Domain (RX Preselector)

**Critical Constraint:** Tuning Range Preservation.

The Receiver Preselector is a High-Q tuned tank circuit. At 30 MHz (10m band), the total required tuning capacitance is extremely small (approx. 10–15 pF). If the PCB trace adds 4 pF of parasitic capacitance, it consumes ~30% of the tuning budget, making it impossible to tune the upper bands.

### Strategy: "The Full Canyon" (Capacitance Elimination)
We must maximize the distance ($d$) between the signal trace and any copper reference to drive $C_p$ effectively to zero.

* **Signal Layer:** Top (L1)
* **Reference Layer:** Bottom Signal/GND (L6)
* **Voided Layers:** L2, L3, L4, L5 (All copper removed under trace)
* **Result:** Increases $d$ from 0.1mm to ~1.5mm. Reduces parasitic capacitance by **~15x**.

**Cross-Section View:**
```text
      [GND]   <-- 1.2mm Gap -->   [SIGNAL]   <-- 1.2mm Gap -->   [GND]    (Layer 1)
        |                             |                            |
      [VIA]                     (VOID / AIR)                     [VIA]    (Layer 2)
      [VIA]                     (VOID / AIR)                     [VIA]    (Layer 3)
      [VIA]                     (VOID / AIR)                     [VIA]    (Layer 4)
      [VIA]                     (VOID / AIR)                     [VIA]    (Layer 5)
        |                             |                            |
      [------------------------ SOLID GROUND ------------------------]    (Layer 6)
      