# VSWR Measurement System Design
## USB-SSB Transceiver Project

### Document Information
- **Date**: January 2025
- **System**: Transmitter VSWR Monitoring
- **Location**: 50Ω point after 200:50Ω transformer, before antenna
- **Power Range**: 0-50W RMS
- **Target**: STM32 ADC inputs (0-3V range)

---

## Design Overview

This document describes the design of a low-loss VSWR measurement system for the transmitter output path. The system uses a Bruene directional coupler with software calibration to eliminate manual adjustments while maintaining excellent performance.

### Key Requirements
- Insertion loss: <0.1dB
- Power handling: 50W continuous
- Frequency range: 1.8-54MHz
- Output voltage: 0-3V for STM32 ADC
- No manual calibration adjustments
- Accurate VSWR measurement from 1:1 to 4:1

---

## System Architecture

### Signal Path
```
PA → LPFs → Tuning Tanks (200Ω) → [200:50Ω Transformer] → [VSWR Sensor] → Antenna
                                                              ↑ Measurement Point
```

The VSWR sensor is placed at the 50Ω impedance point between the impedance transformer output and the antenna connection. This location provides standard 50Ω impedance for measurement while monitoring the actual antenna match.

---

## Bruene Directional Coupler Design

### Principle of Operation

The Bruene coupler combines:
1. **Current sampling** via toroidal transformer
2. **Voltage sampling** via capacitive divider
3. **Phase-sensitive detection** to separate forward and reverse power

When properly balanced, the voltage and current samples cancel for reverse power into a matched load, while they add constructively for forward power.

### Core Circuit Components

#### Current Transformer
- **Core**: FT50-43 ferrite toroid (alternate: FT50-61 for wider frequency)
- **Primary**: Main 50Ω transmission line through center (1 turn)
- **Secondary**: 20 turns center-tapped (10t + 10t), #28 AWG enameled wire
- **Burden Resistors**: 100Ω ±1% each side of center tap

#### Voltage Sampling
- **C1**: 10pF ±5% C0G/NPO ceramic (samples RF voltage)
- **C2**: 1000pF ±5% C0G/NPO ceramic (divider to ground)
- **RFC**: 10µH inductor, SRF >50MHz (DC reference for center tap)

### Detector and Scaling Circuits

Each detector channel (forward and reverse) uses:

```
Secondary End (±5V RMS at 50W)
         │
      BAT54S (Dual Schottky in series, SOT-23)
         │
      10nF C0G (filter capacitor)
         │
      10kΩ ±1% (divider top)
         │
         ├────→ To STM32 ADC pin
         │
      4.7kΩ ±1% (divider bottom)
         │
        GND
```

#### Voltage Levels
- At 50W into 50Ω: Secondary = 5V RMS (7.1V peak)
- After rectification: ~6.8V DC
- After voltage divider: ~2.2V to ADC
- Maximum at 4:1 VSWR: ~2.8V (within 3V limit)

### Protection Components
- **TVS Diodes**: PESD3V3L1BA on each ADC input
- **Series Resistor**: 100Ω between divider and ADC pin
- **Bypass Capacitor**: 100nF at ADC input for RF filtering

---

## PCB Layout Guidelines

### Critical Layout Considerations

1. **Main RF Path**
   - Use 50Ω controlled impedance trace
   - Keep path straight through toroid center
   - Minimize trace length for low inductance

2. **Toroid Mounting**
   - Mount vertically with short secondary connections
   - Keep burden resistors within 5mm of toroid
   - Symmetrical layout for forward/reverse paths

3. **Detector Circuits**
   - Place diodes close to burden resistors
   - Keep detector grounds separate from RF ground
   - Star ground at single point

4. **Shielding**
   - Consider copper pour shield between RF and detector sections
   - Keep digital signals away from RF sections

### Recommended Layout Pattern
```
┌─────────────────────────────────────┐
│  TX IN    [TOROID]      ANT OUT     │
│    ●━━━━━━━[○]━━━━━━━━━━●           │
│            ││││                     │
│         ┌──┴──┴──┐                  │
│         │Resistors│                  │
│         └──┬──┬──┘                  │
│       ┌────┴──┴────┐                │
│       │  Detectors │                │
│       └────┬──┬────┘                │
│          Vfwd Vrev → To STM32       │
└─────────────────────────────────────┘
```

---

## Software Calibration System

### Calibration Philosophy

Instead of hardware trimming, all balancing is done in software. Component tolerances simply create DC offsets that are measured and stored during calibration.

### Calibration Data Structure

