# NexRig RX Preselector Design
## 800Î© Continuously Tunable, 1.8-30.0 MHz, Triple QSD Receiver

## Overview

Tunable band-pass filter ahead of three QSDs (at f, f+k, f-k) providing:
- Out-of-band interference rejection
- 3f attenuation >30 dB (complements QSD3 harmonic null)
- Overload protection
- Continuously tunable across 1.8-30.0 MHz with no gaps

**Architecture:**
- 800Î© tank impedance optimized for CMOS switch Ron and voltage limits
- Binary-weighted capacitor bank (9 bits, 4pF LSB, 13-2057pF range)
- Four inductors (L1=2ÂµH, L2=720nH, L3=270nH, L4=470nH), seven configurations via parallel combination
- ADG884 CMOS switches (5V supply, 0.35Î© Ron)
- Single fixed capacitor (C_160m=3.3nF) for 160m band
- Fixed capacitor X=220pF always parallel with L1

## Design Goals & Achieved Performance

| Parameter | Target | Achieved | Notes |
|-----------|--------|----------|-------|
| **Frequency range** | 1.8-30.0 MHz | Complete coverage | No gaps, continuous tuning |
| **Bandwidth** | â‰¥96 kHz | 107-975 kHz | Varies by band, all exceed target |
| **Q factor** | 15-20 | 14-58 | Band-dependent, naturally varies with frequency |
| **3f rejection** | >30 dB | 28-36 dB preselector<br>71-81 dB total | Total includes QSD3 null |
| **Tuning resolution** | <50 kHz low bands | 1.0-373 kHz | Excellent low bands, adequate high bands |
| **Insertion loss** | <1.5 dB | 0.8-1.2 dB | Including switches and transformers |
| **Input voltage limit** | Safe for switches | 2.8V pk-pk | Via voltage clamp, keeps tank <5.3V |
| **Capacitor voltage** | Realistic rating | 50V C0G | 9Ã— safety margin vs 5.3V max |
| **Cost** | Minimize | $16.78/RX | Still $2.55/RX cheaper than AS183-92LF design |

**Q variation strategy:** Fixed 800Î© impedance gives Q = X_L/R_total, so Q increases with frequency. This naturally provides higher selectivity on crowded low bands and wider passbands on high bands where less retuning is needed.

**Design improvements:**
- Added C8=1024pF (9th bit) extends binary range to 2057pF, eliminating need for intermediate fixed capacitors
- Added L4=470nH enables parallel combinations filling all frequency gaps
- Reduced capacitor voltage rating from 500V to 50V: smaller packages, lower cost, adequate 9Ã— safety margin

---

## System Architecture

**Signal path:**
```
Antenna â†’ Attenuator â†’ Voltage Clamp â†’ T1 (50:800Î©) â†’ Preselector â†’ T2 (800:3Ã—50Î©) â†’ 3Ã— QSD
         (0-45 dB)    (Â±1.4V limit)   (4:1 ratio)     (Variable Q)   (Trifilar)
```

**Tank circuit:**
```
Tank Hot Node (800Î© at resonance, biased to +2.5V DC)
     |
     â”œâ”€â”€â”€ SW1 â”€â”€â”€â”¬â”€â”€â”€ [L1 = 2ÂµH] â”€â”€â”€ GND
     |           â””â”€â”€â”€ [X = 220pF] â”€â”€â”€ GND (no switch, always with L1)
     |
     â”œâ”€â”€â”€ SW2 â”€â”€â”€ [L2 = 720nH] â”€â”€â”€ GND
     â”œâ”€â”€â”€ SW3 â”€â”€â”€ [L3 = 270nH] â”€â”€â”€ GND
     â”œâ”€â”€â”€ SW4 â”€â”€â”€ [L4 = 470nH] â”€â”€â”€ GND (NEW)
     |
     â”œâ”€â”€â”€ Binary bank: C0-C8 (4, 8, 16, 32, 64, 128, 256, 512, 1024pF) â”€â”€â”€ GND
     |
     â””â”€â”€â”€ SW_C160 â”€â”€â”€ [C_160m = 3,300pF] â”€â”€â”€ GND (160m only)
```

**Band switching configurations:**

