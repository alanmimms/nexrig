# NexRig Design Notes and Issues

## Purpose
This document captures critical design decisions, unresolved issues, and implementation notes discovered during the NexRig development process. It serves as a running list of items that need attention, resolution, or documentation.

**Status**: Living document - updated as issues are discovered and resolved

---

## Environmental and Operating Specifications

### Temperature Grade ⚠️ NEEDS DOCUMENTATION
**Issue**: Project temperature specification not documented in architecture

**Decision**: 
- **Component Temperature Grade**: Commercial (0°C to +70°C)
- Not automotive grade (-40°C to +85°C)
- Not industrial extended range

**Rationale**:
- Target application: Amateur radio station (indoor, climate-controlled environment)
- Cost optimization (commercial parts are less expensive)
- Adequate for typical operating conditions

**Action Items**:
- [ ] Add to PROJECT-OVERVIEW.md (environmental specifications section)
- [ ] Add to BOM-AND-SOURCING.md (component selection criteria)
- [ ] Add to schematic review checklist (verify all parts meet this spec)
- [ ] Verify all selected components meet 0°C to +70°C rating

**Related Documents**: PROJECT-OVERVIEW.md, BOM-AND-SOURCING.md

---

## Critical Design Conflicts

### EER Controller IC Conflict 🔴 CRITICAL - MUST RESOLVE
**Issue**: Two different controller ICs specified in documentation

**Conflicting Information**:
1. **Tx EER.md** (detailed design document):
   - Specifies: Texas Instruments **LM34936**
   - Topology: 4-switch synchronous buck-boost
   - Switching frequency: 500 kHz (set by 15kΩ RT resistor)
   - Detailed component specifications provided
   
2. **EER phase modulation.md** (transmitter overview):
   - Mentions: Texas Instruments **LM5155**
   - Topology: SEPIC (a form of buck-boost)
   - Performance requirement: ~1 MHz switching for >75 kHz bandwidth

**Analysis**:
- LM34936: Buck-boost controller, typical for this application
- LM5155: Wide VIN controller, also capable, but different topology
- Cannot use both - must be one or the other
- Component values and PCB layout differ significantly between choices

**Resolution Path**:
1. Check schematic for actual part used
2. If schematic unclear, make engineering decision based on:
   - Performance requirements (bandwidth, efficiency)
   - Component availability
   - Cost
   - PCB layout complexity
3. Update ALL documentation with chosen controller
4. Verify all component values match chosen controller

**Impact**:
- Affects: TX-ARCHITECTURE.md, EER-SUPPLY-DESIGN.md, POWER-ARCHITECTURE.md
- Affects: Schematic, PCB layout, BOM
- Affects: Firmware (register configuration, control loop)

**Status**: ⏳ UNRESOLVED - Awaiting schematic review

**Action Items**:
- [ ] Review schematic to identify actual controller used
- [ ] If LM34936: Update EER phase modulation.md reference, remove LM5155 mention
- [ ] If LM5155: Update Tx EER.md entirely, recalculate all component values
- [ ] Document resolution decision in this file
- [ ] Update affected architecture documents

**Related Documents**: Tx EER.md, EER phase modulation.md, TX-ARCHITECTURE.md (to be created), EER-SUPPLY-DESIGN.md (to be revised)

---

## Component Selection Notes

### RF Switches - Preselector and PA Tank

#### AS183-92LF (Preselector)
**Decision**: Use AS183-92LF for all preselector switching (inductors and capacitors)

**Rationale**:
- Documented use in preselector applications (Skyworks app notes)
- OFF-state voltage capability validated for tank circuits
- Quantity needed: 13 total (3 inductors + 8 capacitors + 2 fixed caps)
- Cost: ~$1.25 each = $16.25 total

**Alternative Considered**: AS169-73LF (cheaper at $0.85)
- Rejected due to: Unknown OFF-state voltage rating in tank circuit application
- Savings ($5.20 total) not worth risk of field failures

**Status**: ✅ DECIDED

**Related Documents**: PRESELECTOR-DESIGN.md, RX-ARCHITECTURE.md

---

