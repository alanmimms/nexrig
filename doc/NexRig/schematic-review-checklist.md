# NexRig Schematic Review Checklist

## Purpose
This document provides a comprehensive checklist for reviewing NexRig schematics to ensure design correctness, completeness, and manufacturability. Use this for both progressive reviews during schematic entry and final validation before PCB layout.

## Review Process Overview

**Recommended Approach:**
1. **First Pass**: Connectivity and basic electrical rules (automated + manual)
2. **Second Pass**: Component specifications and ratings
3. **Third Pass**: Subsystem-specific verification against architecture docs
4. **Fourth Pass**: Debug provisions and manufacturing considerations
5. **Final Pass**: Cross-sheet consistency and documentation completeness

**Severity Levels:**
- 🔴 **CRITICAL**: Design will not function or may be damaged
- 🟡 **WARNING**: May cause intermittent issues or suboptimal performance
- 🟢 **OPTIMIZATION**: Works but could be improved

---

## 1. Connectivity and Pin Assignment

### Basic Electrical Rules
- [ ] 🔴 All nets connected to at least two pins (no single-pin nets)
- [ ] 🔴 No unconnected input pins (except intentionally floating per datasheet)
- [ ] 🔴 Power pins connected to appropriate rails
- [ ] 🔴 Ground pins connected to ground
- [ ] 🔴 No shorts between different nets
- [ ] 🟡 Output pins not driving each other (check for bus conflicts)
- [ ] 🟡 Bidirectional pins configured correctly in firmware plan

### Pin Orientation and Signal Flow
- [ ] 🟢 Inputs on left, outputs on right (schematic readability)
- [ ] 🟢 Power flows top to bottom
- [ ] 🔴 Differential pairs (USB D+/D-, I2S clocks) routed as pairs
- [ ] 🟡 Critical signal paths clear and direct (minimal vias, short traces)

### Component Function Verification
- [ ] 🔴 Each IC appropriate for its intended function
- [ ] 🔴 Pin assignments match datasheet (especially BGA packages)
- [ ] 🔴 Pin multiplexing compatible (STM32 alternate functions)
- [ ] 🟡 DMA-capable peripherals on DMA-capable pins (if using DMA)

---

## 2. Power Supply Architecture

### Voltage Rails
- [ ] 🔴 All required voltage rails present (3.3V, 5V, 12V, etc.)
- [ ] 🔴 Rail voltages within IC absolute maximum ratings
- [ ] 🟡 Rail voltages optimal for IC performance (not just within range)
- [ ] 🔴 Regulator output voltage set correctly (feedback resistor dividers)
- [ ] 🔴 Load current within regulator capability (calculate total load per rail)
- [ ] 🟡 Margin for inrush current and transients

### Power Sequencing
- [ ] 🔴 Power-on sequence documented and implemented (where required)
- [ ] 🔴 Core voltage before I/O voltage (for FPGAs, some microcontrollers)
- [ ] 🔴 Load switches for controlled sequencing where needed
- [ ] 🟡 Enable pin timing relationships correct
- [ ] 🟡 Ramp rates within specifications (soft-start capacitors)
- [ ] 🔴 Brownout/UVLO thresholds set appropriately

### Current Budgeting
- [ ] 🔴 Total load per rail calculated and documented
- [ ] 🔴 Regulator continuous current rating exceeds load + margin
- [ ] 🟡 Peak/transient current capability adequate
- [ ] 🔴 Input supply current capability verified
- [ ] 🟡 Thermal dissipation acceptable for regulator packages

---

## 3. Decoupling and Bypassing

### Bulk Capacitance
- [ ] 🔴 Bulk capacitors on each power rail (10µF-100µF typical)
- [ ] 🟡 Capacitor voltage rating ≥2× rail voltage (preferably 3×)
- [ ] 🟡 Low-ESR type where needed (polymer, ceramic)
- [ ] 🔴 Electrolytic polarity correct

### Local Decoupling
- [ ] 🔴 Decoupling capacitors at each IC power pin
- [ ] 🟡 0.1µF ceramic typical, closer values for high-speed ICs
- [ ] 🔴 High-frequency ceramics (0.01µF, 1nF) where specified by datasheet
- [ ] 🟢 Placement intent clear (notes indicate "close to IC pins")
- [ ] 🟡 ESR requirements met for specific regulators (LDOs, buck controllers)

