# Antenna Impedance Measurement & Tuning Architecture

## Core Concept

Use existing receiver QSDs for vector network analysis. Eliminates dedicated VSWR hardware, enables deterministic tuning.

## Measurement System

### Signal Path
```
TX → Bruene Coupler (FT50-43, 1T primary, 3-4T secondaries) → Antenna
         ↓                    ↓
     Forward              Reverse
         ↓                    ↓
    [AC+Bias 1.65V]     [AC+Bias 1.65V]
         ↓                    ↓
     Mux→QSD1            Mux→QSD2
```

**Levels**: ~150mV RMS @ 1W, ~1V RMS @ 50W → fits QSD 0-3.3V range after bias

### Complex Impedance Calculation

QSDs output I/Q for each path:
```
V_fwd = I_fwd + j·Q_fwd
V_rev = I_rev + j·Q_rev

Γ = V_rev / V_fwd              (complex reflection coefficient)
VSWR = (1 + |Γ|) / (1 - |Γ|)  (from magnitude)
Z = 50·(1 + Γ)/(1 - Γ) = R + j·X  (antenna impedance)
```

**Phase coherence critical**: Both QSDs must sample synchronously to preserve phase relationship.

## FPGA Clocking

**Normal RX**: QSD1=4f, QSD2=4(f+k), QSD3=4(f-k)  
**Measurement**: All QSDs at 4f_measurement (synchronized)

Simple register write to reconfigure.

## Deterministic Tuning

From Z = R + j·X, calculate component values directly:

1. **Cancel X**: If X>0 add series C=1/(2πfX), if X<0 add series L=|X|/(2πf)
2. **Match R**: Select transformer tap or L-network topology for R→50Ω conversion
3. **Set relays**: Single iteration, no trial-and-error

Example: Z=73+j42Ω @ 7.15MHz → C=534pF series, 1.5:1 transformer tap → Done in 50-100ms

## Safety Protocols

### Low Power Measurement
- Transmit at 0.5-1W during measurement (survives any mismatch)
- Calculate tuning, then return to full power

### Zero-Voltage Switching
EER architecture enables:
1. Drop TX envelope to 0V
2. Wait 0.5ms
3. Switch tuner relays (no voltage/current)
4. Wait 2ms settling
5. Ramp power back up

Extends relay life 10⁵→10⁸ operations.

## Measurement Sequence

1. Mux: Fwd→QSD1, Rev→QSD2; FPGA: sync clocks to 4f
2. TX at 0.5-1W for 10-20ms, sample I/Q
3. Browser: Calculate Γ→Z→tuner settings
4. STM32: Zero-volt switch relays
5. Return to normal RX

**Total: 50-100ms**

## Benefits

**Eliminates**: Diode detectors, voltage dividers, dedicated VSWR hardware (~$2, 2 ADC channels)  
**Gains**: VSWR + complex Z + Smith chart + frequency sweeps + predictive tuning

**Active simplification**: QSDs provide superset of VSWR functionality, making dedicated hardware redundant.

## Key Requirements

- Bruene secondaries: 3-4 turns each (light coupling for direct QSD levels)
- Mux switching: Normal RX ↔ Measurement paths per QSD
- Synchronous QSD clocking from FPGA
- Low-power measurement + zero-volt relay switching
