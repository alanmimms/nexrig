Antenna → Input Protection → Attenuator → Preselector → QSD Array → DSP Chain → Host Application
             ↑                   ↑            ↑            ↑          ↑
             │                   │            │            │          └─ Calibration & Control
             │                   │            │            └─ FPGA Clock Generation
             │                   │            └─ STM32 Tuning Control
             │                   └─ STM32 Gain Control & Hardware Protection
             └─ Schottky Voltage Clamp
```

### 2.0 Input Protection and Voltage Clamping

**Schottky Diode Voltage Clamp**

Before the attenuator and preselector, a symmetric voltage clamp protects downstream components from excessive RF voltages that could damage the preselector tank switching elements.

**Protection Requirements:**
- Preselector tank Q: ≤20 (maximum across all bands)
- Safe switch voltage: 50V peak-to-peak conservative limit for AS183-92LF GaAs switches
- Target clamp level: 40V peak tank voltage (±20V swing) for 20% safety margin
- Required input clamp: ±2V AC swing (since 20 × 2V = 40V at tank)

**Circuit Topology: DC-Biased Symmetric Clamp**

The clamp uses a DC bias approach to create symmetric voltage limits without requiring a negative supply rail:
```
                         +12V
                          │
                      [40kΩ, 1%]
                          │
                          ├──────── Vhigh = 8V (upper clamp reference)
                          │
                      [40kΩ, 1%]
                          │
                          ├──────── Vbias = 6V (DC bias point)
                          │
                      [40kΩ, 1%]
                          │
                         GND ────── Vlow = 4V (lower clamp reference)
                         
Signal Path:

From Antenna
      │
  [100nF AC coupling]
      │
      ├────[100kΩ]──── Vbias (6V)  (sets DC operating point)
      │
      │ Signal now at 6V DC ± AC swing
      │
      ├────[BAT54 D1]────[1µH RFC]────[10Ω]──── Vhigh (8V)
      │     cathode→          │                    │
      │                   [0.1µF]              [0.1µF]
      │                       │                    │
      │                      GND                  GND
      │
      ├────[BAT54 D2]────[1µH RFC]────[10Ω]──── Vlow (4V)
      │      anode→          │                    │
      │                   [0.1µF]              [0.1µF]
      │                       │                    │
      │                      GND                  GND
      │
  [100nF AC coupling]
      │
  To Attenuator
```

**Operation:**
- **DC bias resistor (100kΩ)**: Pulls signal path to 6V DC midpoint between clamp voltages
- **AC coupling capacitors**: Isolate DC bias from antenna and attenuator
- **Upper clamp (D1)**: When signal exceeds 8.4V (8V + 0.4V diode drop), D1 conducts, sinking excess current through RFC to 8V rail
- **Lower clamp (D2)**: When signal drops below 3.6V (4V - 0.4V diode drop), D2 conducts, sourcing current from 4V rail through RFC
- **RF chokes (1µH)**: Block RF from DC supply rails while allowing DC connection to clamp references
- **Series resistors (10Ω)**: Limit peak clamp current and provide damping to prevent oscillation
- **Bypass capacitors (0.1µF)**: Provide low-impedance AC return path for clamp currents

**Performance Characteristics:**

*Clamp Voltages:*
```
Normal signals (±1.5V AC):
  DC level: 6V ± 1.5V = 4.5V to 7.5V
  No clipping, signal passes unaffected ✓

Strong signal (+23 dBm input, ±3V AC):
  Clamped to: 3.6V to 8.4V = 6V ± 2.4V
  AC swing: 2.4V peak
  Tank voltage: 20 × 2.4V = 48V peak ✓

Survival signal (+28 dBm input, ±4V AC):
  Clamped to: 3.6V to 8.4V (hard limit)
  AC swing: 2.4V peak  
  Tank voltage: 48V peak ✓✓
  Margin: 4% below 50V conservative safe limit
