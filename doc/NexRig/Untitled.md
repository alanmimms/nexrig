The transmitter includes eight relay-switched low-pass filters optimized for the 200Ω impedance domain:

|Band|Frequency Range|L (Series)|C (Shunt 1)|C (Shunt 2)|C (Series)|Relay|
|---|---|---|---|---|---|---|
|**160m**|1.8-2.0 MHz|1.5µH|350pF|220pF|330pF|K1601|
|**80m**|3.5-4.0 MHz|820nH|220pF|330pF|180pF|K1602|
|**60m**|5.3-5.4 MHz|620nH|150pF|240pF|130pF|K1603|
|**40m**|7.0-7.3 MHz|470nH|220pF|180pF|100pF|K1606|
|**30m**|10.1-10.15 MHz|330nH|82pF|150pF|68pF|K1607|
|**20m**|14.0-14.35 MHz|240nH|56pF|91pF|47pF|K1608|
|**17/15m**|18.068-21.45 MHz|180nH|39pF|33pF|33pF|K1604|
|**12/10m**|24.89-29.7 MHz|130nH|33pF|24pF|27pF|K1605|

### Filter Topology

Each filter implements a modified pi-network configuration optimized for the 200Ω impedance domain:

```
Input → Series L → Shunt C1 → Shunt C2 → Series C → Output
                      ↓          ↓
                     GND        GND
```

This topology provides:

- Stopband attenuation: >40 dB at second harmonic
- Passband insertion loss: <0.3 dB
- Return loss: >20 dB in-band
- Power handling: 100W continuous at 200Ω

### Component Selection at 200Ω

Operating at 200Ω rather than the traditional 50Ω provides significant component advantages:

**Inductors**: Values are 4× larger than equivalent 50Ω designs, enabling higher Q factors and easier winding. The larger inductance values (240nH to 1.5µH) are practical to implement with air-core or toroidal inductors while maintaining excellent Q.

**Capacitors**: Values are 4× smaller than 50Ω equivalents, allowing use of high-quality NP0/C0G ceramic capacitors throughout. The reduced capacitance requirements (24pF to 350pF) eliminate the need for mica or other expensive high-voltage capacitors.

### Filter Switching Implementation

**Relay Selection**: TQ2-5V DPDT reed relays provide reliable switching with minimal insertion loss. Both poles are paralleled to handle the 0.5A RMS current at 50W in the 200Ω domain.

**Switching Architecture**: Each filter connects between common input and output buses. Unselected filters remain disconnected, preventing interaction and maintaining optimal stopband performance.

**Zero-Voltage Switching Protocol**: Filter selection occurs only with Veer at 0V, ensuring no voltage or current through relay contacts during switching. This extends relay life beyond 10⁸ operations and eliminates hot-switching derating requirements.