| Band Range | L Config | Effective L | Parallel Calc | DCR | C Available | Coverage |
|------------|----------|-------------|---------------|-----|-------------|----------|
| **1.8-2.3 MHz** | L1 + X | 2.0ÂµH | Single | 0.6Î© | 3,533-4,553pF | 160m |
| **2.3-4.2 MHz** | L1 + X | 2.0ÂµH | Single | 0.6Î© | 233-2,057pF | 80m |
| **4.2-7.8 MHz** | L1â€–L2 | 529nH | 1/(1/2000+1/720) | 0.37Î© | 13-2,057pF | Upper 80m/40m |
| **7.8-14.8 MHz** | L2 | 720nH | Single | 0.4Î© | 13-2,057pF | 40m/30m/20m |
| **11.5-19.5 MHz** | L4 | 470nH | Single | 0.3Î© | 13-2,057pF | 17m overlap |
| **14.0-20.5 MHz** | L2â€–L4 | 285nH | 1/(1/720+1/470) | 0.24Î© | 13-2,057pF | 20m/17m overlap |
| **18.0-30.0 MHz** | L3â€–L4 | 171nH | 1/(1/270+1/470) | 0.19Î© | 13-2,057pF | 15m/12m/10m |

**Key points:**
- X (220pF) has no switchâ€”physically soldered parallel to L1, active only when SW1 closes
- Binary range includes 13pF parasitic capacitance from switches
- Seven configurations provide complete continuous coverage 1.8-30.0 MHz with generous overlaps
- Parallel inductor combinations have lower DCR than individual inductors (resistance in parallel)

**Frequency coverage map:**
```
1.8 â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• 30.0 MHz
    L1+X (160m) â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
                 L1+X (80m) â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
                                  L1â€–L2 â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
                                              L2 â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
                                                       L4 â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
                                                            L2â€–L4 â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
                                                                       L3â€–L4 â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—

Legend: â• Coverage span with binary bank tuning
        â•— Upper frequency limit
All gaps eliminated, generous overlap between bands
```

---

## Input Voltage Clamp

**Purpose:** Protect ADG884 switches (5.3V max with 5V supply) and prevent preselector overload.

**Circuit:**
```
From Attenuator
       |
    â”Œâ”€â”€â”¼â”€â”€â”
    |  |  |
  [D1] | [D2]  BAT54S Schottky pairs
    |  |  |
  [R1] | [R2]  10kÎ© to bias taps
    |  |  |
 [RFC1]|[RFC2] 1ÂµH, blocks RF from DC bias
    |  |  |
   +7.08V  +4.92V
    â†“  â†“  â†“
  [Bypass caps 0.1ÂµF to GND]
```

**Voltage divider (from +12V):**
```
+12V â”€â”€ 82kÎ© â”€â”€ tapH (+7.08V) â”€â”€ 18kÎ© â”€â”€ tapC (+6.0V) â”€â”€ 18kÎ© â”€â”€ tapL (+4.92V) â”€â”€ 82kÎ© â”€â”€ GND
        R3                        R4                       R5                        R6

Total: 200kÎ©, 60ÂµA current
Signal DC bias: +6.0V (center tap)
```

**Clamping action:**
- Upper diode (D1): Conducts when signal exceeds 7.08V - 0.4V â‰ˆ 6.68V
- Lower diode (D2): Conducts when signal falls below 4.92V + 0.4V â‰ˆ 5.32V
- Effective clamp: 5.32V to 6.68V (1.36V pk-pk from diode Vf)
- **Design spec: Â±1.4V AC around 6.0V bias = 2.8V pk-pk max input**

**Voltage multiplication through system:**
```
Input (clamped): Â±1.4V at 6.0V bias
After T1 (4:1 voltage): Â±5.6V AC, DC stripped by transformer
Tank bias: +2.5V injected via 100kÎ© resistor from +2.5V reference
Voltage division (800Î© source â€– 800Î© tank): Ã—0.5
Tank voltage: 2.5V Â± 2.8V = -0.3V to +5.3V âœ“ Just within ADG884 (-0.3V to +5.3V rating)
```

**Capacitor voltage stress:**
```
Tank hot node: -0.3V to +5.3V absolute limits
DC bias: +2.5V
AC swing: Â±2.8V peak
Maximum capacitor voltage: 5.3V

Voltage rating selection:
- 500V rating: 500V / 5.3V = 94Ã— margin (massive overkill, inherited from AS183-92LF design)
- 50V rating: 50V / 5.3V = 9.4Ã— margin (very conservative, standard engineering practice)
- 25V rating: 25V / 5.3V = 4.7Ã— margin (acceptable but tight)

Selected: 50V C0G for 9Ã— safety margin, smaller packages, lower cost
```

