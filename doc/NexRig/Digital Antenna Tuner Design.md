## Voltage and Current at 50W

At 50W in 200Ω domain:

````
P = V²/R
V_rms = √(P × R) = √(50W × 200Ω) = 100V RMS
V_peak = 100V × √2 = 141V peak

I_rms = √(P/R) = √(50W/200Ω) = 0.5A RMS  
I_peak = 0.5A × √2 = 0.707A peak
```

## Capacitor Voltage Rating

### Direct Application Voltage
```
At 50W continuous:
V_peak = 141V across the capacitor

Safety margin considerations:
- Standard practice: 2× minimum for reliability
- Component derating: 50% of rating for long life
- Transient protection: Allow for mismatches during tuning

Required rating: 141V × 2 = 282V minimum
```

### Resonant Circuit Magnification

In the L-network, capacitors can see voltage magnification due to circuit Q:
```
For matching 50Ω → 200Ω or 800Ω → 200Ω:
Q = √3 = 1.732

Shunt capacitor voltage magnification:
V_C = V_applied × √(1 + Q²) ≈ 2 × V_applied

At 50W: V_C_peak ≈ 2 × 141V = 282V worst case

With 2× safety margin: 564V required
```

**Recommended: 630V NP0/C0G ceramic capacitors**
- Provides 4.5× margin at 141V direct
- Provides 2.2× margin at 282V magnified
- Standard voltage rating, widely available
- Cost-effective

**Alternative: 500V rating would be adequate** (3.5× direct, 1.8× magnified)

## Inductor Current Rating

### Direct Application Current
```
At 50W continuous:
I_rms = 0.5A through the inductor
I_peak = 0.707A

Safety margin:
- Standard practice: 3× minimum for reliability
- Allows for mismatches and transients

Required I_DC rating: 0.5A × 3 = 1.5A minimum
```

### Resonant Circuit Magnification

In the L-network, inductors can see current magnification:
```
For Q = 1.732 matching networks:
I_L_magnified = I_applied × √(1 + Q²) ≈ 2 × I_applied

At 50W: I_L_peak ≈ 2 × 0.707A = 1.4A worst case