#### SMP1302-079LF (PA Tank Capacitor Switching)
**Decision**: Use SMP1302-079LF PIN diodes for PA tank capacitor switching

**Specification**:
- Breakdown voltage: 200V
- Suitable for hot-side topology
- Requires forward bias (~10mA) and reverse bias (+12V)

**Status**: ✅ SPECIFIED in architecture docs

**Related Documents**: PA-TANK-DESIGN.md (to be created), EER phase modulation.md

---

### ADC Selection

#### AKM AK5578 (8-Channel Audio Codec)
**Decision**: Use AK5578 instead of originally considered TI audio codec

**Upgrade Rationale** (documented in "Update to 192kS/s for rx.md"):
- Sample rate: 192 kS/s (vs 96 kS/s originally)
- Channels: 8 available (need 6 for triple-QSD)
- Cost: Minimal increase vs original
- Benefits:
  - Relaxed preselector tuning (±100kHz vs ±50kHz tolerance)
  - Improved tuning step margins on 20m, 17m
  - Software compensation for preselector rolloff (elegant solution)

**Status**: ✅ DECIDED and documented

**Action Items**:
- [ ] Merge "Update to 192kS/s for rx.md" into RX-ARCHITECTURE.md
- [ ] Remove standalone update document after merge
- [ ] Verify AK5578 specifications in schematic

**Related Documents**: RX-ARCHITECTURE.md, Update to 192kS/s for rx.md

---

### MOSFET Selections

#### Attenuator MOSFETs
**Decision**: SiR178DP (Vishay)

**Specification**:
- V_DS: 20V absolute maximum
- Purpose: Adequate for +28 dBm survival (7.9V peak after clamp)
- Quantity: 8 (4 stages × 2 MOSFETs per stage)

**Status**: ✅ SPECIFIED in Rx input Attenuator.md

**Related Documents**: ATTENUATOR-DESIGN.md (to be renamed)

---

#### PA MOSFET
**Decision**: STW25N55M5 (STMicroelectronics)

**Specification**:
- Package: TO-247 (through-hole for heatsink mounting)
- Gate charge: 19 nC (low for fast switching)
- R_DS(on): 165 mΩ
- Requires physical bolt-on heatsink

**Status**: ✅ SPECIFIED in EER phase modulation.md

**Related Documents**: TX-ARCHITECTURE.md (to be created), PA-TANK-DESIGN.md (to be created)

---

#### EER Supply MOSFETs
**Decision**: CSD18543Q3A (Texas Instruments)

**Specification**:
- Rating: 60V, 5.4 mΩ
- Quantity: 4 (for 4-switch buck-boost topology)
- Application: Synchronous buck-boost converter

**Status**: ✅ SPECIFIED in Tx EER.md

**Related Documents**: EER-SUPPLY-DESIGN.md (to be revised)

---

## Architecture Decisions

### Triple-QSD Receiver Strategy
**Decision**: Three parallel quadrature sampling detectors with different characteristics

**Rationale**:
- QSD1: Standard quadrature (f-k), primary receiver
- QSD2: Standard quadrature (f+k), image rejection
- QSD3: Harmonic rejection (6-phase, 33.33% duty cycle at f), 3f nulling

**Combined Performance**:
- 3rd harmonic: >73 dB rejection (preselector + QSD3)
- Even harmonics: Theoretically infinite (QSD1/QSD2 null)
- Image rejection: Software combining of QSD1 and QSD2

**Status**: ✅ DECIDED and well-documented

**Related Documents**: RX-ARCHITECTURE.md

---

### Preselector Q Factor Limitation
**Decision**: Q ≤ 20 across all bands

**Rationale**:
- Switch protection: Limits tank voltage to safe levels
- With Q=30: 237V peak at survival input (risky for AS183-92LF)
- With Q=20: 158V peak without clamp, 48V peak with Schottky clamp
- Trade-off: Only 2.6 dB less 3rd harmonic rejection vs Q=30
- Combined system (preselector + QSD3) still achieves >70 dB total rejection

**Status**: ✅ DECIDED and documented with analysis

**Related Documents**: RX-ARCHITECTURE.md, PRESELECTOR-DESIGN.md (to be created)

---