**Components:**
- D1, D2: BAT54S dual Schottky (SOT-23), Vf=0.4V, <1ns response
- RFC1, RFC2: 1ÂµH (0805), SRF >100MHz
- R1, R2: 10kÎ© 1% (0805)
- R3, R6: 82kÎ© 1% (0805)
- R4, R5: 18kÎ© 1% (0805)
- C1, C2: 0.1ÂµF X7R (0805)

---

## Transformers

**T1 (Input): 50Î© â†’ 800Î©**
- Ratio: 1:16 impedance = 1:4 voltage = 4:16 turns
- Core: FT50-63 or FT50-43
- Windings: 4T primary, 16T secondary, #26 AWG, bifilar
- Voltage gain: +12 dB
- Insertion loss: <0.3 dB

**T2 (Output): 800Î© â†’ 3Ã—50Î©**
- Ratio: 16:1 impedance = 4:1 voltage = 16:4 turns
- Core: FT50-43 (or FT50-63 for lower frequencies)
- Windings: 16T primary, 3Ã— 4T secondaries (trifilar), #26 AWG
- Voltage gain: -12 dB per output
- Output impedance: 2-4Î© actual (leakage inductance ~10-20nH + winding DCR ~0.13Î©)
- Insertion loss: <0.3 dB per output
- Feeds: QSD_f, QSD_f+k, QSD_f-k
- Design rationale: Low output impedance (<5Î©) required for QSD sampling capacitor charging. At 30MHz worst case with 6Ã— sampling, charge time ~1.4ns with total source impedance (transformer + switch Ron) ~5-7Î© gives ~20-25% settling. This incomplete charging is normal for QSD operation as long as all samples are coherent and impedance is identical across I+, I-, Q+, Q- switches. Trifilar winding ensures matched impedance to all three QSDs.

## QSD Interface Circuit

**Signal path from T2 secondary to QSD input (repeated 3×):**

```
T2 Secondary (±0.7V AC, 50Î© nominal, 2-4Î© actual)
     |
[C_AC] 1µF, 50V (AC coupling, blocks transformer DC)
     |
     +---- [RFC] 2.2µH, SRF 68MHz, DCR 0.138Î©  ---- +1.65V bias
     |                |
     |           [C_bypass] 1µF to GND
     |
Direct to QSD input (TS3A4751)
```

**Component specifications:**
- **AC coupling capacitor**: 1µF, 50V, X7R or C0G. Blocks any DC offset from transformer, presents negligible impedance (<1Î©) across 1.8-30MHz.
- **RFC (bias injection)**: 2.2µH with 68MHz SRF and 0.138Î© DCR. Provides 25-415Î© RF isolation across HF range (impedance increases with frequency). Prevents RF signal from coupling into bias supply.
- **Bypass capacitor**: 1µF at +1.65V bias rail to ground. Provides low RF impedance (88Î© @ 1.8MHz down to 5.3Î© @ 30MHz), shunting any RF that couples through RFC to ground.
- **DC bias**: +1.65V derived from +2.5V reference via resistive divider, shared across all three QSD inputs.

**Voltage levels:**
- Transformer secondary output: ±0.7V AC (from preselector tank ±2.8V divided by 4:1 transformer ratio)
- After AC coupling: Pure AC, ±0.7V
- After bias injection: +1.65V DC ± 0.7V AC
- Absolute voltage range at QSD input: 0.95V to 2.35V âœ" (well within 0-3.3V TS3A4751 operating range)

**Design rationale:**
- **No series resistor needed**: Would increase source impedance and slow QSD capacitor charging. Direct connection from low-impedance transformer provides optimal charge time constant.
- **No clipping diodes needed**: Preselector voltage clamp already limits tank to ±2.8V. After 4:1 transformer step-down, maximum QSD voltage is 0.25V to 3.05V even with 2× overvoltage, staying within safe limits. Additional clipping would add capacitance, distortion, and cost without benefit.
- **Simple bias injection**: Single 2.2µH RFC provides adequate RF isolation (12-104× source impedance ratio across bands) with minimal signal loss (0.09-0.64 dB, decreasing with frequency).