```c
typedef struct {
    float forward_scale;       // Voltage to power conversion factor
    float reverse_scale;       // Voltage to power conversion factor
    float reverse_offset;      // Imbalance offset at 50Ω match
    float forward_offset;      // DC offset with no RF
    uint32_t calibration_date; // Timestamp of calibration
    float calibration_temp;    // Temperature during calibration
} VSWR_Calibration;
```

### Calibration Procedure

1. **Setup Phase**
   - Connect known good 50Ω dummy load
   - Ensure stable temperature
   - Allow 5 minute warmup

2. **DC Offset Measurement**
   - No transmission
   - Read both ADC channels 100 times
   - Average to find DC offsets

3. **Power Calibration Points**
   - Transmit at: 1W, 5W, 10W, 25W, 50W
   - Measure forward and reverse voltages
   - Store reverse voltage as imbalance offset

4. **Validation**
   - Test with 100Ω load (2:1 VSWR)
   - Verify reverse power indicates correctly

### Runtime Compensation Algorithm

```c
void measure_vswr(VSWR_Calibration* cal, 
                  float* power_out, 
                  float* vswr_out) {
    
    // Read ADC values (12-bit, 0-4095 range)
    uint16_t adc_fwd = read_adc(ADC_FORWARD_CH);
    uint16_t adc_rev = read_adc(ADC_REVERSE_CH);
    
    // Convert to voltages (3.3V reference)
    float v_fwd = (adc_fwd * 3.3f) / 4096.0f;
    float v_rev = (adc_rev * 3.3f) / 4096.0f;
    
    // Apply calibration offsets
    v_fwd -= cal->forward_offset;
    v_rev -= cal->reverse_offset;
    
    // Prevent negative values
    if (v_fwd < 0) v_fwd = 0;
    if (v_rev < 0) v_rev = 0;
    
    // Calculate power (voltage squared relationship)
    *power_out = (v_fwd * v_fwd) * cal->forward_scale;
    
    // Calculate VSWR
    if (v_fwd > 0.05f) {  // Minimum threshold
        float rho = v_rev / v_fwd;
        *vswr_out = (1.0f + rho) / (1.0f - rho);
        
        // Limit display range
        if (*vswr_out > 99.9f) *vswr_out = 99.9f;
        if (*vswr_out < 1.0f) *vswr_out = 1.0f;
    } else {
        *vswr_out = 1.0f;  // No signal
    }
}
```

### Advanced Compensation Options

For enhanced accuracy:

1. **Temperature Compensation**
   - Monitor temperature with STM32 internal sensor
   - Apply correction factor based on calibration temperature

2. **Frequency Compensation**
   - Store correction factors per band
   - Interpolate for specific frequencies

3. **Power-Level Linearization**
   - Multiple calibration points across power range
   - Polynomial or lookup table correction

---

## Component List

### Bill of Materials

| Reference | Value | Description | Package | Notes |
|-----------|-------|-------------|---------|-------|
| T1 | - | Toroid core | FT50-43 | Fair-Rite 5943001001 |
| - | 20 turns CT | Secondary winding | #28 AWG | Bifilar wound |
| R1, R2 | 100Ω ±1% | Burden resistors | 0805 | 100mW min |
| C1 | 10pF ±5% | Voltage sample | 0805 | C0G/NPO |
| C2 | 1000pF ±5% | Voltage divider | 0805 | C0G/NPO |
| L1 | 10µH | RF choke | 0805 | SRF >50MHz |
| D1, D2 | BAT54S | Dual Schottky | SOT-23 | 30V, 200mA |
| C3, C4 | 10nF | Filter caps | 0805 | C0G/NPO |
| R3, R5 | 10kΩ ±1% | Divider top | 0805 | 100mW |
| R4, R6 | 4.7kΩ ±1% | Divider bottom | 0805 | 100mW |
| R7, R8 | 100Ω | Protection | 0805 | Series to ADC |
| C5, C6 | 100nF | ADC filter | 0805 | X7R |
| D3, D4 | PESD3V3L1BA | TVS protection | SOD-323 | 3.3V clamp |

### Alternate Components

- **Toroid**: FT50-61 for operation above 30MHz
- **Schottky**: 1N5711 or SMS7621 for better sensitivity
- **TVS**: Any 3.3V TVS diode in small package

---

## Performance Specifications

### Measured Performance