### LPF Array Consolidation
**Decision**: Six filters instead of eight (consolidate bands)

**Consolidation Strategy**:
- Filter 1: 160m only
- Filter 2: 80m + 60m
- Filter 3: 40m + 30m
- Filter 4: 20m + 17m
- Filter 5: 15m only (needs good 2f rejection at 42 MHz)
- Filter 6: 12m + 10m

**Benefits**:
- Component savings: $13 per transceiver (~25% reduction)
- All bands still meet >60 dBc harmonic rejection target

**Status**: ✅ DECIDED and documented

**Related Documents**: Transmitter Low-Pass Filter Array.txt (to be renamed LPF-ARRAY-DESIGN.md)

---

### 200Ω Internal LPF Impedance
**Decision**: Use 200Ω internal filter impedance with autotransformer matching

**Rationale**:
- Higher voltage (100V RMS vs 50V RMS at 50W)
- Lower current (0.5A RMS vs 1A RMS)
- Improved component Q
- Reduced capacitor stress (fewer parallel caps needed)
- Lower insertion loss (~0.1 dB improvement)
- Integrated matching (no separate transformers)

**Status**: ✅ DECIDED and documented

**Related Documents**: Transmitter Low-Pass Filter Array.txt

---

## Interface Definitions (To Be Specified)

### STM32 ↔ FPGA SPI Interface ⚠️ NEEDS SPECIFICATION
**Current Status**: Architecture mentions SPI bus, but detailed protocol undefined

**Required Specification**:
- SPI mode (CPOL, CPHA)
- Clock speed (max frequency)
- Register map:
  - NCO1 frequency tuning word (address, format)
  - NCO2 frequency tuning word
  - NCO3 frequency tuning word
  - NCO4 frequency tuning word
  - Phase offset registers
  - Control/status registers
- Transaction format (command byte, data bytes)
- Timing requirements (setup, hold times)

**Action Items**:
- [ ] Define complete register map
- [ ] Document in INTERFACES-AND-PROTOCOLS.md
- [ ] Cross-reference from FPGA-ARCHITECTURE.md and STM32-FIRMWARE-ARCHITECTURE.md

**Related Documents**: INTERFACES-AND-PROTOCOLS.md (to be created), FPGA-ARCHITECTURE.md

---

### STM32 ↔ PC Network Protocol ⚠️ NEEDS SPECIFICATION
**Current Status**: High-level concept documented, detailed protocol undefined

**Known Elements**:
- Physical: USB Ethernet (RNDIS or CDC-ECM)
- Network: IPv4 link-local, IPv6 link-local
- Discovery: mDNS (hostname.local), DHCP server, DNS captive portal

**Required Specification**:
- Transport layer choice (UDP for I/Q? TCP for control? WebSocket?)
- I/Q streaming packet format
- Command/control message format
- Telemetry message format
- Error handling and recovery

**Action Items**:
- [ ] Make transport layer decisions
- [ ] Define all packet formats
- [ ] Document in NETWORK-PROTOCOL-SPEC.md
- [ ] Cross-reference from STM32-FIRMWARE and PC-APPLICATION docs

**Related Documents**: NETWORK-PROTOCOL-SPEC.md (to be created)

---

### STM32 GPIO Assignments ⚠️ NEEDS EXTRACTION FROM SCHEMATIC
**Current Status**: Control signals mentioned in architecture, specific pins not documented

**Required GPIO Mapping**:
- **Attenuator Control** (8 signals):
  - 4 stages × 2 MOSFETs each
  - Active-LOW control (needs hex inverter)
  - Pull-ups for safe default state
  
- **Preselector Control** (13+ signals):
  - 3 inductor switches (SPDT control)
  - 8 capacitor bank switches (SPDT control)
  - 2 fixed capacitor switches (SPDT control)
  
- **PA Tank Control** (TBD signals):
  - Inductor relay control (quantity TBD)
  - Capacitor PIN diode bias control
  
- **LPF Array Control** (6 signals):
  - Relay control for 6 filters
  
- **T/R Switching** (TBD signals):
  - PA enable
  - Antenna relay
  - Other interlocks

- **EER Supply Control**:
  - Enable signal
  - DAC output for amplitude control
  - ADC input for voltage monitoring

