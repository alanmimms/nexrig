# PA Stage Architecture: 4-FET Quadrature H-Bridge

## 1. Overview

This document defines the architecture for the 50W Power Amplifier
(PA) stage. This stage is responsible for the final RF power
generation, combining the **Amplitude** component (from the 0-60V EER
supply) and the **Phase** component (from the FPGA's NCO) to create
the 50W modulated RF signal.

To achieve high efficiency, linearity, and spectral purity, a
**quadrature-driven, Class-D Full-Bridge (H-Bridge)** topology is
used.

## 2. System Architecture

The PA stage consists of three main sub-blocks:

1.  **4-MOSFET H-Bridge:** A Class-D switching core, driven by
    quadrature-phase signals.
2.  **EER Supply:** The 0-60V EER supply provides the *drain voltage*
    to the H-Bridge, thereby controlling the amplitude of the RF
    output.
3.  **Matching Transformer:** A 5.5:1 ratio transformer that steps up
    the PA's 60V (peak) output to the 141V (peak) required by the
    200$\Omega$ tank circuit.



### Signal Path

1.  The FPGA NCO generates four **quadrature-phase-modulated (PM)**
    logic signals (I+, I-, Q+, Q-).
2.  Two high-speed half-bridge drivers amplify these signals to drive
    the gates of the four MOSFETs.
3.  The 0-60V EER supply provides the **drain voltage** ($V_{DD}$) to
    the entire bridge.
4.  The H-Bridge "chops" this EER voltage, producing a differential,
    3-level RF signal that swings from +60V to -60V.
5.  This 36$\Omega$ output is fed into the **step-up transformer**.
6.  The transformer steps up the voltage, outputting a 141V peak,
    200$\Omega$ (single-ended) signal to the `PA_Tank_Capacitor_Bank`.
7.  The tank filters this signal into a pure sine wave for the LPF
    array.

## 3. Principle of Operation

This architecture completely separates the amplitude and phase
modulation:

* **Amplitude (Envelope) Path:** The output RF signal's amplitude is a
  *direct, linear function* of the EER supply voltage. If the EER
  supply is at 10V, the bridge outputs a low-power RF signal. If the
  EER supply is at 60V, the bridge outputs the full 50W.
* **Phase Path:** The RF signal's phase (and frequency) is controlled
  *entirely* by the timing of the FPGA's NCO. The FPGA's 29 MHz NCO is
  phase-modulated with the SSB information, and its top bits are used
  to generate the four quadrature gate-drive signals.

The H-bridge acts as a highly-efficient, high-speed switching mixer,
multiplying the amplitude (voltage) and the phase (timing) to create
the final modulated RF output.

## 4. Key Architectural Advantages

This topology was chosen over simpler single-FET designs for several
critical performance reasons:

* **Even Harmonic Cancellation:** The differential, push-pull nature
  of the H-bridge **naturally cancels all even-order harmonics (2nd,
  4th, 6th, etc.)**. This is a massive advantage, as it places a much
  lower burden on the LPF array. The LPFs only need to filter the 3rd
  harmonic and higher.
* **Excellent Linearity:** The PA's output voltage is a highly linear
  function of the EER supply input. This makes the system far more
  predictable and stable, dramatically simplifying the Digital
  Pre-Distortion (DPD) algorithm.
* **No DC-Blocking Capacitor:** The transformer provides perfect DC
  isolation to the tank. This eliminates the need for a massive,
  expensive, and power-robbing DC-blocking capacitor in the main RF
  path, which is especially critical for high-efficiency 160m
  operation.
* **Optimized Impedance:** The PA bridge drives a low, stable
  impedance of **36$\Omega$**. This is an easier load to drive at high
  frequency than the 200$\Omega$ tank, leading to better stability and
  FET performance.
* **Component Stress & Speed:** The 50W load is distributed across
  four smaller FETs. This allows for the use of components with lower
  capacitance ($Q_g$, $C_{oss}$), which is the *most important factor*
  for reducing switching losses at 29 MHz.

## 5. Required Component Parameters

### 5.1 Power MOSFETs (Quantity 4)

All four FETs must be identical to ensure bridge symmetry.

* **Type:** N-Channel
* **$V_{DS}$ (Drain-Source Voltage):** **> 80V**. A 100V rating is
  required to provide a safe margin over the 60V supply and any
  switching spikes.
* **$Q_g$ (Total Gate Charge):** **Primary Metric.** Must be as low as
  possible (e.g., < 10 nC) to minimize gate-drive power and switching
  time.
* **$C_{oss}$ (Output Capacitance):** **Secondary Metric.** Must be as
  low as possible (e.g., < 150 pF) to reduce switching losses ($P =
  \frac{1}{2} C V^2 f$).
* **$R_{ds(on)}$ (On-Resistance):** < 100 m$\Omega$. Low conduction
  losses are easy to achieve; low switching losses are the priority.
* **Package:** Low-inductance SMT (e.g., DFN, PowerPAK) with a
  bottom-side thermal pad for heat sinking.

### 5.2 Gate Drivers (Quantity 2)

* **Type:** High-Speed, Half-Bridge Driver (or two isolated high/low
  drivers).
* **Propagation Delay:** **< 20 ns**. This is critical, as a full RF
  cycle at 29 MHz is only 34 ns.
* **Technology:** Must have an integrated bootstrap circuit (or
  isolated supply) to drive the high-side N-channel FETs.
* **Input:** 3.3V logic level compatible (for the FPGA).
* **Peak Current:** > 1A, to charge the FET gates quickly.

### 5.3 PA-to-Tank Matching Transformer (Quantity 1)

* **Type:** Differential-to-Single-Ended (Balun) Transformer.
* **Impedance Ratio:** **~5.5:1** (36$\Omega$ differential primary to
  200$\Omega$ single-ended secondary).
* **Turns Ratio (Voltage):** **~1:2.35** (e.g., 3 turns on the primary
  to 7 turns on the secondary).
* **Power:** 50W+ continuous.
* **Core:** Broadband ferrite suitable for 1.8 - 30 MHz operation at
  50W without saturating.