```

*Loading and Insertion Loss:*
- DC bias impedance: 100kΩ (negligible loading on 50Ω line)
- Clamp diodes (off-state): >1kΩ impedance
- Effective load: 50Ω || 100kΩ ≈ 49.95Ω
- **Insertion loss: 0.004 dB** (unmeasurable)
- **VSWR: 1.001:1** (essentially perfect match)

*Response Time and Power Dissipation:*
- Response time: <1 ns (Schottky diode switching speed)
- Peak clamp current at +28 dBm: ~92 mA
- Power dissipation in series resistors: ~43 mW average per clamp path
- Power dissipation in diodes: ~18 mW average per diode
- All components well within thermal ratings

**Design Trade-offs:**

*Why Not Tank-Side Protection?*
- TVS diodes at tank would have 50-150 pF capacitance
- On 10m band (640 pF tuning cap), adding 100 pF would shift frequency by 2.1 MHz
- Makes preselector tracking unreliable
- Low-capacitance high-voltage TVS diodes are rare and expensive
- **Conclusion: Must protect in 50Ω domain before preselector**

*Why DC Bias Instead of Diode Strings?*
- Diode string approach (9× diodes each direction): 18 components, $1.80, fixed voltage
- DC bias approach: 2 diodes + 5 resistors, $0.54, easily adjustable
- Better precision (1% resistor tolerance vs ±0.1V diode variation)
- Simple adjustment: change resistor values to tune clamp voltages
- **Conclusion: DC bias is more elegant and cost-effective**

*Why Not Comparator + AGC Control?*
- Comparator-based protection: 10-20 ms response time
- Tank builds to dangerous voltage in ~2 µs (Q-dependent time constant)
- Would require buffer amplifier for fast peak detection, adding cost and complexity
- Software AGC already handles normal signal variations gracefully
- **Conclusion: Hardware clamp provides instant protection; STM32 AGC handles normal operation**

**Component Selection:**
- Schottky diodes: BAT54 (30V breakdown, 0.4V forward drop, <1 ns response)
- RFCs: 1µH, 0805 package (presents ~40Ω at 7 MHz, adequate RF blocking)
- Divider resistors: 1% tolerance for precise clamp voltages
- Bypass capacitors: X7R 0.1µF for good RF performance and stability

**Summary:**
The Schottky clamp provides fast, passive, symmetric voltage limiting that protects preselector switches from overvoltage damage while introducing negligible insertion loss and requiring no complex control circuitry. It complements the STM32-controlled AGC attenuator, providing instant hardware protection against transients while allowing graceful software-controlled gain adjustment during normal operation.

### 2.1 Input Protection and Gain Control

**Switched-Pad Attenuator**
- **Topology**: Four-stage switched T-pad network (3, 6, 12, 24 dB stages)
- **Range**: 0 to 45 dB in 3 dB steps (additive)
- **Impedance**: Constant 50Ω across all attenuation settings
- **Survival Rating**: +28 dBm (630 mW) input power after voltage clamp protection
- **Control**: Direct microcontroller GPIO with complementary MOSFET pairs per stage
- **Control Logic**: Active-LOW attenuation enable (LOW = attenuate, HIGH = bypass)
- **Purpose**: Protects receiver front-end from strong signals and provides coarse AGC

**Control Architecture:**
Each attenuator stage uses dual complementary MOSFETs with inverted control logic:
- Hex inverter (74HC04) converts active-LOW control signals to active-HIGH for existing MOSFET gate drivers
- STM32 GPIO configured as open-drain outputs for wire-OR capability with hardware protection
- Stiff 4.7kΩ pullup resistors to +3.3V logic rail
- STM32 can read attenuator state by monitoring GPIO pin voltage (even while driving as open-drain)

The attenuator maintains signal integrity by presenting a constant impedance regardless of attenuation setting, preventing reflections that would degrade dynamic range. The additive stage design allows flexible attenuation profiles optimized for different operating scenarios. The active-LOW control enables simple wire-OR logic with hardware protection comparators without requiring complex priority arbitration.

### 2.2 Preselector Front-End

**Continuously-Tunable LC Tank Architecture**

The preselector implements a single parallel LC resonant tank with digitally-switched inductors and a binary-weighted capacitor bank for continuous tuning across the entire HF spectrum. A key design decision was to **limit Q factor to ≤20** across all bands, which provides adequate selectivity while keeping tank voltages at safe levels for the GaAs RF switches.

**Q Factor and Voltage Management Trade-off:**

The Q factor selection represents a fundamental trade-off between selectivity and component safety:

*High Q (Q=30, originally considered):*
- Advantages: Better adjacent-channel rejection (35.6 dB at 3f vs 33 dB with Q=20)
- Disadvantages: Higher tank voltage (237V peak at survival input vs 158V with Q=20)
- Risk: Potential switch breakdown, unknown voltage rating of AS183-92LF

*Moderate Q (Q=20, selected):*
- Tank voltage at +28 dBm input: 158V peak without clamp, 48V peak with clamp
- Harmonic rejection: 33 dB at 3f (only 2.6 dB less than Q=30)
- Combined with QSD3 null: Still achieves >70 dB total 3rd harmonic rejection
- Selectivity: 3 dB bandwidth ~187 kHz on 80m (2× wider than baseband capture bandwidth)
- **Adequate for purpose**: Primary selectivity comes from digital filtering, not preselector

*Why Not Lower Q?*
- Q<15 would reduce harmonic rejection below 30 dB at preselector
- Would place more burden on QSD harmonic nulling and digital processing
- Wider bandwidth increases risk of strong out-of-band signals causing IMD
- Q=20 represents optimal balance for this application

**Combined Protection Strategy:**
1. **Preselector Q≤20**: Limits tank voltage multiplication to 20× input voltage
2. **Schottky clamp**: Limits input to ±2.4V peak (±20% tolerance)
3. **Result**: Maximum tank voltage = 20 × 2.4V = 48V peak (safely below 50V conservative limit)

**Switched Inductor Bank**

Three physical inductors provide four effective inductance values through parallel combination, using GaAs RF switches for fast, low-loss switching:
```
                    RF Hot (Tank Node)
                         │
              ┌──────────┼──────────┐
              │          │          │
           [SW1]      [SW2]      [SW3]
           RF1│       RF1│       RF1│
              │          │          │
           RFC├       RFC├       RFC├
              │          │          │
          [L1]500nH  [L2]180nH  [L3]68nH
              │          │          │
           RF2├       RF2├       RFC├
              │          │          │
             GND        GND        GND