**Action Items**:
- [ ] Extract complete GPIO mapping from schematic
- [ ] Document in INTERFACES-AND-PROTOCOLS.md
- [ ] Add pin assignment notes to schematic if not present
- [ ] Verify no GPIO conflicts (same pin assigned twice)

**Related Documents**: INTERFACES-AND-PROTOCOLS.md (to be created), schematic

---

## Power Architecture Notes

### Power Rails Required
**Identified Rails**:
1. **+12V Input**: From external DC supply (11-15V range per EER spec)
2. **+3.3V Digital**: STM32, FPGA I/O, logic ICs
3. **+1.2V Digital**: FPGA core (if required - verify from datasheet)
4. **+5V Analog**: ADC (AK5578), op-amps, analog circuits
5. **+12V RF**: Relay coils, PIN diode reverse bias
6. **0-25V Variable**: PA supply from EER tracking converter (up to 75W)

**Unresolved Questions**:
- Does Lattice iCE40UP3K require separate 1.2V core supply or integrated?
- What are the current requirements for each rail? (needs calculation)
- Which rails need load switches for sequencing?
- What is the power-up sequence?

**Action Items**:
- [ ] Verify FPGA power requirements from datasheet
- [ ] Calculate current budget for each rail
- [ ] Define power-up sequence
- [ ] Specify regulators for each rail
- [ ] Document in POWER-ARCHITECTURE.md (to be created)

**Related Documents**: POWER-ARCHITECTURE.md (to be created)

---

### Power Sequencing ⚠️ NEEDS DEFINITION
**Known Requirements**:
- FPGA core voltage before I/O voltage (typical FPGA requirement)
- FPGA configured before STM32 attempts SPI communication
- Load switches controlled by STM32 for subsystem power control

**Unresolved Questions**:
- What is the exact sequence of rail activation?
- What delays are needed between rails?
- Which STM32 GPIO controls which load switch?
- How does STM32 verify power good before proceeding?

**Action Items**:
- [ ] Define complete power-up sequence with timing
- [ ] Document in POWER-ARCHITECTURE.md
- [ ] Add power sequencing verification to test procedures

**Related Documents**: POWER-ARCHITECTURE.md (to be created), STM32-FIRMWARE-ARCHITECTURE.md (to be created)

---

## Mechanical and Thermal Notes

### Heatsink Requirements
**Components Requiring Heatsinks**:
1. **PA MOSFET (STW25N55M5)**:
   - Package: TO-247 (designed for heatsink mounting)
   - Power dissipation: ~5-10W at 50W output (depends on efficiency)
   - Bolt-on heatsink required
   
2. **EER Supply MOSFETs (4× CSD18543Q3A)**:
   - Power dissipation: Distributed across 4 devices
   - May need heatsinking depending on layout and airflow
   
3. **Voltage Regulators**:
   - Power dissipation depends on chosen regulators and currents
   - Calculate per rail after regulator selection

**Thermal Design Questions**:
- Natural convection or forced air cooling?
- Enclosure size and ventilation?
- Maximum ambient temperature (given commercial 0-70°C rating)?
- Thermal resistance calculations needed

**Action Items**:
- [ ] Calculate thermal resistance for each power component
- [ ] Specify heatsink requirements
- [ ] Define cooling strategy
- [ ] Document in PCB-LAYOUT-GUIDELINES.md and mechanical design doc

**Related Documents**: PCB-LAYOUT-GUIDELINES.md (to be created)

---

## Firmware Architecture Notes

### Real-Time OS Decision ⚠️ NEEDS DECISION
**Question**: Bare-metal or RTOS for STM32 firmware?

**Considerations**:
- **Bare-metal**:
  - Simpler, more predictable timing
  - Full control over execution flow
  - Adequate for relatively simple control application
  
- **RTOS** (FreeRTOS, Zephyr, etc.):
  - Task scheduling and prioritization
  - Better code organization for complex application
  - USB stack integration easier
  - Overhead in processing and memory

**Current Application Complexity**:
- Real-time ADC/DAC streaming
- USB Ethernet networking (lwIP stack)
- GPIO control (attenuator, preselector, PA tank, relays)
- SPI to FPGA
- State machines (T/R switching, band changes)