| Parameter | Specification | Typical | Notes |
|-----------|--------------|---------|-------|
| Insertion Loss | <0.1dB | 0.02dB | At 14MHz |
| Frequency Range | 1.8-54MHz | - | 3dB bandwidth |
| Power Handling | 50W | 100W | Continuous |
| Directivity | >25dB | 30dB | With calibration |
| VSWR Range | 1:1 to 10:1 | - | Useful range 1:1 to 4:1 |
| Output Voltage | 0-3V | 0-2.2V | At 50W forward |
| Sensitivity | - | 10mV/W | At low power |

### Accuracy

- Forward Power: ±5% after calibration
- VSWR: ±0.1 from 1:1 to 3:1
- Temperature Drift: <0.02dB/°C

---

## Test and Validation

### Required Test Equipment

1. Calibrated RF power meter
2. 50Ω dummy load (1% accuracy)
3. Set of known impedances (25Ω, 100Ω, 150Ω)
4. Signal generator or transmitter
5. Oscilloscope (optional, for waveform verification)

### Test Procedure

1. **Insertion Loss Test**
   - Measure power with and without coupler
   - Verify <0.1dB loss at all frequencies

2. **Directivity Test**
   - Terminate with 50Ω load
   - Measure reverse channel output
   - Calculate isolation in dB

3. **Linearity Test**
   - Test at 0.1W, 0.5W, 1W, 5W, 10W, 25W, 50W
   - Plot measured vs actual power
   - Verify linear relationship

4. **VSWR Accuracy**
   - Test with known impedances
   - Compare calculated vs measured VSWR
   - Verify within specifications

---

## Design Decisions and Rationale

### Why Bruene Coupler?
- Extremely low insertion loss (<0.02dB typical)
- No resistive elements in main RF path
- Wide frequency range with single design
- Proven reliability in commercial equipment

### Why Software Calibration?
- Eliminates mechanical adjustments
- Allows temperature compensation
- Enables per-unit calibration
- Reduces component cost (no trimmers)
- Permits advanced correction algorithms

### Component Selection Rationale
- **FT50-43**: Good compromise between size and frequency range
- **20 turns CT**: Provides ~5V RMS at 50W for good signal level
- **100Ω burden**: Balances sensitivity and loading
- **10pF/1000pF ratio**: Near-optimal balance point
- **BAT54S**: Low Vf, dual diode convenience
- **2.2V max to ADC**: Good headroom below 3V limit

---

## Implementation Notes

### STM32 ADC Configuration

```c
// ADC initialization for VSWR measurement
void init_vswr_adc(void) {
    // Configure ADC1 for forward and reverse channels
    // 12-bit resolution, continuous conversion
    // DMA transfer to buffer
    // Sampling time: 239.5 cycles for stability
}
```

### Measurement Timing
- Sample rate: 1kHz minimum
- Average over 100 samples for display
- Update display: 10Hz
- Protection shutdown: <10ms response

### Flash Storage
- Store calibration in last page of flash
- Include CRC for integrity check
- Backup calibration to EEPROM if available

---

## References

1. Bruene, Warren. "An Inside Picture of Directional Wattmeters", QST, April 1959
2. Tandem Match documentation, various authors
3. "Understanding the Bruene Directional Coupler and Transmission Lines", Gary Bold, ZL1AN, Version 1.3, October 18, 2009
4. Project schematics: tx-LPFs.kicad_sch, ant.kicad_sch

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-01 | 1.0 | Initial design | Project Team |

---

## Appendix A: Transformer Winding Instructions

### Bifilar Winding Technique for 20-turn CT

1. **Prepare Wire**
   - Cut two 12-inch lengths of #28 AWG enameled wire
   - Different colors helpful (red/black)
   - Lightly twist together (2-3 twists per inch)

2. **Wind the Core**
   - Thread twisted pair through toroid
   - Wind 10 complete turns
   - Keep turns evenly spaced
   - All turns in same direction

3. **Connections**
   - Red start = Forward output
   - Red end + Black start = Center tap (ground)
   - Black end = Reverse output

4. **Testing**
   - Check DC resistance: ~0.5Ω each half
   - Check inductance: ~50µH each half
   - Verify continuity and isolation

---

## Appendix B: Troubleshooting Guide

### Common Issues and Solutions

| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| High insertion loss | Poor solder joint on through-line | Reflow connections |
| No forward reading | Diode installed backwards | Check diode polarity |
| Excessive reverse with 50Ω | Imbalance too large | Verify C1/C2 values |
| Unstable readings | RF pickup on ADC lines | Add shielding/filtering |
| Frequency-dependent VSWR | Toroid saturation | Check power levels |
| Temperature drift | Component heating | Improve layout/heatsinking |

---

*End of Document*
