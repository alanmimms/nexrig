Receiver Signal Chain Summary
 * Antenna Input: Standard connector (e.g., BNC or SMA).
 * DC Block: Initial capacitor to block any DC from the antenna.
 * Digital Attenuator (DAPs):
   * Topology: Cascade of four Pi or T-pad attenuators with values 3dB, 6dB, 12dB, and 24dB.
   * Switching: Each pad is switched in/out using a Panasonic TQ2-5V DPDT relay, wired for true bypass (signal completely routed around the pad when OFF).
   * Control: Relays driven by 2N7002K MOSFETs controlled by STM32 GPIO pins (positive logic HIGH turns relay ON, inserting attenuation). Requires 4 GPIO pins.
   * Range: Provides 0dB to 45dB attenuation in 3dB steps.
 * Protection Clipper #1 (Pre-Transformer):
   * Topology: Single-supply biased clipper using fast diodes (e.g., BAT54S or similar low-capacitance Schottky pair).
   * Biasing: Resistor divider from +12V creates +8V, +6V, and +4V rails. Signal line is biased to +6V directly via the center tap resistors (e.g., 2x 40kΩ). Diode cathodes/anodes are biased to +8V and +4V via RF chokes (e.g., 1µH).
   * Clipping Level: Clamps the signal symmetrically around the +6V bias at approx. +3.7V and +8.3V, resulting in a ~4.6V pk-pk maximum output.
 * DC Block: Capacitor (e.g., 1µF) to block the +6V bias from the clipper.
 * Input Transformer (T1):
   * Type: 50Ω to 200Ω step-up transformer.
   * Core: FT37-63.
   * Windings: 5 turns primary, 10 turns secondary (#26 AWG). Provides a 1:2 voltage step-up (+6dB).
 * Preselector:
   * Topology: Switched LC tank circuit operating at 200Ω impedance.
   * Components: Digitally switched inductors and capacitors (details in rx-preselector-matching.md).
   * Target Q: Designed for Q <= 22. Provides significant voltage gain (up to Q times, or ~27dB max) at resonance.
 * Output Transformer (T2):
   * Type: 200Ω to 3×50Ω step-down transformer.
   * Core: FT50-43 (or FT50-63 for lower core losses at lower frequencies).
   * Windings: 12 turns primary (#26 AWG), three separate 6-turn secondaries (#26 AWG), trifilar wound for matched outputs.
   * Impedance: 200Ω primary to 50Ω per secondary (nominal), 4:1 impedance ratio, 2:1 voltage step-down.
   * Output impedance: 2-4Ω actual at HF (dominated by leakage inductance ~10-20nH and winding resistance ~0.13Ω referred to secondary).
   * Design notes: Low output impedance critical for QSD sampling capacitor charging. At 30MHz worst case with 6× sampling (1.4ns charge time), source impedance of 2-4Ω allows ~20-25% capacitor settling, which is normal and acceptable for coherent QSD operation. Trifilar winding ensures identical impedance to all three QSDs preserving I/Q balance.
 * Interface Circuit (Repeated x3, one for each T2 secondary):
   * AC Coupling: Series capacitor 1µF, 50V immediately after T2 secondary, blocks transformer DC offset.
   * Bias Injection: +1.65V DC bias (from +2.5V reference via resistive divider) injected via 2.2µH RFC.
     * RFC: 2.2µH, SRF 68MHz, DCR 0.138Ω provides 25-415Ω isolation across 1.8-30MHz HF range.
     * Bypass: 1µF capacitor at +1.65V bias rail to ground, provides low RF impedance (5-88Ω) preventing RF coupling into bias supply.
   * Direct connection to QSD input after bias injection, no series resistor or additional clipping needed.
   * Voltage levels: Transformer secondary ±0.7V AC + 1.65V bias = 0.95V to 2.35V absolute range, well within 0-3.3V QSD operating limits.
   * Design rationale: Preselector voltage clamp limits tank to ±2.8V, transformer 4:1 step-down gives ±0.7V, natural voltage range stays within safe limits without additional protection components.
 * Quadrature Sampling Detectors (QSDs):
   * Type: Texas Instruments TS3A4751 low-voltage analog switch (SP4T).
   * Quantity: 3 used (for f, f+k, f-k channels).
   * Clocking: Quadrature (4x) clock for f+k/f-k, 1/3-rature (6x) clock for f.
   * Input Range: Strictly 0V to +3.3V.
 * Sample Capacitors: 1000pF on each of the four outputs (I+, I-, Q+, Q-) per QSD.
 * AC Coupling: Series capacitors (e.g., 0.1µF - 1µF) on all I/Q lines (I+, I-, Q+, Q-) from the sample caps.
 * Programmable Gain Amplifier (PGA) Stage:
   * Type: Analog Devices MAX9939.
   * Quantity: 6 total (one for each I signal, one for each Q signal, across the 3 QSDs).
   * Configuration: Differential input (connected directly after AC coupling caps), configured for differential output per datasheet Figure 4. Internal biasing sets input CM to +2.5V. Internal 10kΩ resistors provide input current limiting.
   * Control: Gain controlled via SPI from STM32 (-14dB to +44dB range).
   * Power: Single +5V supply. Output implicitly common-moded to +2.5V.
 * Anti-Aliasing Filter:
   * Topology: Differential RC low-pass filter on each PGA output pair (OUTA/OUTB).
   * Components: Recalculated values (e.g., ~1kΩ series R + ~4.7nF shunt C per line) for a cutoff frequency of ~30-50 kHz.
   * Placement: Placed between the MAX9939 outputs and the ADC inputs.
 * Protection Diodes (ADC Input):
   * Topology: Symmetric clamping using Schottky diode pairs (e.g., BAV99, BAT54S, BAS40-04 or similar in SOT-23 packages).
   * Placement: Directly at the ADC input pins (IN+, IN-).
   * Connections: Clamp each input line to GND and +5V (AVDD). Requires 4 diodes per differential pair.
 * Analog-to-Digital Converter (ADC):
   * Type: AKM AK5578 (or similar 8-channel audio ADC).
   * Channels Used: 6 differential channels (I/Q for f, f+k, f-k).
   * Input Range: ~2.5V pk-pk differential, common-moded to +2.5V.
   * Power: +5V AVDD.
   * Sampling Rate: 96 kHz planned.
Control & AGC Summary
 * Coarse Gain: STM32 controls the DAP relays (0-45dB in 3dB steps). Reacts slowly (~100ms) based on detected clipping or high signal levels at the ADC.
 * Fine Gain: STM32 controls the MAX9939 PGA gain (-14dB to +44dB) via SPI. Reacts quickly (<100µs) based on signal level at the ADC to keep it within the optimal range. Separate gain applied to f channel vs. f±k channels to compensate for QSD clocking differences.
 * Protection: Fast diode clippers (pre-T1 and pre-QSD) provide instantaneous protection while the AGC adjusts. Internal ADC clipping is monitored as an overload indicator.