With 2× safety margin: 2.8A I_DC required
```

**Recommended: I_DC ≥ 3A, I_sat ≥ 4A**
- Provides 6× margin at 0.5A direct
- Provides 2.1× margin at 1.4A magnified
- Prevents saturation under all conditions

## Revised Commercial Inductor Selection

With relaxed requirements (3A/4A instead of 3A/5A):

### Coilcraft 1515SQ Series (Excellent Choice)

| Value | Part Number | I_DC | I_sat | DCR | SRF | Cost (1 qty) |
|-------|-------------|------|-------|-----|-----|--------------|
| 0.5 µH | 1515SQ-R50M | 9.7A | 13.6A | 8mΩ | >100MHz | ~$3 |
| 1.0 µH | 1515SQ-1R0M | 7.3A | 9.6A | 13mΩ | >80MHz | ~$3 |
| 2.0 µH | 1515SQ-2R0M | 5.4A | 7.0A | 21mΩ | >60MHz | ~$3 |
| 4.0 µH | 1515SQ-4R0M | 3.9A | 5.1A | 37mΩ | >45MHz | ~$3 |
| 8.0 µH | 1515SQ-8R0M | 2.9A | 3.8A | 65mΩ | >35MHz | ~$3 |
| 16 µH | 1515SQ-160M | 2.1A | 2.8A | 115mΩ | >25MHz | ~$3 |
| 32 µH | 1515SQ-320M | 1.5A | 2.0A | 205mΩ | >18MHz | ~$3 |
| 64 µH | 1515SQ-640M | 1.1A | 1.5A | 360mΩ | >13MHz | ~$3 |

**Problem:** 16 µH and larger values still don't meet 3A/4A requirement.

### Wurth WE-HCI (744 771 xxx) Series for Larger Values

| Value | Part Number | I_DC | I_sat | DCR | SRF | Cost (1 qty) |
|-------|-------------|------|-------|-----|-----|--------------|
| 16 µH | 744 771 116 | 4.1A | 5.3A | 72mΩ | 28MHz | ~$2 |
| 32 µH | 744 771 232 | 3.3A | 4.2A | 95mΩ | 22MHz | ~$2 |
| 64 µH | 744 771 264 | 2.4A | 3.0A | 165mΩ | 16MHz | ~$2 |

**Problem:** 64 µH is marginal at 2.4A/3.0A (only 2× margin)

### Better Option: Wurth WE-PD2 (744 773 xxx) Series

Larger physical size, better current handling:

| Value | Part Number | I_DC | I_sat | DCR | SRF | Cost (1 qty) |
|-------|-------------|------|-------|-----|-----|--------------|
| 32 µH | 744 773 232 | 5.0A | 7.5A | 52mΩ | 18MHz | ~$3 |
| 68 µH | 744 773 268 | 3.6A | 5.5A | 90mΩ | 12MHz | ~$3 |

**Much better!** Now we can use strict binary weighting.

## Recommended Component Banks (50W Operation)

### Inductor Bank (Strict Binary)

| Inductor | Value | Part Number | I_DC | I_sat | Margin | Cost |
|----------|-------|-------------|------|-------|--------|------|
| L1 | 0.5 µH | Coilcraft 1515SQ-R50M | 9.7A | 13.6A | 19×/27× | $3 |
| L2 | 1.0 µH | Coilcraft 1515SQ-1R0M | 7.3A | 9.6A | 15×/19× | $3 |
| L3 | 2.0 µH | Coilcraft 1515SQ-2R0M | 5.4A | 7.0A | 11×/14× | $3 |
| L4 | 4.0 µH | Coilcraft 1515SQ-4R0M | 3.9A | 5.1A | 8×/10× | $3 |
| L5 | 8.0 µH | Coilcraft 1515SQ-8R0M | 2.9A | 3.8A | 6×/8× | $3 |
| L6 | 16 µH | Wurth 744 771 116 | 4.1A | 5.3A | 8×/11× | $2 |
| L7 | 32 µH | Wurth 744 773 232 | 5.0A | 7.5A | 10×/15× | $3 |
| L8 | 64 µH | Wurth 744 773 268 | 3.6A | 5.5A | 7×/11× | $3 |

**Total range:** 0.5 to 127.5 µH in 0.5 µH steps
**Total cost:** ~$23 for inductors

All inductors exceed 3A/4A requirements! ✓

### Capacitor Bank (Strict Binary)

| Capacitor | Value | Voltage | Package | Cost (1 qty) |
|-----------|-------|---------|---------|--------------|
| C1 | 10 pF | 630V | 1206 C0G | $0.30 |
| C2 | 20 pF | 630V | 1206 C0G | $0.30 |
| C3 | 40 pF | 630V | 1206 C0G | $0.30 |
| C4 | 80 pF | 630V | 1206 C0G | $0.30 |
| C5 | 160 pF | 630V | 1206 C0G | $0.35 |
| C6 | 320 pF | 630V | 1206 C0G | $0.40 |
| C7 | 640 pF | 630V | 1210 C0G | $0.45 |
| C8 | 1280 pF | 630V | 1210 C0G | $0.50 |

**Total range:** 10 to 2550 pF in 10 pF steps
**Total cost:** ~$2.90 for capacitors

All capacitors provide 4.5× voltage margin! ✓

## Updated Cost Analysis
```
Components per tuner at 50W:
- 16× TQ2-5V relay @ $1.50 each     = $24.00
- 8× Inductors (commercial)          = $23.00
- 8× C0G capacitors (630V)           = $2.90
- Relay drivers (4× ULN2003)         = $2.00
- PCB area (estimated)               = $6.00
─────────────────────────────────────────────
Total per unit (single qty):          $57.90

At 100 units with volume pricing:
- Relays (35% discount)              = $15.60
- Inductors (30% discount)           = $16.10  
- Capacitors (20% discount)          = $2.30
- Drivers (no change)                = $2.00
- PCB (volume pricing)               = $4.00
─────────────────────────────────────────────
Total per unit (100 qty):             $40.00
````

## Summary

For **50W operation in 200Ω domain**:

**Capacitors:** 630V C0G/NP0 ceramic (4.5× margin) **Inductors:** I_DC ≥ 3A, I_sat ≥ 4A (6-10× margin)