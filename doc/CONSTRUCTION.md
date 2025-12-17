# Transmit Power MOSFET driver transformer
The power MOSFET gate is driven by a special purpose gate driver chip
UCC27511A. This device is then transformer coupled to the MOSFET gate
to maximize the power delivered to the MOSFET's highly capacitive gate
to get better switching efficiency and cleaner output waveform.

Between the gate drive transformer and the MOSFET is a 6.8 Ω series
gate resistor, which is essential for damping oscillations that can
arise from the interaction between the transformer's leakage
inductance and the MOSFET's input capacitance (Ciss).

## Winding Instructions
For this transformer to work correctly, the two windings must be wound
together to ensure they are tightly coupled. This is a bifilar winding
on a Fair-Rite 2843000202 binocular core.

*Prepare the Wire*: Take two equal lengths of Litz 5/52/38 wire. You
can lightly twist them together, about one twist per inch (or one per
2-3 cm). Mark one end of each wire (e.g., with a dab of paint) so you
can identify the "start" and "finish" of each winding.

*Wind the Core*: Take the twisted pair and pass it through one hole of
the binocular core and back through the second hole. This completes
one turn. Repeat this process two more times for a total of three
turns.

Connect the Windings:

* The two "start" ends you marked are in-phase.

* *Primary*: Connect the start of one winding to the driver output and
  the finish to the driver's return path (VDD or GND).

* *Secondary*: Connect the start of the other winding to the MOSFET
  gate (via the 6.8 Ω resistor) and the finish to the MOSFET source.

This method creates a highly efficient 1:1 transformer with low
leakage inductance, which is critical for transmitting the fast,
sharp-edged pulses needed to drive the power amplifier MOSFET
efficiently.