### Analog Power Supply Rejection
- [ ] 🔴 Separate analog and digital supply filtering where required
- [ ] 🟡 LC or RC filters on sensitive analog rails
- [ ] 🔴 ADC/DAC reference voltage decoupling per datasheet
- [ ] 🟡 Op-amp power supply bypassing adequate

---

## 4. Clock and Timing

### Clock Sources
- [ ] 🔴 Crystal/oscillator frequency matches design requirements
- [ ] 🔴 Crystal loading capacitors correct value per datasheet
- [ ] 🔴 Crystal ESR within microcontroller/FPGA specification
- [ ] 🟡 Clock accuracy adequate for application (USB needs <0.25%, etc.)
- [ ] 🟡 Temperature stability specified (TCXO for critical applications)
- [ ] 🔴 Clock enable/disable control correct

### Clock Distribution
- [ ] 🔴 Fanout limits not exceeded (clock buffer if needed)
- [ ] 🟡 Termination resistors where required (high-speed clocks)
- [ ] 🟡 Clock trace lengths appropriate (consider propagation delay)
- [ ] 🔴 No unintended stubs on clock lines

### PLL Configuration
- [ ] 🔴 PLL input frequency within specified range
- [ ] 🔴 PLL feedback divider values correct
- [ ] 🔴 PLL output frequency achievable and within range
- [ ] 🟡 PLL lock time considered in power-up sequence
- [ ] 🟡 PLL power supply filtering adequate (separate rail or LC filter)

### Reset Timing
- [ ] 🔴 Reset asserted during power-up (reset IC or RC network)
- [ ] 🔴 Reset pulse width adequate (check datasheet minimum)
- [ ] 🟡 Reset released after clocks stable
- [ ] 🟡 Reset button or external reset provision
- [ ] 🔴 Reset pin not floating (pull-up or pull-down as required)

---

## 5. Control Signal Logic Levels

### Voltage Compatibility
- [ ] 🔴 GPIO output levels compatible with input thresholds
- [ ] 🔴 Level shifters present where needed (3.3V ↔ 5V, etc.)
- [ ] 🟡 5V-tolerant pins used for 5V inputs (or protection added)
- [ ] 🔴 Open-drain outputs have pull-up resistors to correct rail

### Drive Capability
- [ ] 🔴 GPIO output current within limits (check fan-out)
- [ ] 🟡 High-current outputs use drivers/buffers (relay coils, LED arrays)
- [ ] 🔴 MOSFET gate drive adequate (voltage and current)
- [ ] 🟡 Capacitive loads within driver capability

### Signal Polarity and Default States
- [ ] 🟡 Active-high vs active-low consistent and documented
- [ ] 🔴 Default states safe (what happens before firmware initializes?)
- [ ] 🔴 Pull-ups/pull-downs set safe defaults
- [ ] 🟡 Enable signals default to disabled state for safety
- [ ] 🔴 Interlock signals prevent unsafe conditions (PA enable, T/R switching)

---

## 6. Pull-Up and Pull-Down Resistors

### I2C Bus
- [ ] 🔴 Pull-up resistors present on SDA and SCL
- [ ] 🔴 Pull-up resistor values appropriate (1.5kΩ-10kΩ typical, depends on bus speed and capacitance)
- [ ] 🔴 Pull-ups connected to correct voltage rail (usually 3.3V or 5V)
- [ ] 🟡 Only one set of pull-ups per bus (not duplicated)

### SPI Bus
- [ ] 🔴 MISO pull-up if multiple slaves (or tri-state capable slaves only)
- [ ] 🟡 CS/SS lines default to inactive (pull-up usually)
- [ ] 🟡 Unused SPI pins tied appropriately (master or slave mode)

### Other Buses and Signals
- [ ] 🔴 USB D+ pull-up for device mode (1.5kΩ to 3.3V)
- [ ] 🔴 UART RX pull-up to prevent floating (if no external driver)
- [ ] 🔴 Unused inputs tied high or low (not floating, unless datasheet allows)
- [ ] 🟡 Reset pins pulled to inactive state
- [ ] 🟡 Enable pins default state via pull-up/pull-down