```

**Switch Type: AS183-92LF GaAs MESFET SPDT**
- Technology: Gallium Arsenide MESFET
- Insertion loss: 0.35 dB typical
- Isolation: >40 dB (unselected paths)
- Power handling: Suitable for tank circuit application (documented preselector use)
- Switching speed: <1 µs
- Package: SOT-363
- Cost: ~$1.25 each

**Why AS183-92LF vs. Alternatives:**

*AS169-73LF Comparison (cheaper alternative, $0.85):*
- Better IP3 spec (+50 dBm vs +47 dBm)
- Lower cost ($0.40 less per switch)
- **Critical issue**: No documented use in preselector/tank applications
- **Voltage concern**: IP3 testing measures power in matched 50Ω systems, not OFF-state voltage capability
- **OFF-state voltage stress**: In tank circuits, the unused switch path sees full tank voltage between toggle and RF pins
- **Risk**: Unknown breakdown voltage could be 20V, 50V, or 100V - insufficient data
- **Field reliability concern**: Potential catastrophic failure or gradual degradation
- **Validation cost**: Would require extensive high-voltage RF testing across temperature
- **Conclusion**: $5.20 total savings not worth risk for critical RF component

*AS183-92LF Selection Rationale:*
- Documented use in preselector circuits (Skyworks application notes)
- Application heritage suggests validated OFF-state voltage capability
- Low on-resistance (0.8Ω) minimizes insertion loss
- Die/junction design optimized for high-voltage tank environments
- Proven reliability in similar applications
- **Conclusion**: Worth extra cost for peace of mind in production design

**Inductor Selection Logic:**

The SPDT switches route each inductor to either the tank hot node (active) or ground (shorted):

| Inductance | SW1 State | SW2 State | SW3 State | Configuration |
|------------|-----------|-----------|-----------|---------------|
| 500 nH | RF1→RFC | RF2→RFC | RF2→RFC | L1 only (L2, L3 shorted) |
| 180 nH | RF2→RFC | RF1→RFC | RF2→RFC | L2 only (L1, L3 shorted) |
| 68 nH | RF2→RFC | RF2→RFC | RF1→RFC | L3 only (L1, L2 shorted) |
| 49.4 nH | RF2→RFC | RF1→RFC | RF1→RFC | L2 ‖ L3 parallel (L1 shorted) |

**Key Advantage of Switch Topology:**
- Active inductor: Connected between hot node and ground via RFC path
- Inactive inductors: Both ends shorted to ground (RF2→RFC→GND)
- Zero stray reactance from unused components
- Complete isolation: >40 dB

**Parallel Inductor Configuration (15m, 12m, 10m bands):**

The 49.4 nH inductance is achieved by operating L2 and L3 simultaneously in parallel:
```
L_parallel = 1 / (1/L2 + 1/L3)
L_parallel = 1 / (1/180nH + 1/68nH) = 49.4 nH

Both SW2 and SW3 set to RF1→RFC
Both inductors connected to tank hot node
Parallel combination at RF frequencies
```

This approach provides optimal inductance for high bands without requiring a fourth physical inductor, saving cost and PCB space while maintaining performance.

**Binary-Weighted Capacitor Bank (8-bit)**

The capacitor bank uses the same AS183-92LF GaAs switches in an identical SPDT topology:
```
                    RF Hot (Tank Node)
                         │
       ┌─────────────────┼─────────────────┐
       │        │        │        │         │
    [SW_C7]  [SW_C6]  [SW_C5]  ...      [SW_C0]
     RF1│     RF1│     RF1│              RF1│
        │        │        │                 │
     RFC├     RFC├     RFC├              RFC├
        │        │        │                 │
     [C7]      [C6]      [C5]             [C0]
    512pF     256pF     128pF            4pF
        │        │        │                 │
     RF2├     RF2├     RF2├              RF2├
        │        │        │                 │
       GND      GND      GND               GND
```

**Capacitor Values:**
```
Bit 7 (MSB):  512 pF
Bit 6:        256 pF
Bit 5:        128 pF
Bit 4:         64 pF
Bit 3:         32 pF
Bit 2:         16 pF
Bit 1:          8 pF
Bit 0 (LSB):    4 pF

Total range: 0 to 1020 pF in 4 pF steps
```

**Switching Logic:**
- **Bit = 1** (capacitor active): Switch position RF1→RFC
  - Capacitor connected between hot node and ground (active in tank)
- **Bit = 0** (capacitor inactive): Switch position RF2→RFC
  - Capacitor shorted by switch (both ends grounded)
  - No reactive effect on circuit

**Parallel Capacitor Operation:**

Multiple capacitor switches can be active simultaneously to create arbitrary capacitance values:
```
Example: 640 pF required
Binary: 10100000
Active: C7 (512pF) + C5 (128pF) = 640pF