**Preliminary Assessment**: RTOS likely beneficial given USB stack and multiple concurrent tasks

**Action Items**:
- [ ] Make RTOS decision (bare-metal vs which RTOS)
- [ ] Document rationale
- [ ] Define task structure if RTOS chosen
- [ ] Document in STM32-FIRMWARE-ARCHITECTURE.md

**Related Documents**: STM32-FIRMWARE-ARCHITECTURE.md (to be created)

---

## Software Architecture Notes

### PC Application Framework Decision ⚠️ NEEDS DETAIL
**Known**: Using Electron framework

**Unresolved Details**:
- **UI Framework**: React? Vue? Svelte? Plain JavaScript?
- **State Management**: Redux? MobX? Context API? None?
- **DSP Backend**: Node native addons? N-API? WASM?
- **Audio API**: Web Audio API? Native library?

**Action Items**:
- [ ] Make UI framework decision
- [ ] Define state management approach
- [ ] Specify DSP backend integration method
- [ ] Document in PC-APPLICATION-ARCHITECTURE.md

**Related Documents**: PC-APPLICATION-ARCHITECTURE.md (to be created)

---

## Calibration Strategy Notes

### Self-Calibration Capability
**Innovation**: Using transmitter at -40 dBm as calibration signal source

**Benefits**:
- 90 dB SNR (above -130 dBm noise floor)
- No external equipment needed
- Automated calibration possible
- Below Part 15 limits (no interference)

**Calibration Procedures Needed**:
1. QSD3 duty cycle optimization (3f nulling)
2. Amplitude/phase matching between QSD1/QSD2/QSD3
3. Preselector frequency response characterization
4. Harmonic response measurement (actual vs theoretical)
5. DPD coefficient training

**Status**: ✅ CONCEPT DOCUMENTED in RX-ARCHITECTURE.md

**Action Items**:
- [ ] Create detailed step-by-step procedures
- [ ] Define calibration data format and storage
- [ ] Document in CALIBRATION-PROCEDURES.md

**Related Documents**: CALIBRATION-PROCEDURES.md (to be created), RX-ARCHITECTURE.md

---

## Test Equipment Requirements

### Minimum Required Equipment
**For Comprehensive Testing**:
- Signal generator (1.8-30 MHz, -140 dBm to +10 dBm)
- Spectrum analyzer (1-300 MHz, RBW to 10 Hz)
- RF power meter (50W range)
- 50Ω dummy load (100W capacity)
- Oscilloscope (>100 MHz, 4+ channels)
- Multimeter (DC measurements)

**Optional but Useful**:
- Vector network analyzer (impedance measurements)
- Frequency counter (clock verification)
- Audio analyzer

**Action Items**:
- [ ] Finalize test equipment list
- [ ] Document in TEST-AND-VALIDATION.md

**Related Documents**: TEST-AND-VALIDATION.md (to be created)

---

## Documentation Status Tracking

### Documents Requiring Creation (13 total)
- [ ] PROJECT-OVERVIEW.md
- [ ] SYSTEM-ARCHITECTURE.md
- [ ] INTERFACES-AND-PROTOCOLS.md
- [ ] TX-ARCHITECTURE.md
- [ ] POWER-ARCHITECTURE.md
- [ ] PRESELECTOR-DESIGN.md
- [ ] PA-TANK-DESIGN.md
- [ ] DPD-SYSTEM-DESIGN.md
- [ ] STM32-FIRMWARE-ARCHITECTURE.md
- [ ] PC-APPLICATION-ARCHITECTURE.md
- [ ] NETWORK-PROTOCOL-SPEC.md
- [ ] PCB-LAYOUT-GUIDELINES.md
- [ ] CALIBRATION-PROCEDURES.md
- [ ] TEST-AND-VALIDATION.md
- [ ] BOM-AND-SOURCING.md