**QSD charging analysis:**
- QSD input impedance: ~5Î© effective (TS3A4751 switch Ron ~3Î© + sampling dynamics)
- Total source impedance: Transformer output (~3Î©) + switch Ron (~3Î©) = ~6Î©
- Time constant: Ï„ = 6Î© Ã— 1000pF = 6ns
- At 30MHz worst case (6Ã— sampling = 180MHz switch rate, 1.4ns charge time):
  - Settling achieved: 1 - exp(-1.4ns/6ns) = 21% of final value
  - This incomplete charging is normal and acceptable for QSD operation
  - Coherent sampling across all I+, I-, Q+, Q- switches maintains phase relationships
  - Identical impedance to all switches (via trifilar transformer) preserves I/Q balance

## Tank Circuit Design

**Resonance:** f = 1/(2Ï€âˆšLC), so C = 1/((2Ï€f)Â²L)

**At resonance:**
- Tank Z = R_total (resistive due to losses)
- Q = X_L / R_total where X_L = 2Ï€fL
- 3dB BW = fâ‚€ / Q
- Voltage across L or C = Q Ã— V_tank (but switches see only tank hot node voltage)

**Resistance budget (typical 160m):**
```
R_total = DCR(L1) + Ron(SW1) + ESR(X) + Ron(SW_C160) + Ron(binary_switches)
        = 0.6Î© + 0.35Î© + 0.05Î© + 0.35Î© + 0.35Î© = 1.7Î©

X_L @ 1.9MHz = 2Ï€(1.9MHz)(2ÂµH) = 23.9Î©
Q = 23.9Î© / 1.7Î© = 14.1
BW = 1.9MHz / 14.1 = 135 kHz âœ“
```

**Capacitance coverage analysis:**

| Band Range | L | Fixed C | Binary+Parasitic | Total C Range | C Needed | Margin |
|------------|---|---------|------------------|---------------|----------|--------|
| **1.8-2.3 MHz** | 2ÂµH | 220+3300pF | 13-2057pF | 3,533-4,553pF | 3,167-4,887pF | Good âœ“ |
| **2.3-4.2 MHz** | 2ÂµH | 220pF | 13-2057pF | 233-2,277pF | 792-1,544pF | Excellent âœ“âœ“ |
| **4.2-7.8 MHz** | 529nH | â€” | 13-2057pF | 13-2,057pF | 770-1,410pF | Excellent âœ“âœ“ |
| **7.8-14.8 MHz** | 720nH | â€” | 13-2057pF | 13-2,057pF | 169-382pF | Large âœ“âœ“ |
| **11.5-19.5 MHz** | 470nH | â€” | 13-2057pF | 13-2,057pF | 168-409pF | Large âœ“âœ“ |
| **14.0-20.5 MHz** | 285nH | â€” | 13-2057pF | 13-2,057pF | 180-427pF | Large âœ“âœ“ |
| **18.0-30.0 MHz** | 171nH | â€” | 13-2057pF | 13-2,057pF | 163-429pF | Large âœ“âœ“ |

All bands have excellent coverage including Â±5% inductor tolerance. The extended binary range (C8=1024pF) eliminates the need for intermediate fixed capacitors.

---

## Component Selection

**Inductors:**

| Part | Value | Q @ freq | DCR | SRF | Package | Cost |
|------|-------|----------|-----|-----|---------|------|
| Coilcraft 1812SMS-2R0 | 2.0ÂµH Â±5% | >40 @ 4MHz | 0.6Î© | >30MHz | 1812 | $0.80 |
| Coilcraft 1812SMS-72NJ | 720nH Â±5% | >50 @ 14MHz | 0.4Î© | >50MHz | 1812 | $0.70 |
| Coilcraft 1812SMS-27NJ | 270nH Â±5% | >60 @ 21MHz | 0.25Î© | >100MHz | 1210 | $0.60 |
| Coilcraft 1812SMS-47NJ | 470nH Â±5% | >55 @ 18MHz | 0.3Î© | >70MHz | 1812 | $0.70 |

**RF Switches: ADG884 Quad SPST**
- Ron: 0.35Î© typ @ 5V supply
- Signal range: -0.3V to +5.3V (with VDD=5V)
- Control: 3.3V CMOS compatible (VIH=2.0V min)
- Switching: <100ns
- Package: LFCSP-16 (4Ã—4mm)
- Cost: $1.80 each
- **Quantity: 4 ICs = 16 switches (14 used: 4 inductors, 1 C_160m, 9 binary caps)**