### Timing Considerations
- [ ] 🟡 Pull-up/pull-down strength vs signal speed (fast signals need stronger pull)
- [ ] 🟡 Pull-ups connected to rail that powers up before the bus is used

---

## 7. Analog Signal Integrity

### ADC Input Conditioning
- [ ] 🔴 Anti-aliasing filter present (cutoff frequency appropriate)
- [ ] 🔴 Input impedance within ADC specification
- [ ] 🟡 Filter order adequate (typically 2nd or 3rd order minimum)
- [ ] 🔴 ADC reference voltage stable and decoupled
- [ ] 🟡 Input voltage range within ADC limits (0-VREF or ±VREF/2)
- [ ] 🟡 Offset and gain adjust provisions if needed

### DAC Output Conditioning
- [ ] 🔴 Reconstruction filter present (cutoff frequency appropriate)
- [ ] 🟡 Output buffer amplifier if needed (current drive capability)
- [ ] 🔴 DAC reference voltage stable and decoupled
- [ ] 🟡 DC blocking capacitor if AC-coupled output

### Ground Strategy
- [ ] 🔴 Analog ground and digital ground strategy defined
- [ ] 🟡 Single-point ground connection (star ground) for sensitive analog
- [ ] 🟡 Guard traces or ground pour around sensitive analog signals
- [ ] 🟡 No digital signals routed under/near sensitive analog paths

### Differential Signals
- [ ] 🔴 Differential pairs matched length (especially for high-speed)
- [ ] 🟡 Differential pairs routed together, same layer
- [ ] 🟡 Common-mode filtering if needed (ferrite beads, common-mode chokes)

---

## 8. RF-Specific Checks

### Impedance Matching
- [ ] 🔴 50Ω impedance maintained throughout RF path
- [ ] 🔴 Matching networks calculated and correct
- [ ] 🟡 Component tolerances considered (tight tolerance caps for matching)
- [ ] 🔴 Trace impedance controlled (note on schematic for PCB design)

### DC Blocking and Bias
- [ ] 🔴 DC blocking capacitors where required (coupling between stages)
- [ ] 🔴 Bias tees for PIN diodes correct (RFC and DC feed)
- [ ] 🔴 RF switches bias voltages correct (forward bias, reverse bias)
- [ ] 🟡 Voltage ratings adequate for RF peak voltages

### Component Ratings
- [ ] 🔴 Capacitor voltage ratings vs RF voltage swings (preselector tank)
- [ ] 🔴 Inductor saturation current vs circulating RF current
- [ ] 🔴 Switch power handling vs RF power levels
- [ ] 🟡 Component Q factor adequate for application (filter insertion loss)

### Filtering
- [ ] 🔴 Harmonic filter component values match design calculations
- [ ] 🔴 LPF array component values vs architecture document
- [ ] 🟡 Filter capacitor types specified (C0G/NP0 for stability)
- [ ] 🟡 Inductor cores specified (material type for frequency range)

### Ground and Shielding
- [ ] 🔴 RF ground vias spacing adequate (<λ/10 at highest frequency)
- [ ] 🟡 Ground plane under RF sections continuous
- [ ] 🟡 Shielded inductors where specified (prevents coupling)

---

## 9. Protection and Fault Handling

### ESD Protection
- [ ] 🔴 TVS diodes or ESD protection on external interfaces (USB, antenna, audio)
- [ ] 🟡 Protection on user-accessible signals
- [ ] 🟡 Proximity of protection devices to connectors (note for PCB layout)

### Overvoltage and Reverse Polarity
- [ ] 🔴 Reverse polarity protection on power input (diode or P-MOSFET)
- [ ] 🔴 Overvoltage protection (TVS, Zener, voltage clamp)
- [ ] 🟡 Crowbar circuit for critical rails (if applicable)
- [ ] 🔴 Voltage clamp for high-Q preselector (Schottky diode clamp per design)

### Overcurrent Protection
- [ ] 🟡 Inrush current limiting (NTC thermistor or active circuit)
- [ ] 🟡 Fuse or PTC on power input
- [ ] 🟡 Current limit provisions on high-power rails
- [ ] 🔴 Short-circuit protection for PA and EER supply

### Thermal Protection
- [ ] 🟡 Thermal shutdown for power components (if available)
- [ ] 🟡 Temperature sensors on critical components (PA, EER converter)
- [ ] 🟡 Overtemperature monitoring capability