All inactive capacitors fully shorted
No parasitic effects from unused components
```

**Switch Power Handling in Tank Circuit:**

The switches experience different stress levels depending on whether they're in the selected (conducting) or unselected (blocking) state:

*Selected Component (Switch ON, component active in tank):*
```
Worst case with Q=20, input +28 dBm (7.9V peak):
  Tank voltage: 20 × 7.9V = 158V peak (without clamp)
  Tank voltage: 20 × 2.4V = 48V peak (with Schottky clamp)
  Tank current (500 nH inductor, 3.75 MHz): ~409 mA RMS
  
Switch carries tank circulating current:
  ON-resistance: 0.8Ω (AS183-92LF)
  Power dissipation: (0.409A)² × 0.8Ω = 0.13W
  Switch rating: Suitable for preselector applications
  Voltage across ON switch: Minimal (I × R_on)
  Safety margin: >10× ✓
```

*Unselected Component (Switch OFF, component shorted):*
```
Critical failure mode: OFF-state voltage stress

Tank hot node at 158V peak (worst case without clamp)
Shorted component through switch: Both ends at GND potential
Voltage across OFF switch (toggle→RF pin): 158V peak

With Schottky clamp protection:
Tank hot node at 48V peak maximum
Voltage across OFF switch: 48V peak
AS183-92LF rating: Unknown but validated for preselector use
Safety margin: Conservative design with clamp ✓
```

**Why OFF-State Voltage Matters:**

Standard RF switch testing (IP3, power handling) measures performance in matched 50Ω systems where all ports are terminated. These tests don't reveal OFF-state voltage capability because voltage stress is minimal:
```
IP3 Test at +50 dBm (AS169-73LF spec):
  Power: 100W into 50Ω matched load
  Voltage at load: 100V peak
  Voltage across ON switch: (100V × R_on) / 50Ω = ~2V
  Voltage across OFF switch: ~0V (both ports terminated to similar impedance)
  
Tank Circuit Reality:
  Toggle pin: Connected to tank hot node (48-158V)
  Unselected RF pin: Grounded (0V)
  Voltage across OFF switch: 48-158V ⚠️
  This stress mode never tested in standard characterization
```

This is why AS183-92LF's documented preselector application heritage is critical - it indicates the part was designed and validated for this specific high-voltage OFF-state stress condition.

**Fixed Capacitors (Band-Specific)**

Two additional fixed capacitors handle the very large capacitance requirements of the lowest bands:
```
                    RF Hot (Tank Node)
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    [SW_FIX1]         [SW_FIX2]      (binary bank)
     RF1│              RF1│
        │                 │
     RFC├              RFC├
        │                 │
    [C_160m]          [C_80m]
     12,000pF          2,000pF
        │                 │
     RF2├              RF2├
        │                 │
       GND               GND