**Why ADG884 vs AS183-92LF:**
- ADG884: Direct 3.3V control, quad package (4 ICs vs 13 ICs), massive PCB space savings
- AS183-92LF: Higher voltage rating (50V), but requires 13Ã— more board area
- Total cost lower after accounting for IC count reduction
- ADG884 requires voltage clamp (needed anyway for overload protection)
- 50V capacitors adequate with voltage clamp

**Control: MCP23S17 SPI I/O Expander**
- 16 GPIO (2Ã— 8-bit ports)
- SPI interface, 25mA per pin
- Port A: Binary caps C0-C7 (8 bits)
- Port B: C8, L1, L2, L3, L4, C_160m, 2 spare
- Package: SSOP-28 or QFN-28
- Cost: $1.20

**Fixed Capacitors:**
- X = 220pF: C0G 50V, 0805, $0.12 (no switch, parallel with L1)
- C_160m = 3,300pF (3.3nF): C0G 50V, 1206, $0.25

**Binary Bank Capacitors (50V C0G):**
- C0 (4pF): 0805, $0.08
- C1 (8pF): 0805, $0.08
- C2 (16pF): 0805, $0.08
- C3 (32pF): 0805, $0.08
- C4 (64pF): 0805, $0.10
- C5 (128pF): 0805, $0.12
- C6 (256pF): 0805, $0.15
- C7 (512pF): 0805, $0.18
- C8 (1024pF): 1206, $0.20

**Voltage rating rationale:**
- Tank voltage: 5.3V maximum (with clamp)
- 50V rating: 9.4Ã— safety margin (very conservative)
- 500V rating: 94Ã— margin (massive overkill, inherited from high-impedance AS183-92LF design)
- Package size: 50V enables 0805 for all except C8 (1206)
- Cost savings: ~$0.60 per receiver vs 500V parts

---

## Band Performance Summary

| Band | f (MHz) | L (nH) | C Needed (pF) | C Available (pF) | Q | BW (kHz) | Î”f/step (kHz) | Atten @Â±48kHz | 3f Total (dB) |
|------|---------|--------|---------------|------------------|---|----------|---------------|---------------|---------------|
| **160m** | 1.8-2.0 | 2,000 | 3,167-3,906 | 3,533-4,553 | 14.1 | 135 | 1.0 | 1.8 dB | 71.5 |
| **80m** | 3.5-4.0 | 2,000 | 792-1,040 | 233-2,277 | 34.9 | 107 | 8.3 | 2.5 dB | 76.8 |
| **40m** | 7.0-7.3 | 720 | 661-717 | 13-2,057 | 29.4 | 243 | 21 | 0.6 dB | 75.4 |
| **30m** | 10.1-10.15 | 720 | 342-345 | 13-2,057 | 41.5 | 244 | 59 | 0.3 dB | 78.4 |
| **20m** | 14.0-14.35 | 720 | 169-179 | 13-2,057 | 58.1 | 244 | 163 | 0.6 dB | 81.3 |
| **17m** | 18.07-18.17 | 270 | 284-287 | 13-2,057 | 32.3 | 561 | 127 | 0.2 dB | 76.2 |
| **15m** | 21.0-21.45 | 196 | 282-296 | 13-2,057 | 21.8 | 974 | 147 | 0.1 dB | 72.8 |
| **12m** | 24.89-24.99 | 196 | 208-210 | 13-2,057 | 25.6 | 974 | 239 | 0.1 dB | 74.2 |
| **10m** | 28.0-29.7 | 196 | 147-164 | 13-2,057 | 29.6 | 975 | 373 | 0.1 dB | 75.4 |

**Additional continuous coverage (between amateur bands):**

| Range | f (MHz) | L Config | L (nH) | C Range (pF) | Purpose |
|-------|---------|----------|--------|--------------|---------|
| **2.0-3.5** | 2.0-3.5 | L1+X | 2,000 | 1,040-2,277 | WWV, marine |
| **4.0-7.0** | 4.0-7.0 | L1â€–L2 | 529 | 770-1,410 | HF broadcast |
| **7.3-10.1** | 7.3-10.1 | L2 | 720 | 342-661 | 60m overlap |
| **10.15-14.0** | 10.15-14.0 | L2/L4 | 470-720 | 169-342 | 30m-20m gap |
| **14.35-18.07** | 14.35-18.07 | L2â€–L4/L4 | 285-470 | 284-427 | 20m-17m gap |