---

## 10. Component Selection and Ratings

### Voltage Ratings
- [ ] 🔴 All components rated ≥2× operating voltage (3× preferred)
- [ ] 🔴 Transient voltage capability considered
- [ ] 🔴 DC bias effects on capacitor voltage rating (ceramic derating)

### Current Ratings
- [ ] 🔴 Continuous current within component ratings
- [ ] 🟡 Peak/transient current capability verified
- [ ] 🔴 Trace width adequate for current (note for PCB layout)

### Power Dissipation
- [ ] 🔴 Power dissipation calculated for each component
- [ ] 🔴 Package thermal resistance adequate (heatsink needed?)
- [ ] 🟡 Worst-case thermal analysis (maximum ambient temperature)

### Frequency and Bandwidth
- [ ] 🔴 Op-amp gain-bandwidth product adequate
- [ ] 🔴 MOSFET switching speed adequate (gate charge, rise/fall times)
- [ ] 🟡 Capacitor ESR and ESL acceptable at operating frequency
- [ ] 🔴 Inductor self-resonant frequency above operating frequency

### Temperature Range
- [ ] 🟡 **Component temperature grade: Commercial (0°C to +70°C) or Industrial (-40°C to +85°C)**
- [ ] 🟡 All components same temperature grade (or specify mixed)
- [ ] 🔴 Critical components automotive-grade if needed (high reliability)

### Availability and Lifecycle
- [ ] 🟡 Obsolete or NRND (not recommended for new designs) parts flagged
- [ ] 🟡 Single-source components identified (risk assessment)
- [ ] 🟢 Alternate/substitute parts documented

---

## 11. Subsystem-Specific Reviews

### STM32 Microcontroller
- [ ] 🔴 Boot mode pins configured (BOOT0 state at power-up)
- [ ] 🔴 SWD/JTAG programming interface present and accessible
- [ ] 🔴 HSE crystal circuit correct (loading caps, trace routing)
- [ ] 🟡 LSE crystal for RTC (if used)
- [ ] 🔴 USB D+/D- routing differential and length-matched
- [ ] 🔴 VDDA separated from VDD with filtering
- [ ] 🔴 VREF+ configured and decoupled (if using ADC)
- [ ] 🟡 All VDD and VSS pins connected
- [ ] 🟡 VCAP pins have required capacitors (if applicable to STM32 variant)
- [ ] 🔴 NRST pull-up and reset circuit

### FPGA (Lattice iCE40UP3K)
- [ ] 🔴 Configuration interface correct (SPI flash connections)
- [ ] 🔴 JTAG programming interface present
- [ ] 🔴 Bank voltage supplies correct for I/O standards used
- [ ] 🟡 Unused I/O pins tied per datasheet recommendation
- [ ] 🔴 PLL power supply filtered (LC filter or separate rail)
- [ ] 🔴 Configuration mode pins (CRESET_B, CDONE) connected correctly
- [ ] 🟡 Configuration flash (if used) correct pinout and voltage

### Attenuator (4-Stage T-Pad)
- [ ] 🔴 MOSFET part numbers match design (SiR178DP or equivalent)
- [ ] 🔴 Gate drive voltage adequate for logic-level MOSFETs
- [ ] 🔴 Complementary control signals implemented (inverter IC present)
- [ ] 🔴 Resistor values match design document (3dB, 6dB, 12dB, 24dB stages)
- [ ] 🟡 Pull-up resistors provide safe default state
- [ ] 🟡 Bypass MOSFET R_DS(on) acceptable for insertion loss

### Preselector (LC Tank)
- [ ] 🔴 AS183-92LF switch part number confirmed
- [ ] 🔴 Switch control voltages correct (0V/5V logic levels)
- [ ] 🔴 RFC values appropriate for frequency range (1µH typical)
- [ ] 🔴 Capacitor bank values binary-weighted (4pF, 8pF, 16pF... 512pF)
- [ ] 🔴 Inductor values match design (500nH, 180nH, 68nH)
- [ ] 🔴 Fixed capacitors for 160m/80m present (12000pF, 2000pF)
- [ ] 🟡 Parasitic capacitance noted (to be calibrated out)
- [ ] 🔴 Schottky clamp circuit present (BAT54 diodes, voltage divider per design)