```

**Control Logic:**
- **SW_FIX1**: Enable (RF1→RFC) only when on 160m band, otherwise short (RF2→RFC)
- **SW_FIX2**: Enable (RF1→RFC) only when on 80m band, otherwise short (RF2→RFC)

These fixed capacitors are only connected when the 500 nH inductor is selected (160m and 80m bands).

**Band Plan and Inductor Selection**

| Band | Frequency Range | Inductor | L Value | Fixed Cap | Target Q | Notes |
|------|----------------|----------|---------|-----------|----------|-------|
| 160m | 1.8 - 2.0 MHz | L1 only | 500 nH | +12,000 pF | 20 | Max selectivity for crowded band |
| 80m | 3.5 - 4.0 MHz | L1 only | 500 nH | +2,000 pF | 20 | Max selectivity for crowded band |
| 40m | 7.0 - 7.3 MHz | L2 only | 180 nH | None | 20 | Medium Q, good balance |
| 30m | 10.1 - 10.15 MHz | L2 only | 180 nH | None | 18 | Medium Q |
| 20m | 14.0 - 14.35 MHz | L2 only | 180 nH | None | 18 | Medium Q |
| 17m | 18.068 - 18.168 MHz | L3 only | 68 nH | None | 17 | Lower Q, wider response |
| 15m | 21.0 - 21.45 MHz | L2 ‖ L3 | 49.4 nH | None | 17 | Parallel inductors |
| 12m | 24.89 - 24.99 MHz | L2 ‖ L3 | 49.4 nH | None | 17 | Parallel inductors |
| 10m | 28.0 - 29.7 MHz | L2 ‖ L3 | 49.4 nH | None | 17 | Parallel inductors |

**Variable Impedance Strategy**

The tank impedance varies across the HF spectrum as a natural consequence of the L/C selection, creating a deliberate trade-off between selectivity and voltage management:

**Low Bands (160m - 40m):**
- Larger inductors selected (500 nH, 180 nH)
- Higher tank impedance: ~2.0-2.5 kΩ typical
- Higher Q (20) for maximum selectivity
- Essential for rejecting powerful broadcast interference and dense amateur traffic
- Handles weaker signal levels typical of these bands
- Lower circulating currents reduce switch stress

**High Bands (17m - 10m):**
- Smaller inductors selected (68 nH, 49.4 nH)
- Lower tank impedance: ~500-800 Ω typical
- Lower Q (17) provides broader, flatter passband
- Voltage management: Limits peak RF voltage to protect switching components
- Wide coverage without constant retuning
- Higher circulating currents but still within switch ratings

**Tuning Resolution**

The 8-bit binary-weighted capacitor bank with 4 pF LSB provides frequency resolution matched to operational requirements:

| Band | Frequency Step per LSB | Design Target | Status |
|------|----------------------|---------------|--------|
| 160m | 2.7 kHz | 50 kHz | ✓✓ Excellent |
| 80m | 21 kHz | 50 kHz | ✓✓ Excellent |
| 40m | 5.2 kHz | 50 kHz | ✓✓ Excellent |
| 30m | 14.5 kHz | 50 kHz | ✓✓ Excellent |
| 20m | 42 kHz | 50 kHz | ✓ Good |
| 17m | 32 kHz | 50 kHz | ✓ Good |
| 15m | 37 kHz | 100 kHz | ✓✓ Excellent |
| 12m | 61 kHz | 100 kHz | ✓ Good |
| 10m | 95 kHz | 100 kHz | ✓ Acceptable |

The relaxed 100 kHz resolution requirement on high bands (15m-10m) is operationally appropriate because:
- These bands have broader preselector response (lower Q=17)
- The baseband capture bandwidth is 96 kHz (±48 kHz)
- Signals are less densely packed on high bands
- The preselector 3 dB bandwidth on 10m is ~1.44 MHz, making 95 kHz steps imperceptible

**Why 8-bit Resolution (Not 6-bit):**

A 6-bit capacitor bank was considered for cost savings (eliminating 2 switches):

*6-bit Analysis:*
```
Cost savings: 2 × $1.25 = $2.50 per receiver
Frequency steps (10m): 364 kHz per LSB
Problem: Only 4-5 discrete tuning points across preselector passband
Mitigation: Adaptive tuning algorithm (offset QSD clocks to compensate)
```

*Decision to Keep 8-bit:*
- Frequency step on 10m (95 kHz) vs 6-bit (364 kHz): 3.8× coarser
- 10m has best propagation conditions when open - want full performance
- Simpler firmware (no adaptive offset compensation needed)
- More uniform performance across all bands
- $2.50 savings not significant in context of $500+ transceiver
- Future features (automatic preselector peaking, notch tuning) benefit from fine resolution

**Parasitic Capacitance**

The total parasitic capacitance from all switches must be accounted for in tuning calculations:
- 13 AS183-92LF switches total (3 inductors + 8 capacitors + 2 fixed)
- Typical parasitic: ~0.8-1.0 pF per switch (primarily OFF-state capacitance)
- **Total parasitic: ~10-13 pF** (always present, included in tuning algorithm)

This parasitic is calibrated out during preselector tuning calibration and incorporated into the STM32's frequency-to-capacitance lookup tables.

**Performance Characteristics**

*Switching Performance:*
- Switching speed: <1 µs (GaAs MESFET technology)
- Insertion loss per switch: ~0.35 dB (typical)
- Total insertion loss (3 active switches typical): ~1 dB
- Isolation (unselected components): >40 dB

*Cost Analysis:*
- Switch count: 13 total (3L + 8C + 2 fixed)
- Switch cost: 13 × $1.25 = $16.25 per receiver
- Inductors: 3 × ~$0.50 = $1.50
- Capacitors (binary bank): 8 × ~$0.20 = $1.60
- Fixed capacitors: 2 × ~$0.30 = $0.60
- **Total preselector switching cost: ~$20 per receiver**

This continuously-tunable architecture provides the initial selectivity and harmonic rejection needed to protect the QSD array while maintaining flexibility across all amateur bands.

**Harmonic Rejection Performance**

The preselector provides significant initial harmonic attenuation before the QSD mixers. With Q limited to 20:

| Band | Q Factor | 3f Rejection (dB) | 5f Rejection (dB) | 7f Rejection (dB) |
|------|----------|-------------------|-------------------|-------------------|
| 160m | 20 | 33.0 | 40.6 | 44.2 |
| 80m | 20 | 33.0 | 40.6 | 44.2 |
| 40m | 20 | 33.0 | 40.6 | 44.2 |
| 30m | 18 | 31.1 | 38.7 | 41.9 |
| 20m | 18 | 31.1 | 38.7 | 41.9 |
| 17m | 17 | 30.6 | 38.2 | 41.4 |
| 15m | 17 | 30.6 | 38.2 | 41.4 |
| 12m | 17 | 30.6 | 38.2 | 41.4 |
| 10m | 17 | 30.6 | 38.2 | 41.4 |

**Comparison: Q=20 vs Originally Considered Q=30**

| Harmonic | Q=30 Rejection | Q=20 Rejection | Difference | Impact |
|----------|----------------|----------------|------------|--------|
| 3f | 35.6 dB | 33.0 dB | -2.6 dB | Minimal (QSD3 provides >40 dB additional) |
| 5f | 43.1 dB | 40.6 dB | -2.5 dB | Slight reduction, still excellent |
| 7f | 46.3 dB | 44.2 dB | -2.1 dB | Negligible |

**Combined System Performance (Q=20):**

When combined with the QSD harmonic nulling (see Section 3), the system achieves:
- **3rd harmonic (3f)**: >73 dB rejection (33 dB preselector + >40 dB QSD3 null)
- **5th harmonic (5f)**: 54-59 dB rejection (preselector + natural QSD rolloff)
- **7th harmonic (7f)**: 61-66 dB rejection (preselector + natural QSD rolloff)
- **Even harmonics (2f, 4f, 6f...)**: Theoretically infinite rejection (QSD1/QSD2 nulls)

**Conclusion:** The reduction from Q=30 to Q=20 costs only 2.6 dB of 3rd harmonic rejection at the preselector, while providing critical switch protection. The combined system still exceeds typical receiver specifications (>50 dB spurious rejection) by significant margin.

## 3. Triple-QSD Mixer Architecture

The core innovation of the receiver is the parallel operation of three quadrature sampling detectors, each optimized for different spurious rejection characteristics.

### 3.1 QSD1: Primary Receiver (sampling at f - k)

**Clock Configuration**
- Sampling frequency: f - k (where k is a small offset, typically 15-20 kHz)
- Clock generator frequency: 4(f - k)
- Clock type: Standard 4-phase quadrature (50% duty cycle)
- Phases: I+, I-, Q+, Q- at 90° spacing

**Characteristics**
- Provides primary signal reception with excellent sensitivity
- Standard harmonic response (responds to f, 3f, 5f, 7f... odd harmonics)
- Nulls all even harmonics (2f, 4f, 6f, 8f...)
- Offset frequency creates image separation for software processing

### 3.2 QSD2: Image Rejection Path (sampling at f + k)

**Clock Configuration**
- Sampling frequency: f + k (opposite offset from QSD1)
- Clock generator frequency: 4(f + k)
- Clock type: Standard 4-phase quadrature (50% duty cycle)
- Phases: I+, I-, Q+, Q- at 90° spacing

**Characteristics**
- Mirrors QSD1 with opposite frequency offset
- Nulls all even harmonics (2f, 4f, 6f, 8f...)
- Enables software-based image cancellation through complex signal combination
- Provides diversity reception for multipath mitigation

### 3.3 QSD3: Harmonic Rejection Path (sampling at f)

**Clock Configuration**
- Sampling frequency: f (same fundamental frequency as the desired signal)
- Clock generator frequency: 6f (six times the fundamental)
- Clock type: Six-phase with 33.33% duty cycle
- Phases: Four outputs (I+, I-, Q+, Q-), each active for exactly 1/3 cycle

**Timing Structure**

The 33.33% duty cycle creates a fundamental difference from standard QSD operation:
```
LO Period divided into 6 slots (60° each):