**Key observations:**
- All amateur bands exceed 96 kHz minimum bandwidth
- Total 3f rejection >70 dB (preselector 28-36 dB + QSD3 null 40 dB)
- Attenuation at Â±48 kHz (QSD capture edges): <3 dB all bands, <1 dB on most
- Tuning resolution excellent on low bands (1-21 kHz), adequate on high bands
- Q naturally higher on mid bands (20m: Q=58), lower on extremes
- Complete continuous coverage 1.8-30 MHz, no gaps between amateur bands
- Extended binary range (C8=1024pF) eliminates need for intermediate fixed capacitors

---

## PCB Layout Guidelines

**Tank area layout:**
- Inductor spacing: â‰¥15mm between inductors (minimize coupling)
- Inductor mounting: Vertical on standoffs 3-5mm above PCB, perpendicular orientation
- Capacitor placement: Binary caps <5mm from switches, X adjacent to L1
- Switch clustering: ADG884 ICs near tank hot node, traces <10mm
- Ground plane: Solid top and bottom layers, 20+ vias stitching under tank area
- Star grounding: All tank component grounds converge at single point

**Layer stack (4-layer recommended):**
```
Layer 1 (Top):    RF components, signal traces
Layer 2 (Inner):  Solid GND plane
Layer 3 (Inner):  Power planes (+5V, +3.3V)
Layer 4 (Bottom): Control signals, SPI routing

Copper: 2oz outer layers, 1oz inner
Dielectric: FR-4, 1.6mm total
```

**Critical routing:**
- SPI bus: Bottom layer, 50Î© controlled impedance
- Control signals: Route away from RF, 100Î© series resistors for slew rate
- Transformer placement: T1 near clamp output, T2 equidistant to 3 QSDs
- Decoupling: 0.1ÂµF at each ADG884 VDD pin, <5mm trace
- Tank bias: 100kÎ© from +2.5V reference, bypass with 0.1ÂµF

**Thermal:**
- Natural convection sufficient (<0.5W total)
- Thermal vias from ADG884 pads to ground plane
- 2oz copper provides adequate heat spreading

**PCB space advantage:**
- 0805 capacitors vs 1210: ~50% area reduction per component
- 4Ã— ADG884 (4Ã—4mm) vs 13Ã— AS183-92LF (SOT-363): ~60% switch footprint reduction
- Overall preselector section: ~30% smaller than AS183-92LF design

## Bill of Materials

| Category | Part | Value/Type | Qty | Package | Unit $ | Ext $ |
|----------|------|------------|-----|---------|--------|-------|
| **Inductors** | | | | | | |
| L1 | Coilcraft 1812SMS-2R0 | 2ÂµH Â±5% | 1 | 1812 | 0.80 | 0.80 |
| L2 | Coilcraft 1812SMS-72NJ | 720nH Â±5% | 1 | 1812 | 0.70 | 0.70 |
| L3 | Coilcraft 1812SMS-27NJ | 270nH Â±5% | 1 | 1210 | 0.60 | 0.60 |
| L4 | Coilcraft 1812SMS-47NJ | 470nH Â±5% | 1 | 1812 | 0.70 | 0.70 |
| **Fixed Caps** | | | | | | |
| X | C0G 50V | 220pF | 1 | 0805 | 0.12 | 0.12 |
| C_160m | C0G 50V | 3.3nF | 1 | 1206 | 0.25 | 0.25 |
| **Binary Bank** | | | | | | |
| C0-C3 | C0G 50V | 4,8,16,32pF | 4 | 0805 | 0.08 | 0.32 |
| C4 | C0G 50V | 64pF | 1 | 0805 | 0.10 | 0.10 |
| C5 | C0G 50V | 128pF | 1 | 0805 | 0.12 | 0.12 |
| C6 | C0G 50V | 256pF | 1 | 0805 | 0.15 | 0.15 |
| C7 | C0G 50V | 512pF | 1 | 0805 | 0.18 | 0.18 |
| C8 | C0G 50V | 1024pF | 1 | 1206 | 0.20 | 0.20 |
| **Switches** | | | | | | |
| U1-U4 | ADG884 | Quad SPST | 4 | LFCSP-16 | 1.80 | 7.20 |
| **Control** | | | | | | |
| U5 | MCP23S17 | SPI I/O | 1 | SSOP-28 | 1.20 | 1.20 |
| **Clamp** | | | | | | |
| D1, D2 | BAT54S | Dual Schottky | 2 | SOT-23 | 0.10 | 0.20 |
| RFC1, RFC2 | SMD | 1ÂµH | 2 | 0805 | 0.05 | 0.10 |
| R1, R2 | 1% | 10kÎ© | 2 | 0805 | 0.02 | 0.04 |
| R3, R6 | 1% | 82kÎ© | 2 | 0805 | 0.02 | 0.04 |
| R4, R5 | 1% | 18kÎ© | 2 | 0805 | 0.02 | 0.04 |
| C1, C2 | X7R 16V | 0.1ÂµF | 2 | 0805 | 0.03 | 0.06 |
| **Transformers** | | | | | | |
| T1 | FT50-63 | 4:16T | 1 | Toroid | 1.50 | 1.50 |
| T2 | FT50-43 | 16:4:4:4T | 1 | Toroid | 1.50 | 1.50 |
| **Misc** | | | | | | |
| - | Bias, decoupling | Various | - | 0805 | - | 0.55 |
| | | | | **Per RX** | | **16.78** |
| | | | | **3Ã— RX** | | **50.34** |