### QSD Mixer Array (3× Quadrature Sampling Detectors)
- [ ] 🔴 Clock inputs from FPGA assigned correctly
- [ ] 🔴 I/Q output pairs routed to correct ADC channels
- [ ] 🔴 RC anti-aliasing filters present on QSD outputs
- [ ] 🟡 QSD switch part numbers specified
- [ ] 🟡 Local decoupling on QSD supply pins

### ADC (AKM AK5578)
- [ ] 🔴 Part number confirmed (AK5578 for 8-channel, 192kS/s)
- [ ] 🔴 I2S interface to STM32 (BCLK, LRCK, SDATA connections)
- [ ] 🔴 Master clock input (MCLK) from FPGA or oscillator
- [ ] 🔴 Control interface (I2C or SPI) connected
- [ ] 🔴 Analog supply (AVDD) and digital supply (DVDD) correct voltages
- [ ] 🟡 Reference voltage configuration
- [ ] 🟡 Six channels connected to QSD outputs (verify channel mapping)

### EER Tracking Power Supply
- [ ] 🔴 **Controller IC part number confirmed (LM34936 or LM5155 - resolve conflict)**
- [ ] 🔴 Switching frequency set correctly (RT resistor value)
- [ ] 🔴 Feedback resistor divider correct for 0-25V output
- [ ] 🔴 Power MOSFETs match design (CSD18543Q3A or equivalent)
- [ ] 🔴 Inductor value and current rating (6.8µH, I_SAT >11A, I_RMS >9A)
- [ ] 🔴 Current sense resistor (8mΩ, 1W, 1% tolerance)
- [ ] 🔴 Input and output capacitors correct (voltage, capacitance, ESR)
- [ ] 🔴 Soft-start capacitor value correct (39nF for ~5ms rise time)
- [ ] 🟡 Hiccup mode resistor (93.1kΩ) present
- [ ] 🟡 Slope compensation capacitor (27pF C0G) present
- [ ] 🔴 DAC input from STM32 for amplitude control
- [ ] 🔴 Voltage monitoring to STM32 ADC (buffered divider)

### PA (Power Amplifier)
- [ ] 🔴 PA MOSFET part number confirmed (STW25N55M5)
- [ ] 🔴 Gate drive transformer present (turns ratio 3:1 or 2:1 per design)
- [ ] 🔴 Gate drive IC adequate (UCC27511 or equivalent)
- [ ] 🔴 Drain tank circuit components present (switched L/C)
- [ ] 🔴 Tank inductor switching relays specified
- [ ] 🔴 Tank capacitor PIN diode switching present
- [ ] 🔴 PIN diode bias circuits correct (pull-up/pull-down drivers)
- [ ] 🟡 Heatsink provision noted on schematic
- [ ] 🟡 Temperature sensor on heatsink (if used)

### LPF (Low-Pass Filter) Array
- [ ] 🔴 Filter component values match design document (per band)
- [ ] 🔴 Autotransformer inductors with tap points (2:1 turns ratio)
- [ ] 🔴 Capacitor types specified (C0G/NP0, 500V rating)
- [ ] 🔴 Six filter sections present (160m, 80m+60m, 40m+30m, 20m+17m, 15m, 12m+10m)
- [ ] 🔴 DPDT relays for each filter (part number specified)
- [ ] 🔴 Relay control signals from STM32
- [ ] 🟡 Relay grounding of unused filters implemented
- [ ] 🟡 Inductor cores specified (T50-2 vs T50-6 per frequency)

### DPD (Digital Pre-Distortion) Feedback Path
- [ ] 🔴 Output coupler (resistive divider 570kΩ / 51Ω per design)
- [ ] 🔴 Buffer amplifier (GALI-74+ MMIC) present
- [ ] 🔴 Injection point into receiver (Tayloe detector input)
- [ ] 🟡 Isolation from RX LNA during calibration (switch or relay)

---

## 12. Debug and Test Provisions

### Test Points
- [ ] 🟡 Labeled test points on all power rails
- [ ] 🟡 Test points on critical signals (clocks, ADC inputs, DAC outputs)
- [ ] 🟡 RF signal monitoring points (attenuator output, preselector output, PA output)
- [ ] 🟢 Ground test points near signal test points