I+: ██████████░░░░░░░░░░░░░░░░░░  (Slots 0-1: ON)
I-: ░░░░░░░░░░░░░░░░██████████░░  (Slots 3-4: ON)
Q+: ░░░░██████████░░░░░░░░░░░░░░  (Slots 1-2: ON)
Q-: ░░░░░░░░░░░░░░░░░░░░██████████  (Slots 4-5: ON)
```

**Harmonic Nulling Mechanism**
- The 33.33% duty cycle creates a null in the mixer's frequency response at 3f (and all multiples: 6f, 9f, 12f...)
- Third harmonic interference (a major source of receiver spurious responses) produces minimal output
- Trade-off: Slightly reduced sensitivity at fundamental frequency (~1-2 dB)
- Target performance: >40 dB null depth at 3f with proper duty cycle calibration

**Implementation Requirements**
- Duty cycle precision: 33.33% ±0.1% for >40 dB rejection
- Phase accuracy: Critical synchronization between I and Q paths
- Calibration: Software-adjustable duty cycle compensation for component tolerances

### 3.4 Combined System Harmonic Rejection

The three QSDs work together to provide comprehensive harmonic rejection:

**Harmonic Response Table:**

| Harmonic | QSD1/QSD2 Response | QSD3 Response | Combined Result |
|----------|-------------------|---------------|-----------------|
| f (fundamental) | Full response | Full response (slight reduction) | Excellent sensitivity |
| 2f | **NULL** (even) | Response | **Rejected by QSD1/QSD2** |
| 3f | Response (1/3 amplitude) | **NULL** (33.33% duty) | **>73 dB total rejection** |
| 4f | **NULL** (even) | Response | **Rejected by QSD1/QSD2** |
| 5f | Response (1/5 amplitude) | Response | 54-59 dB rejection (preselector + rolloff) |
| 6f | **NULL** (even) | **NULL** (multiple of 3) | **Double null** |
| 7f | Response (1/7 amplitude) | Response | 61-66 dB rejection (preselector + rolloff) |
| 8f+ | **NULL** (even) or Response | Various | >60 dB typical |

**Critical Analysis:**
- **Excellent rejection**: 2f, 3f, 4f, 6f (>70 dB)
- **Good rejection**: 7f and higher (>58 dB)
- **Adequate rejection**: 5f (54-59 dB, potential for software enhancement)

The 5th harmonic represents the weakest point in the rejection profile. However, this is mitigated by:
1. The preselector providing 38-43 dB attenuation at 5f
2. Natural 1/5 amplitude rolloff in QSD response (~14 dB)
3. Potential for software-based adaptive cancellation using the triple-QSD calibration system
4. Low probability of real-world 5f interference (5× operating frequency typically in different band)

## 4. Clock Generation Subsystem

**Master Reference**
- Source: 40 MHz TCXO (high-stability temperature-compensated crystal oscillator)
- Stability: Ensures coherent phase relationships across all three QSD paths

**FPGA Digital Synthesizer (Lattice iCE40UP3K)**

The FPGA implements four independent numerically controlled oscillators (NCOs) with precise phase and frequency control:

1. **NCO1**: Generates 4(f - k) clock for QSD1, 4-phase quadrature output
2. **NCO2**: Generates 4(f + k) clock for QSD2, 4-phase quadrature output  
3. **NCO3**: Generates 6f clock for QSD3, 6-phase output decoded to 33.33% duty cycle
4. **NCO4**: Transmitter modulator clock (separate subsystem)

**NCO Architecture**
- Phase accumulator: 32-bit resolution (<0.1 Hz frequency precision)
- Master clock: 240 MHz (generated by internal PLL from 40 MHz TCXO)
- Frequency resolution: ~0.056 Hz steps across HF spectrum
- Phase coherence: All NCOs derive from common master, ensuring phase-locked operation

**Critical Implementation: 33.33% Duty Cycle Generator**

For QSD3's harmonic rejection:
```
40 MHz TCXO → PLL → 600 MHz Master → NCO → 6f Clock → ÷6 Counter → Decoder
                                                                      ↓
                                                         I+, I-, Q+, Q- outputs