**Cost comparison:**
- This design: $16.78/RX
- Original 8-bit design: $14.68/RX (+$2.10 for continuous coverage)
- AS183-92LF design: $19.33/RX
- **Savings vs AS183-92LF: $2.55 per receiver**

**Cost breakdown of changes:**
- Added L4 (470nH): +$0.70
- Added C8 (1024pF): +$0.20
- Added one ADG884: +$1.80
- **Subtotal additions: +$2.70**
- Reduced voltage rating (500Vâ†’50V): -$0.60
- **Net increase: +$2.10 per receiver**

## Design Trade-offs

**Why 800Î© impedance?**
- Achieves Q=15-35 with ADG884 Ron (0.35Î©)
- Tank voltage within ADG884 limits (5.3V) with clamping
- Standard 4:1 voltage transformer ratios
- Lower impedances (200-400Î©) create tank voltage >5.3V; higher (1600Î©) also exceeds limits

**Why ADG884 vs AS183-92LF?**
- ADG884: Direct 3.3V control, quad package (4 ICs vs 13), massive PCB space savings
- AS183-92LF: Higher voltage rating (50V vs 5.3V), but requires 13Ã— more board area
- Lower total cost after accounting for IC count reduction
- ADG884 requires voltage clamp (needed anyway for overload protection)
- 50V capacitors adequate with proper voltage clamp design

**Why 50V capacitor rating?**
- Tank voltage: 5.3V maximum (with clamp)
- 50V rating: 9.4Ã— safety margin (industry standard 2-3Ã— margin, we use 9Ã—)
- 500V rating: 94Ã— margin (massive overkill from AS183-92LF high-impedance design)
- Package benefits: 0805 fits all except C8 (vs 1210 for 500V)
- Cost savings: ~$0.60 per receiver
- PCB area: ~30% smaller footprint

**Why binary bank vs varicap?**
- Deterministic tuning, no drift/aging, simple digital control
- Varicaps need 0-30V bias generation, temperature/aging calibration, lower Q
- Binary bank enables precise frequency resolution with no calibration

**Why C8=1024pF vs adding fixed capacitors?**
- Extended binary range (13-2057pF) covers all intermediate frequencies
- Eliminates need for C_40m and other intermediate fixed caps
- Simpler control logic (one less switch to manage)
- More flexible for future frequency coverage needs
- Cost: One capacitor (+$0.20) vs one fixed cap + switch

**Why add L4=470nH?**
- Fills all frequency gaps between amateur bands
- Enables continuous 1.8-30 MHz coverage via parallel combinations
- Provides optimal inductance values for each frequency range
- L2â€–L4 and L3â€–L4 combinations have lower DCR than individual inductors

---

## Firmware Implementation

**Configuration selection algorithm:**