### Current Measurement
- [ ] 🟡 Provision for current measurement on each rail (zero-ohm resistor or jumper)
- [ ] 🟡 High-current paths accessible (PA supply, EER converter output)
- [ ] 🟢 Voltage drop measurement points for sense resistors

### Signal Injection and Monitoring
- [ ] 🟡 Ability to inject test signals (RF input, baseband signals)
- [ ] 🟡 Ability to monitor intermediate stages (preselector output, QSD inputs)
- [ ] 🟢 Access to FPGA clock outputs for verification

### Isolation and Bypass
- [ ] 🟡 Ability to isolate subsystems (zero-ohm jumpers between stages)
- [ ] 🟡 Ability to bypass components for debug (parallel zero-ohm resistor footprints)
- [ ] 🟡 Power supply isolation (separate power inputs per subsystem if needed)

### Programming and Debug Interfaces
- [ ] 🔴 STM32 SWD header accessible (SWDIO, SWCLK, GND, VDD, NRST)
- [ ] 🔴 FPGA JTAG header accessible (TDI, TDO, TCK, TMS, GND, VDD)
- [ ] 🟡 Serial console UART accessible (TX, RX, GND)
- [ ] 🟡 Bootloader entry mechanism (button, jumper, or software)

### Status Indicators
- [ ] 🟡 Power LED per rail (or key rails)
- [ ] 🟡 Status LEDs for operational modes (RX/TX, band select, fault)
- [ ] 🟢 LED current-limiting resistors correct

---

## 13. Mechanical and Thermal

### Heatsinking
- [ ] 🔴 Heatsink required components identified (PA MOSFET, EER MOSFETs)
- [ ] 🟡 Heatsink mounting holes on PCB
- [ ] 🟡 Thermal interface material specified
- [ ] 🟡 Thermal resistance calculated (junction-to-ambient)

