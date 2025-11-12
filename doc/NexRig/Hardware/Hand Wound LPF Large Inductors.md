Excellent - hand-wound toroids are actually the **best solution** for your high-value inductors. Let me design these for you.

## Toroid Design Requirements

**Your specifications:**

- Frequency range: 1.8-10 MHz (160m filter uses these values)
- Current: 0.5A RMS, peaks to ~1.5A
- Required Isat: >2.8A (design for >3A to be safe)
- Power handling: Minimal heating at 0.5A RMS
- Q factor: Maximize (minimize DCR)
- SRF: >30 MHz for use at 10 MHz (5th harmonic)

## Core Material Selection

### Iron Powder vs Ferrite

**Iron Powder (Micrometals) - RECOMMENDED:**

- Distributed air gap (won't saturate easily)
- Excellent for power applications
- High Q at HF frequencies
- Stable with temperature
- Isat essentially unlimited (<1% inductance change at 10A)

**Ferrite (Fair-Rite) - NOT RECOMMENDED:**

- No distributed gap (saturates suddenly)
- Lower Q at HF
- Temperature sensitive
- Isat typically <2A for these inductance values

**Conclusion: Use Micrometals iron powder cores**

### Material Selection (Micrometals Mix)

|Mix|Color|Frequency Range|Application|Use for Your Design|
|---|---|---|---|---|
|-2|Red|1-30 MHz|Broadband transformers, HF inductors|**YES - Best choice**|
|-6|Yellow/White|2-30 MHz|HF power inductors|**YES - Also good**|
|-10|Black|0.5-5 MHz|Low frequency inductors|Maybe for 160m only|
|-26|Yellow/White|0.1-2 MHz|EMI suppression|No - too low frequency|

**Recommendation: Use Mix-2 (Red) for all your inductors**

- Optimal for 1.8-30 MHz
- Lowest core loss at your frequencies
- Excellent Q factor (150-250)
- Widely available
- Consistent performance across all bands

### Core Size Selection

**T50 (0.500" OD) - RECOMMENDED for all values:**

- Outside diameter: 0.500" (12.7mm)
- Inside diameter: 0.300" (7.62mm)
- Height: 0.188" (4.78mm)
- Plenty of room for all your turn counts
- Good balance of size/performance/cost
- Most common size (excellent availability)

**Alternative T68 (0.680" OD) for 27µH only:**

- More winding space if T50 is tight
- Slightly lower DCR (more copper area)
- Larger footprint

**Part numbers:**

- T50-2 (Red, Mix-2): ~$0.60-0.75 each
- T68-2 (Red, Mix-2): ~$1.00-1.25 each

## Inductance Calculation

### AL Value for T50-2

**AL = 4.9 nH/turn²** (from Micrometals datasheet)

### Turns Calculation Formula

```
N = √(L / AL)

Where:
- N = number of turns
- L = desired inductance (nH)
- AL = inductance per turn² (nH/turn²)
```

## Design for Each Value

### 10µH Inductor

**Turns required:**

```
N = √(10,000 nH / 4.9 nH/turn²)
N = √2041
N = 45.2 turns
→ Use 45 turns
```

**Actual inductance:**

```
L = AL × N² = 4.9 × 45² = 9,922 nH ≈ 9.9µH
(within tolerance)
```

**Wire size:** #22 AWG (0.644mm / 0.0253" diameter)

- Bare wire fits: ~60 turns on T50-2
- 45 turns easily fits with room to spare
- Current capacity: 0.92A (for 700 circular mils/amp)
- Adequate for 0.5A RMS continuous

**DCR estimate:**

```
Mean length per turn (T50): 1.14" (29mm)
Wire length: 45 × 29mm = 1.31m
#22 AWG resistance: 52.8 Ω/km
DCR = 1.31m × 52.8 Ω/km = 0.069Ω
```

**SRF estimate:** >50 MHz (low turn count, good spacing)

---

### 15µH Inductor

**Turns required:**

```
N = √(15,000 nH / 4.9 nH/turn²)
N = √3061
N = 55.3 turns
→ Use 55 turns
```

**Actual inductance:**

```
L = 4.9 × 55² = 14,823 nH ≈ 14.8µH
(close enough, within tolerance)
```

**Wire size:** #22 AWG

- 55 turns fits on T50-2 (approaches maximum)
- Consider #24 AWG if winding is too tight
- Current capacity still adequate

**DCR estimate:**

```
Wire length: 55 × 29mm = 1.60m
DCR = 1.60m × 52.8 Ω/km = 0.084Ω
```

**SRF estimate:** ~40 MHz

**Alternative with #24 AWG:**

- Easier to wind (smaller diameter)
- Slightly higher DCR: ~0.13Ω (still acceptable)
- Better SRF due to tighter winding

---

### 20µH Inductor

**Turns required:**

```
N = √(20,000 nH / 4.9 nH/turn²)
N = √4082
N = 63.9 turns
→ Use 64 turns
```

**Actual inductance:**

```
L = 4.9 × 64² = 20,070 nH ≈ 20.1µH
(perfect!)
```

**Wire size:** #24 AWG (0.511mm / 0.0201" diameter) **REQUIRED**

- #22 AWG: 64 turns won't fit on T50-2
- #24 AWG: 64 turns fits comfortably
- Current capacity: 0.577A (still adequate for 0.5A RMS)

**DCR estimate:**

```
Wire length: 64 × 29mm = 1.86m
#24 AWG resistance: 84.2 Ω/km
DCR = 1.86m × 84.2 Ω/km = 0.157Ω
```

**SRF estimate:** ~35 MHz

**Alternative: T68-2 core with #22 AWG:**

- More winding space
- Can use thicker wire (#22 AWG)
- Lower DCR: ~0.11Ω
- Larger footprint (17mm diameter)

---

### 27µH Inductor

**Turns required:**

```
N = √(27,000 nH / 4.9 nH/turn²)
N = √5510
N = 74.2 turns
→ Use 74 turns
```

**Actual inductance:**

```
L = 4.9 × 74² = 26,814 nH ≈ 26.8µH
(close enough)
```

**Wire size:** #24 AWG **REQUIRED**

- #22 AWG: 74 turns definitely won't fit on T50-2
- #24 AWG: 74 turns is very tight on T50-2
- Consider T68-2 core instead

**DCR estimate (T50-2 with #24 AWG):**

```
Wire length: 74 × 29mm = 2.15m
DCR = 2.15m × 84.2 Ω/km = 0.181Ω
```

**SRF estimate:** ~30 MHz (acceptable but marginal)

**BETTER OPTION: T68-2 core with #22 AWG:**

```
AL (T68-2) = 5.7 nH/turn²
N = √(27,000 / 5.7) = 68.8 turns → 69 turns
Wire length: 69 × 1.50" × 25.4mm/in = 2.64m
DCR = 2.64m × 52.8 Ω/km = 0.139Ω
SRF: ~35 MHz (better margin)
```

## Complete Design Summary

### Recommended Configuration

|Value|Core|Wire|Turns|Actual L|DCR|SRF|Fits?|
|---|---|---|---|---|---|---|---|
|10µH|T50-2|#22 AWG|45|9.9µH|0.069Ω|>50 MHz|✓ Easy|
|15µH|T50-2|#22 AWG|55|14.8µH|0.084Ω|~40 MHz|✓ Tight|
|20µH|T50-2|#24 AWG|64|20.1µH|0.157Ω|~35 MHz|✓ OK|
|27µH|**T68-2**|#22 AWG|69|26.9µH|0.139Ω|~35 MHz|✓ Good|

**Alternative (all T50-2, smaller footprint):**

|Value|Core|Wire|Turns|Actual L|DCR|SRF|Fits?|
|---|---|---|---|---|---|---|---|
|10µH|T50-2|#22 AWG|45|9.9µH|0.069Ω|>50 MHz|✓ Easy|
|15µH|T50-2|#24 AWG|55|14.8µH|0.130Ω|~40 MHz|✓ Better|
|20µH|T50-2|#24 AWG|64|20.1µH|0.157Ω|~35 MHz|✓ OK|
|27µH|T50-2|#24 AWG|74|26.8µH|0.181Ω|~30 MHz|✓ Very tight|

## Winding Technique

### General Procedure

**1. Prepare wire:**

- Cut length: (N × mean_length_per_turn) + 50mm for leads
- Example for 45 turns on T50: (45 × 29mm) + 50mm = 1.36m
- Strip 10mm insulation on each end

**2. Winding pattern - CRITICAL:**

```
Use "toroidal winding" technique:

     Start lead
         ↓
    ┌────●────┐
    │    │    │  Pass wire through center hole
    │    ↓    │  Wind around outside
    │  ──→    │  
    │    ↑    │  Pass back through center
    │    │    │
    └─────────┘
         ↑
    Finish lead

Key points:
- Wind turns EVENLY around entire circumference
- Don't bunch turns on one side
- Maintain consistent spacing
- Don't overlap turns if possible
```

**3. Even distribution:**

- Divide core circumference into equal sections
- Example for 45 turns: mark core every 8° (360°/45)
- Each turn passes through center at marked position
- Results in evenly distributed winding

**4. Winding direction:**

- Always wind in same direction (all clockwise or all counterclockwise)
- Keep wire flat against core (don't twist)
- Maintain slight tension (don't pull too tight)

**5. Lead orientation:**

- Exit leads on opposite sides of core (180° apart)
- This minimizes lead inductance
- Makes PCB mounting easier

### Tight Winding Tips (for 55-74 turn inductors)

**For maximum turns on T50:**

1. **Use smaller wire:** #24 AWG instead of #22 AWG
2. **Pre-tin wire:** Lightly tin with solder before winding
    - Makes wire stiffer
    - Easier to control
    - Slightly smaller diameter
3. **Wind in two layers if needed:**
    - First layer: wind evenly around core
    - Second layer: wind in gaps between first layer turns
    - Insulate layers with one wrap of Kapton tape
    - Note: This lowers SRF slightly
4. **Use winding jig:** Clamp core, rotate while feeding wire

### SRF Optimization

**To maximize SRF:**

1. **Space turns evenly** (not bunched)
2. **Single layer winding** (avoid layer-to-layer capacitance)
3. **Minimize lead length** (keep leads short)
4. **Lead dress:** Route leads away from winding
5. **Consider progressive winding:**

```
   Instead of continuous spiral:
   Wind every 2nd position first pass
   Fill gaps on second pass
   Reduces turn-to-turn capacitance
```

## PCB Mounting

### Horizontal Mounting (Recommended)

```
Top view:
              Lead spacing
         ├────────────────┤
    ─────●───[Toroid]───●─────  PCB trace
         │               │
       Solder          Solder
         ↓               ↓
    ─────●───────────────●─────  PCB pads
```

**Pad design:**

- Pad diameter: 2.0-2.5mm (0.080-0.100")
- Pad spacing: 15-20mm (0.6-0.8")
- Solder: Use adequate solder to secure mechanically

**Mounting:**

- Lay toroid flat on PCB
- Leads should be ~15-20mm apart
- Secure with solder only (no additional adhesive needed)

### Vertical Mounting (Space-constrained)

```
Side view:
         [Toroid]
            │
            │  Lead
            ↓
    ────────●────────  PCB
```

- Stand toroid on edge
- Both leads on same side of core
- Requires mechanical support (glue or clamp)
- Less desirable due to vertical field radiation

## Testing and Verification

### Inductance Measurement

**Equipment needed:**

- LCR meter (e.g., BK Precision 879B: $179)
- Test frequency: 1 MHz
- Test voltage: 0.1V RMS
- DC bias: 0A

**Procedure:**

1. Measure each inductor after winding
2. Compare to target value
3. If low: add 1-2 turns
4. If high: remove 1-2 turns
5. Remeasure and verify

**Tolerance achievement:**

- With careful winding: ±2-5% achievable
- Much better than commercial 10-20% parts!

### SRF Measurement

**With network analyzer or VNA:**

- Sweep 1-100 MHz
- Look for impedance maximum (series resonance)
- Verify SRF >30 MHz for all values

**With LCR meter:**

- Measure inductance vs frequency
- Watch for inductance decrease at high frequency
- SRF is where L becomes negative or minimum

### Q Factor Measurement

**At 7 MHz (40m band example):**

```
Q = XL / (DCR + Rac)

Where:
- XL = 2π × f × L (inductive reactance)
- DCR = DC resistance (measured)
- Rac = AC resistance (skin effect, typically 1.5-2× DCR at HF)

Example for 10µH at 7 MHz:
XL = 2π × 7MHz × 10µH = 440Ω
DCR = 0.069Ω
Rac = 0.069Ω × 1.5 = 0.104Ω
Q = 440 / 0.104 = 4,231

(Excellent! Commercial inductors: Q = 100-300)
```

## Parts Sourcing

### Cores

**Micrometals T50-2 (Red):**

- Digi-Key: P/N 435-T50-2-ND
- Mouser: P/N 535-T502
- Direct from Micrometals: [www.micrometals.com](http://www.micrometals.com)
- Price: $0.60-0.75 each (quantity 10-50)

**Micrometals T68-2 (Red):**

- Similar sources
- Price: $1.00-1.25 each

### Wire

**Magnet wire (enameled copper):**

**#22 AWG:**

- Digi-Key: Multiple options (search "magnet wire 22 awg")
- Remington Industries: 22SNSP (1 lb spool ~$15-20)
- Sufficient for ~50 inductors (20m on spool)

**#24 AWG:**

- Same sources
- Remington Industries: 24SNSP (1 lb spool ~$15-20)
- Sufficient for ~80 inductors (30m on spool)

**Wire specifications:**

- Type: Single build polyurethane-coated
- Temperature rating: 200°C minimum
- Insulation: Self-bonding or heavy build optional (easier handling)

### Cost Summary

**For complete set (10, 15, 20, 27µH × 8 filters × 3 series L per position):**

- Assume 24 total toroids needed (conservative)
- Cores: 24 × $0.75 = **$18**
- Wire: 1 spool each size = **$35**
- Total materials: **$53 for all prototypes**

Per transceiver after initial wire purchase:

- 24 cores × $0.75 = **$18 per transceiver**

**Compare to commercial inductors:**

- Coilcraft DR0810: ~$50-60
- Bourns 5900: ~$70-90

**Savings: $30-70 per transceiver** plus superior performance!

## Advantages of Hand-Wound Toroids

✓ **Exact target values** (wind to measured inductance) ✓ **Excellent Q** (200-300 vs 50-150 commercial) ✓ **High SRF** (>30 MHz achievable) ✓ **Unlimited Isat** (iron powder won't saturate at <10A) ✓ **Self-shielding** (toroidal field contained within core) ✓ **Low cost** ($0.75 per inductor vs $2-4 commercial) ✓ **No coupling issues** (field self-contained) ✓ **Tolerance ±2-5%** (vs ±10-20% commercial)