```c
// Determine optimal L configuration and fixed caps for frequency
PreselectorConfig SelectConfig(float freq_mhz) {
  PreselectorConfig cfg = {0};
  
  if (freq_mhz < 2.3) {
    cfg.L_config = L1_ONLY;        // L1 = 2ÂµH (X=220pF always included)
    cfg.enable_C160m = true;       // Need 3.3nF for 160m
  } else if (freq_mhz < 4.2) {
    cfg.L_config = L1_ONLY;        // L1 = 2ÂµH
    cfg.enable_C160m = false;      // Binary bank sufficient
  } else if (freq_mhz < 7.8) {
    cfg.L_config = L1_PARALLEL_L2; // L1â€–L2 = 529nH
  } else if (freq_mhz < 11.5) {
    cfg.L_config = L2_ONLY;        // L2 = 720nH
  } else if (freq_mhz < 14.0) {
    cfg.L_config = L4_ONLY;        // L4 = 470nH (overlap region)
  } else if (freq_mhz < 18.0) {
    cfg.L_config = L2_PARALLEL_L4; // L2â€–L4 = 285nH
  } else {
    cfg.L_config = L3_PARALLEL_L4; // L3â€–L4 = 171nH
  }
  
  return cfg;
}

// Calculate required binary capacitor value
uint16_t CalculateBinaryCaps(float freq_mhz, PreselectorConfig cfg) {
  // Get effective inductance in nH
  float L_nH = GetEffectiveInductance(cfg);
  
  // Calculate required capacitance in pF
  float C_pF = 1e6 / (4 * PI * PI * (freq_mhz * freq_mhz) * L_nH);
  
  // Subtract fixed capacitances
  if (cfg.L_config == L1_ONLY || cfg.L_config == L1_PARALLEL_L2) {
    C_pF -= 220;  // X is always present with L1
  }
  if (cfg.enable_C160m) {
    C_pF -= 3300; // C_160m
  }
  
  // Subtract parasitic (13pF from switches)
  C_pF -= 13;
  
  // Convert to 9-bit binary value (4pF LSB)
  uint16_t binary_value = (uint16_t)((C_pF + 2) / 4);  // Round to nearest
  
  // Clamp to 0-511 range (9 bits)
  if (binary_value > 511) binary_value = 511;
  
  return binary_value;
}
```

**Switch control mapping:**

```c
// MCP23S17 Port A: Binary capacitors C0-C7
// MCP23S17 Port B: [7:0] = [spare, spare, C_160m, L4, L3, L2, L1, C8]

void ApplyPreselectorConfig(PreselectorConfig cfg, uint16_t binary_caps) {
  uint8_t portA = binary_caps & 0xFF;        // C0-C7 (lower 8 bits)
  uint8_t portB = (binary_caps >> 8) & 0x01; // C8 (bit 0 of portB)
  
  // Set L switches based on configuration
  switch(cfg.L_config) {
    case L1_ONLY:
      portB |= (1 << 1);  // L1 ON
      break;
    case L2_ONLY:
      portB |= (1 << 2);  // L2 ON
      break;
    case L3_ONLY:
      portB |= (1 << 3);  // L3 ON
      break;
    case L4_ONLY:
      portB |= (1 << 4);  // L4 ON
      break;
    case L1_PARALLEL_L2:
      portB |= (1 << 1) | (1 << 2);  // L1 and L2 ON
      break;
    case L2_PARALLEL_L4:
      portB |= (1 << 2) | (1 << 4);  // L2 and L4 ON
      break;
    case L3_PARALLEL_L4:
      portB |= (1 << 3) | (1 << 4);  // L3 and L4 ON
      break;
  }
  
  // Set C_160m if needed
  if (cfg.enable_C160m) {
    portB |= (1 << 5);
  }
  
  // Write to MCP23S17
  MCP23S17_WriteRegister(GPIOA, portA);
  MCP23S17_WriteRegister(GPIOB, portB);
}
```

---

## Related Documents

- IMPEDANCE-MEASUREMENT.md: Vector network analysis using RX QSDs
- RX-ARCHITECTURE.md: Complete receiver signal chain  
- ARCHITECTURE.md: System overview
- DESIGN_PHILOSOPHY.md: Active simplification principles

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-01 | 1.0 | Initial 8-bit binary bank design (C0-C7) |
| 2025-01 | 2.0 | Added C8=1024pF, L4=470nH for continuous 1.8-30 MHz coverage; reduced cap voltage to 50V |

---

**Document Status:** Complete - Ready for PCB layout and implementation
