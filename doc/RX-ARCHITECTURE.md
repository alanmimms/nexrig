Total resistance: 82k + 40k + 40k + 82k = 244kΩ
Current: 12V / 244kΩ = 49.2µA

Top tap (8V):    12V - (49.2µA × 82kΩ) = 12V - 4.03V = 7.97V ≈ 8.0V ✓✓
Second tap (6V): 12V - (49.2µA × 122kΩ) = 12V - 6.00V = 6.00V ✓✓
Third tap (4V):  12V - (49.2µA × 162kΩ) = 12V - 7.97V = 4.03V ≈ 4.0V ✓✓
Bottom: GND = 0V ✓
```

**Or using voltage divider formula:**
```
V_8V = 12V × (162kΩ / 244kΩ) = 12V × 0.6639 = 7.97V ✓
V_6V = 12V × (122kΩ / 244kΩ) = 12V × 0.5000 = 6.00V ✓
V_4V = 12V × (82kΩ / 244kΩ)  = 12V × 0.3361 = 4.03V ✓
```

**Excellent! Almost exactly 8V / 6V / 4V**

### Clamp Performance

**With BAT54S (V_f = 0.4V):**
```
Upper clamp: 7.97V + 0.4V = 8.37V ≈ 8.4V
Lower clamp: 4.03V - 0.4V = 3.63V ≈ 3.6V

Bias: 6.0V (exact)
Upper swing: 8.37V - 6.0V = +2.37V
Lower swing: 6.0V - 3.63V = -2.37V

Symmetric ±2.37V swing ✓✓

Tank voltage (Q=20): 20 × 2.37V = 47.4V peak ✓✓
Safety margin: 47.4V / 50V = 94.8%
Headroom below 50V limit: 5.2% ✓✓
```

**Perfect! You're now safely below the 50V conservative limit with good margin.**

## Power Dissipation
```
Current through divider: 49.2µA
Power per resistor:
  82kΩ: (49.2µA)² × 82kΩ = 0.20 mW
  40kΩ: (49.2µA)² × 40kΩ = 0.10 mW

All well within 0.1W (100mW) rating for 0805 resistors ✓
```

## Final BOM for Voltage Clamp

| Component | Value | Qty | Package | Notes |
|-----------|-------|-----|---------|-------|
| **R1403** | 82kΩ, 1% | 1 | 0805 | Top divider |
| **R1401** | 40kΩ, 1% | 1 | 0805 | Upper-mid divider |
| **R1404** | 40kΩ, 1% | 1 | 0805 | Lower-mid divider |
| **R1405** | 82kΩ, 1% | 1 | 0805 | Bottom divider |
| **D1403** | BAT54S | 1 | SOT-23 | Series Schottky pair |
| **L1401** | 1µH | 1 | 0805 | RFC, SRF >400MHz |
| **L1405** | 1µH | 1 | 0805 | RFC, SRF >400MHz |
| **C1405** | 10µF, X7R, 25V | 1 | 1206 | Lower rail bypass |
| **C1407** | 10µF, X7R, 25V | 1 | 1206 | Upper rail bypass |
| **C1409** | 1µF, X7R, 50V | 1 | 0805 | Input AC coupling |
| **C1406** | 1µF, X7R, 50V | 1 | 0805 | Output AC coupling |

**Total cost: ~$1.40 per receiver**

## Performance Summary (Final)

| Parameter | Value | Target | Status |
|-----------|-------|--------|--------|
| **Upper clamp voltage** | 8.37V | ~8.4V | ✓ Perfect |
| **Lower clamp voltage** | 3.63V | ~3.6V | ✓ Perfect |
| **DC bias point** | 6.00V | 6.0V | ✓ Exact |
| **AC swing** | ±2.37V | ±2.4V | ✓ Excellent |
| **Symmetry** | Perfect | Symmetric | ✓✓ |
| **Tank voltage (Q=20)** | 47.4V | <50V | ✓✓ Safe |
| **Safety margin** | 5.2% | >0% | ✓ Good headroom |
| **Clamp response** | <1 ns | <10ns | ✓✓ Excellent |
| **Peak current** | 108 mA | <200mA | ✓ Within rating |
| **Insertion loss** | <0.01 dB | <0.1dB | ✓✓ Negligible |

## Resistor Values Standard Series Check

**E24 series (5% tolerance):**
- 82kΩ ✓ (standard E24)
- 40kΩ - Not in E24, need E96

**E96 series (1% tolerance):**
- 82.5kΩ ✓ (use 82kΩ for simplicity)
- 40.2kΩ ✓ (exact E96 value)

**Recommended part numbers:**

For 1% tolerance (E96):
- 82kΩ: Standard 1% value (82.0kΩ exact)
- 40kΩ: Use 40.2kΩ (closest E96)

**With 82k / 40.2k / 40.2k / 82k:**
```
Total: 244.4kΩ
Current: 49.1µA

V_8V = 12V × (162.4k / 244.4k) = 7.98V ✓
V_6V = 12V × (122.2k / 244.4k) = 6.00V ✓
V_4V = 12V × (82k / 244.4k) = 4.02V ✓

Essentially identical to 82k/40k/40k/82k ✓