```

The divide-by-6 counter produces a 3-bit count (0-5), which is decoded to four outputs where each is active for exactly two consecutive count states, creating the precise 33.33% duty cycle required for third harmonic nulling.

**Decoder Truth Table:**
| Count | I+ | I- | Q+ | Q- | Phase |
|-------|----|----|----|----|--------|
| 0     | 1  | 0  | 0  | 0  | 0°     |
| 1     | 1  | 0  | 1  | 0  | 60°    |
| 2     | 0  | 0  | 1  | 0  | 120°   |
| 3     | 0  | 1  | 0  | 0  | 180°   |
| 4     | 0  | 1  | 0  | 1  | 240°   |
| 5     | 0  | 0  | 0  | 1  | 300°   |

Each output is active (1) for exactly 2 consecutive count states, creating the 120° (1/3 cycle) ON time required.

## 5. Analog-to-Digital Conversion

Each QSD produces a pair of differential baseband signals (I and Q channels), resulting in six analog channels total across the three mixers.

**ADC Architecture**
- Converter: Six simultaneous-sampling channels
- Resolution: 16-bit minimum for wide dynamic range
- Sample rate: Matched to STM32 DSP capability (~192 kHz typical)
- Interface: Direct connection to STM32H753 ADC peripherals
- Anti-aliasing: Passive RC networks between QSD outputs and ADC inputs

The simultaneous sampling is critical for maintaining precise phase relationships between I and Q channels within each QSD and between the three QSD paths.

## 6. Digital Signal Processing Architecture

### 6.1 Embedded Processing (STM32H753)

**Hardware Specifications**
- Core: 480 MHz ARM Cortex-M7 with FPU and DSP extensions
- Memory: 1 MB Flash, 1 MB RAM
- Purpose: Real-time RF processing and hardware control

**DSP Responsibilities**
- **Decimation**: Reduces 192 kHz I/Q streams from ADCs to manageable bandwidth
- **Packetization**: Frames data for USB Ethernet transmission to host
- **Low-Latency Control**: Manages T/R switching, preselector tuning, attenuator settings
- **FPGA Interface**: Configures NCO frequencies and phases via SPI

The embedded processor handles only time-critical operations, keeping CPU headroom available for reliable real-time performance.

### 6.2 Host Processing (PC Application)

**Platform**: Cross-platform Electron application (Windows, macOS, Linux)

**DSP Responsibilities**
- **Triple-QSD Combining**: Performs complex signal processing to combine outputs from all three QSDs
- **Harmonic Cancellation**: Applies measured calibration coefficients to null spurious responses
- **Image Rejection**: Processes QSD1 and QSD2 pairs for image frequency suppression
- **Demodulation**: All mode-specific demodulation (SSB, CW, AM, FM, digital modes)
- **User Filtering**: Interactive bandpass, notch, and noise reduction filters
- **Visualization**: 30 FPS waterfall display and constellation plots

**Native DSP Backend**
The Electron application loads native C++ modules for performance-critical operations, achieving near-native processing speed while maintaining cross-platform compatibility.

## 7. Calibration and Optimization System

### 7.1 Self-Calibration Capability

The system leverages the transmitter's ability to generate precisely controlled microwatt-level test signals for comprehensive receiver calibration:

**Calibration Signal Levels**
- Transmitter output: -40 dBm (0.1 μW)
- Receiver noise floor: -130 dBm
- Calibration SNR: 90 dB (excellent for precise measurements)
- Regulatory: Below Part 15 limits, no interference concerns

**Calibration Procedures**

**Duty Cycle Optimization (QSD3)**
- Generate carrier at 3f at -40 dBm
- Monitor QSD3 output while adjusting duty cycle register in FPGA
- Null depth indicates precision:
  - -20 dB: Duty cycle off by ~2%
  - -40 dB: Duty cycle off by ~0.5%
  - -60 dB: Duty cycle within 0.1% (optimal)

**Amplitude/Phase Matching**
- Inject test tones at f-k, f, f+k, and 3f
- Measure complex gain (magnitude and phase) through each QSD path
- QSD1 and QSD2 sample at their respective offset frequencies (f±k)
- QSD3 samples at f with harmonic rejection characteristics
- Build correction matrices for software combining algorithms
- Accounts for component tolerances and PCB parasitic effects

**Preselector Characterization**
- Sweep test frequency around target (f-50kHz through f+50kHz)
- Measure response at each point
- Map the actual preselector bandpass shape
- Detect any detuning or component drift
- Auto-adjust capacitor selection if needed for optimal response

**Real-World Harmonic Response Measurement**
- Theory predicts specific harmonic rejection values
- Actual performance differs due to:
  - FET switching characteristics in QSD mixers
  - PCB parasitic capacitances and trace inductances
  - Component tolerances (capacitors, resistors in QSD)
  - Temperature-dependent effects
- Calibration measures ACTUAL response with test signals, not just theoretical
- Allows creation of precise correction coefficients for software processing

### 7.2 Dynamic Optimization Strategy

Since calibration is "free" (microwatts, milliseconds), the system can perform multiple calibration types:

**Per Band Change:**
- Full calibration sweep (10-20 test frequencies across band)
- Map the harmonic response curves for this specific frequency range
- Set optimal parameters for QSD combining and preselector tracking
- Takes a few hundred milliseconds during band change (imperceptible to user)

**Periodic Verification (Every Few Minutes):**
- Single tone at 3f to verify QSD3 null depth
- Quick check of amplitude/phase matching between paths
- Tweak parameters if drift detected
- Background operation during normal receive

**After Large Temperature Changes:**
- Quick amplitude/phase calibration between QSD paths
- Duty cycle verification for QSD3
- Preselector retuning if needed
- Triggered by monitoring MCU temperature sensor

**The Measurement Dynamic Range Advantage**

The system's huge dynamic range makes precision calibration practical:
```
Noise floor: -130 dBm (typical HF receiver)
Calibration signal: -40 dBm
Strong interferencer: +10 dBm possible