### Component Placement
- [ ] 🟢 High-power components spaced for cooling
- [ ] 🟡 Tall components noted (won't interfere with enclosure)
- [ ] 🟡 Connector orientations suitable for cable routing
- [ ] 🟡 Access for hand-wound components (toroids, inductors)

### Stress and Strain
- [ ] 🟡 Heavy components not near PCB edges (mechanical stress)
- [ ] 🟡 Mounting holes not near sensitive circuits
- [ ] 🟡 Connectors strain-relieved or mechanically robust

---

## 14. Manufacturing and Assembly

### PCB Fabrication Notes
- [ ] 🟡 Layer count specified
- [ ] 🟡 Impedance-controlled traces noted (50Ω RF traces)
- [ ] 🟡 Copper weight specified (2oz for high-current)
- [ ] 🟢 Special requirements noted (ENIG finish, impedance test coupon)

### Assembly Notes
- [ ] 🟡 Hand-selected components marked (capacitors for LPF, ±2% tolerance)
- [ ] 🟡 Hand-wound components identified (inductors with core type, turns, wire gauge)
- [ ] 🟡 Orientation-critical components marked (electrolytic caps, diodes, ICs)
- [ ] 🟡 Temperature-sensitive components noted (placement away from hot areas)

### Silkscreen and Documentation
- [ ] 🟢 Component reference designators visible
- [ ] 🟢 Polarity marks for polarized components
- [ ] 🟢 Pin 1 indicators for ICs
- [ ] 🟢 Test point labels
- [ ] 🟡 Voltage rail labels near connectors
- [ ] 🟡 Version number or revision code

### Rework and Repair
- [ ] 🟡 Rework access (can you remove/replace BGAs, QFNs?)
- [ ] 🟡 Critical components not buried under others
- [ ] 🟢 Spare pads for alternative footprints (if applicable)

---

## 15. Documentation Cross-Reference

### Component Values vs Architecture Docs
- [ ] 🔴 Attenuator resistor values match "Rx input Attenuator.md"
- [ ] 🔴 Preselector L/C values match "RX-ARCHITECTURE.md"
- [ ] 🔴 LPF component values match "Transmitter Low-Pass Filter Array.txt"
- [ ] 🔴 EER supply values match "Tx EER.md"
- [ ] 🔴 FPGA clock frequencies match "FPGA.md"
- [ ] 🟡 PA tank component values match "EER phase modulation.md"

### Part Numbers Specified
- [ ] 🟡 All ICs have specific part numbers (not generic symbols)
- [ ] 🟡 Critical passive components have part numbers or tight specs
- [ ] 🟡 Voltage ratings specified on schematic
- [ ] 🟡 Tolerances specified where critical (±1%, ±2%)
- [ ] 🟡 Component types specified (C0G, X7R, metal film, etc.)

### Interface Protocol Compliance
- [ ] 🔴 Pin assignments match interface protocol document (when available)
- [ ] 🔴 Control signal names consistent with firmware/software design
- [ ] 🟡 Signal naming consistent across hierarchical sheets

---

## 16. Cross-Sheet Consistency

### Hierarchical Design
- [ ] 🔴 Net names consistent across sheets
- [ ] 🔴 Power rail names consistent (VCC vs VDD vs 3V3, etc.)
- [ ] 🟡 No duplicate net names causing unintended shorts
- [ ] 🔴 Hierarchical pins match between parent and child sheets
- [ ] 🟡 Global labels used correctly (not overused)

### Bus Notation
- [ ] 🟡 Bus notation correct and consistent (if used)
- [ ] 🟡 Bus members expanded correctly on destination sheets

### Reference Designators
- [ ] 🔴 No duplicate reference designators
- [ ] 🟢 Reference designators sequential and logical
- [ ] 🟢 Reference designator prefixes standard (R, C, U, L, etc.)

---

## 17. Regulatory and Safety

### EMI/EMC
- [ ] 🟡 Input power filtering (common-mode chokes, ferrite beads)
- [ ] 🟡 Shielding provisions where needed
- [ ] 🟡 Critical signal filtering (ferrite beads on USB, etc.)

### Safety Ground
- [ ] 🟡 Chassis ground vs signal ground strategy
- [ ] 🟡 Safety ground connection to enclosure
- [ ] 🟡 Isolation barriers (if required for mains-powered designs)

### High Voltage Clearance
- [ ] 🟡 Adequate creepage and clearance for high-voltage sections
- [ ] 🟡 Note on schematic for PCB designer (maintain spacing)

---

## 18. Final Review Checklist

### Before Sending to PCB Layout
- [ ] 🔴 All schematic pages reviewed
- [ ] 🔴 All subsystems verified against architecture documents
- [ ] 🔴 All critical component values confirmed
- [ ] 🟡 DRC (Design Rule Check) run and errors resolved
- [ ] 🟡 ERC (Electrical Rule Check) run and errors resolved
- [ ] 🟡 Bill of Materials exported and reviewed
- [ ] 🟡 Obsolete/unavailable parts identified and replaced
- [ ] 🟡 Layout notes added to schematic (critical spacing, routing)

### Documentation Completeness
- [ ] 🟡 Schematic has title block with project name, revision, date
- [ ] 🟡 Each sheet has descriptive title
- [ ] 🟡 Notes added for critical design decisions
- [ ] 🟡 Cross-references to architecture documents noted
- [ ] 🔴 Contact information for designer

---

## Appendix: Automated vs Manual Checks

### Can Be Automated (KiCad ERC/DRC)
- Unconnected pins
- Power pin connections
- Duplicate reference designators
- Floating nets
- Pin type conflicts (output driving output)

### Requires Expert Review
- Component selection appropriateness
- Current/voltage/power ratings
- Subsystem-specific design rules
- Compliance with architecture documents
- Debug provisions adequacy
- Manufacturing and assembly considerations

### Recommended Tools
- KiCad ERC (Electrical Rule Check)
- KiCad DRC (Design Rule Check)
- Custom Python scripts for component parameter extraction
- Spreadsheet for power budget analysis
- Spreadsheet for BOM cost and availability analysis

---

## Document Revision History
**Version 1.0** - Initial comprehensive checklist  
**Date**: 2024-10-18  
**Author**: NexRig Development Team

---

## Usage Notes

**For Progressive Review**: Use relevant sections during schematic entry to catch issues early.

**For Final Review**: Complete all sections before releasing to PCB layout.

**For Team Review**: Assign sections to domain experts (RF engineer reviews RF sections, power engineer reviews power sections, etc.).

**Color Coding in KiCad**: Consider using schematic annotation colors to mark review status (red=needs review, yellow=in progress, green=approved).