### Documents Requiring Revision (5 total)
- [ ] RX-ARCHITECTURE.md (merge 192kS/s update)
- [ ] TX-ARCHITECTURE.md (consolidate Tx EER + EER phase modulation)
- [ ] FPGA-ARCHITECTURE.md (add pin assignments, expand NCO4)
- [ ] EER-SUPPLY-DESIGN.md (resolve controller conflict)
- [ ] ATTENUATOR-DESIGN.md (rename, add GPIO mapping)

### Documents Requiring Rename Only (2 total)
- [ ] Rx input Attenuator.md → ATTENUATOR-DESIGN.md
- [ ] Transmitter Low-Pass Filter Array.txt → LPF-ARRAY-DESIGN.md

### Documents to Remove After Consolidation (5 total)
- [ ] Audio codec.md (split into SYSTEM, DSP, UI docs)
- [ ] UI and summary.md (split into SYSTEM, DSP, UI docs)
- [ ] Update to 192kS/s for rx.md (merge into RX-ARCHITECTURE)
- [ ] Tx EER.md (merge into TX-ARCHITECTURE and EER-SUPPLY-DESIGN)
- [ ] EER phase modulation.md (merge into TX-ARCHITECTURE)

---

## Schematic Review Findings
**Status**: ⏳ PENDING - Awaiting schematic review in Phase 1

**To Be Added During Review**:
- EER controller IC identification (LM34936 or LM5155?)
- Complete GPIO pin assignments
- Missing component specifications
- Power sequencing implementation details
- Any conflicts between schematic and architecture docs

---

## Manufacturing and Assembly Notes

### Hand-Selected Components
**Components Requiring Manual Selection**:
- LPF capacitors: C0G/NP0 500V, select to ±2% tolerance
- List specific reference designators (from schematic)

### Hand-Wound Components
**Components Requiring Manual Winding**:
- LPF inductors: Various toroids with specific turns and tap points
- PA tank inductors: TBD cores and turns
- Gate drive transformer: Binocular core, turns ratio
- List specific reference designators (from schematic)

**Action Items**:
- [ ] Create complete list from schematic
- [ ] Document winding instructions per component
- [ ] Document in BOM-AND-SOURCING.md and component design docs

**Related Documents**: BOM-AND-SOURCING.md (to be created), component design docs

---

## Open Design Questions

### Questions Requiring Resolution

1. **T/R Switching Timing**: What are the exact timing requirements and interlock logic?
   - Related: TX-ARCHITECTURE.md, STM32-FIRMWARE-ARCHITECTURE.md

2. **Band Switching Coordination**: How do preselector, PA tank, and LPF switching coordinate?
   - Related: TX-ARCHITECTURE.md, STM32-FIRMWARE-ARCHITECTURE.md

3. **Calibration Data Storage**: Where and in what format?
   - Flash on STM32? External EEPROM? File on PC?
   - Related: CALIBRATION-PROCEDURES.md, STM32-FIRMWARE-ARCHITECTURE.md

4. **PC DSP Threading**: How to structure multi-threaded DSP processing?
   - Related: PC-APPLICATION-ARCHITECTURE.md

5. **Setbox Serialization**: How to save/load/transfer configurations?
   - Related: PC-APPLICATION-ARCHITECTURE.md, NETWORK-PROTOCOL-SPEC.md

---

## Lessons Learned and Best Practices

### Documentation Workflow
**What Works Well**:
- Creating detailed checklists before implementation (schematic review)
- Capturing design rationale alongside decisions
- Using structured documentation plan (this document and DOCUMENTATION-PLAN.md)
- Extracting knowledge from conversational chats into distilled docs

**To Improve**:
- Resolve conflicts earlier (EER controller IC should have been caught sooner)
- Document environmental specs upfront (temperature grade, etc.)
- Create interface specs before detailed subsystem design

---

## Change Log

| Date | Item | Change | Impact |
|------|------|--------|--------|
| 2024-10-18 | Temperature grade | Added commercial (0-70°C) specification | PROJECT-OVERVIEW, BOM |
| 2024-10-18 | EER controller | Identified LM34936 vs LM5155 conflict | TX-ARCH, EER-SUPPLY |
| 2024-10-18 | Documentation plan | Created 20-document structure | All docs |

---

**Document Status**: Living document - continuously updated  
**Last Updated**: 2024-10-18  
**Maintainer**: NexRig Development Team