Calibration operates in the sweet middle ground:
  Calibration signals: 90 dB above noise (easy to measure accurately)
  But: 50 dB below normal strong signals (no interference with operation)
  Available dynamic range: 140 dB total (from ADCs)
```

This means calibration measurements have excellent SNR and precision without requiring any special receiver configuration or user intervention.

### 7.3 Harmonic Cancellation Coefficients

With microwatt test signals, the system can measure exact transfer functions:

**For 3f Interference Cancellation:**
```
1. Inject 3f test tone at -40 dBm
2. Measure response in QSD1: Complex value A₁ (magnitude + phase)
3. Measure response in QSD2: Complex value A₂
4. Measure response in QSD3: Complex value A₃ (should be near zero)

Now the system knows EXACTLY how 3f couples into each QSD path,
not just the theoretical prediction.

Software can then combine the three QSD outputs with weighting:
  Output = (QSD1 × W₁) + (QSD2 × W₂) + (QSD3 × W₃)
  
Where W₁, W₂, W₃ are calculated to null 3f while preserving f.
```

This measured approach accounts for all real-world imperfections and provides superior harmonic rejection compared to theoretical calculations alone.

### 7.4 Preselector Interaction Calibration

The preselector's tuned response can be precisely characterized:

**Frequency Response Mapping:**
```
1. Set preselector to target frequency f
2. Transmit test tones from (f - 100kHz) to (f + 100kHz) in 10 kHz steps
3. Measure received signal strength at each frequency
4. Build actual preselector frequency response curve

Benefits:
  - Detect preselector mistuning (peak not at target frequency)
  - Measure actual bandwidth and shape (may differ from theory)
  - Identify component tolerance effects
  - Enable auto-correction: adjust capacitor selection to center peak
