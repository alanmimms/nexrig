# NexRig Documentation Plan

## Purpose
This document defines the structure and organization of the NexRig project documentation. It serves as the master plan for creating, consolidating, and maintaining all architecture, design, and implementation documents.

---

## Documentation Philosophy

### Design Principles
1. **Hierarchy**: Organize from system-level down to component-level detail
2. **Single Source of Truth**: Each piece of information lives in exactly one place
3. **Cross-Reference**: Documents reference each other rather than duplicating content
4. **Completeness**: Capture both WHAT (decisions) and WHY (rationale)
5. **Maintainability**: Structure supports updates without causing cascading changes
6. **Accessibility**: Useful for both human readers and AI assistant context

### Target Audiences
- **System Engineers**: Need high-level architecture and subsystem interaction
- **Hardware Engineers**: Need detailed circuit design and component specifications
- **Firmware Developers**: Need interface protocols and hardware control specifications
- **Software Developers**: Need API definitions and DSP algorithm details
- **PCB Designers**: Need layout constraints and routing requirements
- **Test Engineers**: Need validation procedures and acceptance criteria
- **Manufacturing**: Need BOM, assembly notes, and hand-selection requirements

---

## Current State Summary

### Existing Documents (9 total)
| Document | Status | Action Required |
|----------|--------|-----------------|
| FPGA.md | Good | Revise: Add pin assignments, reference interfaces doc |
| Rx input Attenuator.md | Excellent | Rename: ATTENUATOR-DESIGN.md |
| Tx EER.md | Good | Revise: Resolve controller IC conflict, consolidate |
| EER phase modulation.md | Good | Consolidate: Merge into TX-ARCHITECTURE.md |
| Audio codec.md | Good | Split: Extract to SYSTEM and DSP docs |
| UI and summary.md | Good | Split: Extract to SYSTEM, DSP, and UI docs |
| RX-ARCHITECTURE.md | Excellent | Revise: Merge 192kS/s update, add evolution notes |
| Update to 192kS/s for rx.md | Good | Merge: Into RX-ARCHITECTURE-v2.md, then remove |
| Transmitter Low-Pass Filter Array.txt | Excellent | Rename: LPF-ARRAY-DESIGN.md |

### Content Gaps Identified
**Well-Documented**: Receiver front-end, FPGA clocking, EER supply, TX filtering, system philosophy

**Partially Documented**: TX signal path (scattered), PA tank, DPD (brief mentions), firmware architecture, band switching

**Undocumented**: Power architecture, STM32-FPGA protocol, T/R switching, USB Ethernet protocol, calibration procedures, PCB layout guidelines, test procedures, thermal management, complete BOM

### Critical Issues to Resolve
1. **EER Controller IC Conflict**: Tx EER.md specifies LM34936, EER phase modulation.md mentions LM5155
2. **Scattered TX Documentation**: Need consolidation into unified TX-ARCHITECTURE.md
3. **Missing Interface Specs**: SPI register map, GPIO assignments, network protocol undefined
4. **Temperature Grade**: Project uses commercial-grade components (0°C to +70°C)

---

## Proposed Documentation Structure

### Overview: 20 Documents in 5 Tiers

```
NexRig Documentation/
│
├── TIER 1: Project & System (3 docs)
│   ├── PROJECT-OVERVIEW.md ⭐ NEW
│   ├── SYSTEM-ARCHITECTURE.md ⭐ NEW (consolidation)
│   └── INTERFACES-AND-PROTOCOLS.md ⭐ NEW
│
├── TIER 2: Hardware Subsystems (4 docs)
│   ├── RX-ARCHITECTURE.md ✏️ REVISED
│   ├── TX-ARCHITECTURE.md ✏️ NEW (consolidation)
│   ├── FPGA-ARCHITECTURE.md ✏️ REVISED
│   └── POWER-ARCHITECTURE.md ⭐ NEW
│
├── TIER 3: Component Designs (6 docs)
│   ├── ATTENUATOR-DESIGN.md ✏️ RENAME
│   ├── PRESELECTOR-DESIGN.md ⭐ NEW (extract)
│   ├── LPF-ARRAY-DESIGN.md ✏️ RENAME
│   ├── PA-TANK-DESIGN.md ⭐ NEW
│   ├── EER-SUPPLY-DESIGN.md ✏️ REVISED
│   └── DPD-SYSTEM-DESIGN.md ⭐ NEW
│
├── TIER 4: Firmware & Software (3 docs)
│   ├── STM32-FIRMWARE-ARCHITECTURE.md ⭐ NEW
│   ├── PC-APPLICATION-ARCHITECTURE.md ✏️ NEW (consolidation)
│   └── NETWORK-PROTOCOL-SPEC.md ⭐ NEW
│
└── TIER 5: Implementation (4 docs)
    ├── PCB-LAYOUT-GUIDELINES.md ⭐ NEW
    ├── CALIBRATION-PROCEDURES.md ⭐ NEW
    ├── TEST-AND-VALIDATION.md ⭐ NEW
    └── BOM-AND-SOURCING.md ⭐ NEW

Legend:
⭐ NEW: Needs creation (13 documents)
✏️ REVISED: Needs consolidation/editing (5 documents)
✏️ RENAME: Minimal changes (2 documents)
```

---

## Tier 1: Project & System Level

### 1. PROJECT-OVERVIEW.md ⭐ NEW
**Purpose**: 30,000-foot view for newcomers and stakeholders

**Target Length**: 2000-3000 words

**Contents**:
- Project goals and philosophy (open-source SDR, setbox innovation)
- Target specifications (50W HF, all amateur bands, supported modes)
- Major architectural decisions and rationale
- Key innovations (triple-QSD, EER, preselector approach)
- Development status and roadmap
- How to navigate the documentation
- Quick-start guide for contributors

**Sources**: 
- Extract from Audio codec.md
- Create new high-level content
- Summarize key points from all subsystem docs

**Priority**: HIGH - Create in Phase 2 (Foundation)

---

### 2. SYSTEM-ARCHITECTURE.md ⭐ NEW (consolidation)
**Purpose**: System-level block diagram and subsystem interaction

**Target Length**: 5000-7000 words

**Contents**:
- Complete system block diagram (all major subsystems)
- Subsystem responsibilities:
  - STM32: Real-time control, hardware management, basic DSP
  - FPGA: Clock generation, NCOs, precise timing
  - PC Application: Complex DSP, UI, mode processing
- Major signal paths:
  - RX: Antenna → Attenuator → Preselector → QSD → ADC → STM32 → PC
  - TX: PC → STM32 → FPGA → PA → Tank → LPF → Antenna
- Control paths (user → UI → STM32 → hardware)
- Power architecture overview (12V input, rails, sequencing)
- Interface definitions between subsystems (summary, details in INTERFACES doc)
- System timing and sequencing
- Setbox architecture and configuration management
- Design philosophy and trade-offs

**Sources**: 
- Consolidate Audio codec.md + UI and summary.md
- Extract system-level content from subsystem docs
- Create new integration content

**Priority**: HIGH - Create in Phase 2 (Foundation)

---

### 3. INTERFACES-AND-PROTOCOLS.md ⭐ NEW
**Purpose**: Define all interface contracts between subsystems

**Target Length**: 6000-8000 words

**Contents**:
- **STM32 ↔ FPGA**:
  - SPI protocol (master/slave, clock speed, mode)
  - Register map (frequency tuning words, phase offsets, control bits)
  - Timing requirements
  - Power-up initialization sequence
  
- **STM32 ↔ PC**:
  - USB Ethernet (driver, IP assignment)
  - Packet format (I/Q data streaming, control messages, telemetry)
  - Network protocol (UDP/TCP/WebSocket decision)
  - Discovery (mDNS, DHCP, DNS, captive portal)
  - Error handling and recovery
  
- **STM32 ↔ Hardware**:
  - GPIO mapping (attenuator, preselector, PA tank, relays, T/R switching)
  - ADC channel assignments (six QSD I/Q channels)
  - DAC outputs (EER amplitude signal)
  - SPI to peripherals (if any)
  - I2C devices (if any)
  
- **PC ↔ User**:
  - UI update mechanism (WebSocket/IPC)
  - Command structure
  - Setbox API
  
- **Calibration Data**:
  - Storage format (binary, JSON, etc.)
  - Location (EEPROM, flash, file system)
  - Structure (per-band coefficients, global offsets)

**Sources**: 
- Extract from multiple docs
- Create detailed specifications (currently undefined)

**Priority**: HIGH - Create in Phase 3 (enables firmware/software development)

---

## Tier 2: Hardware Subsystem Architecture

### 4. RX-ARCHITECTURE.md ✏️ REVISED (consolidation)
**Purpose**: Complete receiver signal path documentation

**Target Length**: 8000-10000 words

**Current State**: Excellent comprehensive document

**Revision Actions**:
- ✅ Merge "Update to 192kS/s for rx.md" content
  - Update ADC section (TI codec → AKM AK5578, 96kS/s → 192kS/s)
  - Update preselector tuning requirements (±50kHz → ±100kHz tolerance)
  - Update tuning step margins (especially 20m, 17m improved)
  - Add software compensation strategy for preselector rolloff
- ✅ Add "Design Evolution" section noting ADC upgrade rationale
- ✅ Reduce FPGA clock generation detail (reference FPGA-ARCHITECTURE instead)
- ✅ Add clear cross-references to component design docs
- ✅ Update frequency response compensation algorithm section
- ✅ Verify all component values match schematics

**Sources**: 
- Current RX-ARCHITECTURE.md (keep bulk of content)
- Merge Update to 192kS/s for rx.md
- Extract relevant sections from FPGA.md

**Priority**: HIGH - Revise in Phase 3

---

### 5. TX-ARCHITECTURE.md ✏️ NEW (consolidation)
**Purpose**: Complete transmitter signal path documentation

**Target Length**: 8000-10000 words

**Contents**:
- Signal path overview (PC → STM32 → FPGA → PA → Tank → LPF → Antenna)
- DSP chain on STM32:
  - I/Q input from PC (sample rate, format)
  - Interpolation to DAC rate
  - I/Q to polar conversion (amplitude, phase)
  - DAC output configuration
- FPGA phase modulation:
  - NCO4 architecture
  - Phase accumulator (32-bit resolution)
  - Phase modulation input from STM32
  - Square wave output to PA gate drive
- PA architecture:
  - Class-E topology rationale
  - MOSFET selection (STW25N55M5)
  - Gate drive transformer (turns ratio, core, winding)
  - Gate driver IC (UCC27511)
  - Optimal load impedance (6Ω)
- PA tank circuit:
  - Switched inductor bank (reference PA-TANK-DESIGN for detail)
  - Binary-weighted capacitor bank (PIN diode switching)
  - 6Ω → 50Ω transformation
  - Band coverage strategy
- EER tracking supply:
  - **CRITICAL: Resolve LM34936 vs LM5155 controller conflict**
  - Reference EER-SUPPLY-DESIGN for detailed design
  - Amplitude signal from STM32 DAC
  - Tracking bandwidth requirements (>75kHz)
  - Supply voltage range (0-25V)
- Output filtering:
  - Reference LPF-ARRAY-DESIGN for detail
  - Six-filter consolidation strategy
  - Harmonic rejection performance
- Digital Pre-Distortion:
  - Reference DPD-SYSTEM-DESIGN for detail
  - Feedback path architecture
  - Calibration procedure overview
- Band switching sequencing:
  - PA tank tuning
  - LPF selection
  - Preselector coordination
  - T/R switching interlocks
- Performance predictions:
  - Output power (50W target)
  - Efficiency (EER advantage)
  - Harmonic rejection (with LPF)
  - Spectral purity (with DPD)

**Sources**: 
- Consolidate Tx EER.md + EER phase modulation.md
- Resolve controller IC conflict
- Extract from FPGA.md (NCO4)
- Create band switching section

**Priority**: HIGH - Create in Phase 3

**CRITICAL ACTION**: Determine correct EER controller IC before creating this document

---

### 6. FPGA-ARCHITECTURE.md ✏️ REVISED
**Purpose**: FPGA digital signal generation subsystem

**Target Length**: 4000-5000 words

**Current State**: Good focused document

**Revision Actions**:
- ✅ Add explicit pin assignment table (physical pins for clock outputs, SPI, etc.)
- ✅ Expand SPI interface section (summary here, detail in INTERFACES doc)
- ✅ Add NCO4 details (currently light on TX modulation NCO)
- ✅ Add clock output to STM32 (synchronization clock)
- ✅ Reference INTERFACES-AND-PROTOCOLS.md for SPI register map
- ✅ Add implementation notes (resource utilization, timing constraints)
- ✅ Verify against schematics

**Sources**: 
- Current FPGA.md
- Extract NCO4 info from TX docs
- Add pin assignment info from schematics

**Priority**: MEDIUM - Revise in Phase 3

---

### 7. POWER-ARCHITECTURE.md ⭐ NEW
**Purpose**: System power distribution and management

**Target Length**: 4000-6000 words

**Contents**:
- Input power specification:
  - 12V DC nominal (range: 11V-15V per EER spec)
  - Current budget (calculate total)
  - Connector type
  - Reverse polarity protection
- Power domains and rails:
  - Digital 3.3V: STM32, FPGA I/O, logic (current budget)
  - Digital 1.2V: FPGA core if needed (verify from datasheet)
  - Analog 5V: ADC, op-amps, analog circuits (current budget)
  - RF 12V: Relays, PIN diode bias (current budget)
  - PA supply: 0-25V variable from EER converter (up to 75W)
- Regulators and converters:
  - Part selection for each rail
  - Topology (LDO, buck, boost, etc.)
  - Efficiency and thermal analysis
- Load switch control:
  - Which rails use load switches
  - Control from STM32
  - Purpose (sequencing, isolation)
- Power-up sequence:
  - Order of rail activation
  - Delays between rails
  - FPGA core before configuration
  - Verification signals
- Current budgeting:
  - Per-rail load calculation
  - Margin analysis
  - Peak vs continuous current
- Decoupling strategy:
  - Bulk capacitance per rail
  - Local decoupling guidelines
  - Filter requirements
- Thermal considerations:
  - Heat sources (regulators, EER converter, PA)
  - Thermal resistance calculations
  - Cooling strategy (natural convection, forced air)
- Protection:
  - Overcurrent protection
  - Thermal shutdown
  - Fault indication

**Sources**: 
- Extract from multiple docs (EER supply has 12V input specs)
- Create new content from schematic review
- Calculate budgets from component datasheets

**Priority**: MEDIUM - Create in Phase 3

---

## Tier 3: Detailed Component/Circuit Designs

### 8. ATTENUATOR-DESIGN.md ✏️ RENAME
**Current**: "Rx input Attenuator.md"

**Action**: 
- Rename for consistency
- Add control signal mapping (STM32 GPIO assignments)
- Verify against schematic
- Add reference in RX-ARCHITECTURE

**Priority**: LOW - Rename in Phase 4

---

### 9. PRESELECTOR-DESIGN.md ⭐ NEW (extract from RX-ARCHITECTURE)
**Purpose**: Preselector LC tank detailed component design

**Target Length**: 4000-5000 words

**Contents**:
- Q factor selection rationale (Q≤20 for switch protection, voltage analysis)
- Schottky clamp circuit (DC-biased symmetric design, component values)
- Switched inductor bank:
  - Three physical inductors (500nH, 180nH, 68nH)
  - AS183-92LF switch selection rationale
  - Parallel combination for high bands (49.4nH)
  - SPDT switching topology
  - Control signals
- Binary-weighted capacitor bank:
  - 8-bit design (4pF LSB to 512pF MSB)
  - AS183-92LF switches (same part as inductors)
  - SPDT topology (active vs shorted)
  - Total range: 0-1020pF in 4pF steps
- Fixed capacitors (160m, 80m bands):
  - 12000pF for 160m
  - 2000pF for 80m
  - Switching logic
- Band plan:
  - Per-band inductor/capacitor selection
  - Target Q per band
  - Tuning resolution per band
  - Frequency step analysis
- Component selection:
  - Switch voltage/current ratings
  - OFF-state voltage stress analysis
  - Capacitor voltage ratings
  - Inductor saturation analysis
- Parasitic capacitance:
  - Total switch parasitic (~10-13pF)
  - Calibration approach
- Control signals:
  - STM32 GPIO mapping
  - Control logic (active state definitions)
- Performance characteristics:
  - Insertion loss per band
  - Harmonic rejection per band
  - Tuning range verification
- Cost analysis

**Sources**: 
- Extract from RX-ARCHITECTURE.md (Section 2.2 and 2.3)
- Add control signal details from schematic
- Verify component values

**Priority**: MEDIUM - Create in Phase 4

**Rationale**: ~4000 words of detailed component design deserves separate document for clarity

---

### 10. LPF-ARRAY-DESIGN.md ✏️ RENAME
**Current**: "Transmitter Low-Pass Filter Array.txt"

**Action**: 
- Rename to .md for consistency
- Add control signal mapping (STM32 GPIO for relay control)
- Add cross-reference from TX-ARCHITECTURE
- Verify component values against schematic

**Priority**: LOW - Rename in Phase 4

---

### 11. PA-TANK-DESIGN.md ⭐ NEW
**Purpose**: PA output tank circuit and impedance matching

**Target Length**: 4000-5000 words

**Contents**:
- Tank circuit topology:
  - Class-E matching requirements
  - Parallel LC resonant tank
  - Load transformation (6Ω → 50Ω)
- Switched inductor bank:
  - Inductor values per band
  - Core selection (material, size)
  - Switching method (RF relays)
  - Relay specifications
- Binary-weighted capacitor bank:
  - Capacitor values (binary weighting)
  - PIN diode switching (SMP1302-079LF)
  - Hot-side topology rationale
  - Bias circuit (pull-up/pull-down drivers)
  - Forward bias current requirements
  - Reverse bias voltage requirements
- Band coverage strategy:
  - Which L/C combinations for which bands
  - Tuning algorithm
  - Frequency resolution per band
- Component stress analysis:
  - Voltage stress (tank Q, circulating current)
  - Current stress (RMS, peak)
  - Power dissipation
  - Thermal analysis
- Control signals:
  - STM32 GPIO mapping
  - Switching timing (break-before-make)
  - Coordination with LPF switching
- Component specifications:
  - Capacitor paralleling (high-value caps)
  - Inductor winding details
  - PIN diode selection rationale
  - Relay contact ratings
- Tuning procedure:
  - Initial tuning (target frequency)
  - Fine-tuning for SWR
  - Software algorithm

**Sources**: 
- Extract from EER phase modulation.md
- Create detailed component design
- Verify against schematic

**Priority**: MEDIUM - Create in Phase 4

---

### 12. EER-SUPPLY-DESIGN.md ✏️ REVISED (resolve conflict)
**Purpose**: EER tracking power supply detailed design

**Target Length**: 5000-6000 words

**Current State**: Good detail in "Tx EER.md"

**Revision Actions**:
- ✅ **CRITICAL: Resolve LM34936 vs LM5155 controller conflict**
  - Check schematic for actual part used
  - Document conflict and resolution decision
  - Update all references in document
- ✅ Verify all component values against schematic
- ✅ Add detailed feedback loop analysis (compensation, bandwidth)
- ✅ Expand DAC interface specification
- ✅ Add monitoring/telemetry section (ADC feedback)
- ✅ Component stress verification (MOSFETs, inductor, sense resistor)

**Contents** (assuming LM34936 per "Tx EER.md"):
- Topology: 4-switch synchronous buck-boost
- Controller IC: LM34936 configuration
- Power stage components
- Control loop design
- Interface to STM32 (DAC amplitude, ADC monitoring)
- Layout considerations
- Component specifications and BOM

**Sources**: 
- Current Tx EER.md
- Relevant sections from EER phase modulation.md
- Schematic verification

**Priority**: HIGH - Must resolve conflict before Phase 3

---

### 13. DPD-SYSTEM-DESIGN.md ⭐ NEW
**Purpose**: Digital Pre-Distortion system implementation

**Target Length**: 3000-4000 words

**Contents**:
- DPD rationale:
  - Class-E PA non-linearity (AM/AM, AM/PM)
  - Spectral purity requirements
  - FCC compliance margin
- Memory polynomial model:
  - Model structure (order, memory depth)
  - Coefficient format
  - Polar domain operation (amplitude, phase)
- Feedback path design:
  - Output coupler (570kΩ / 51Ω resistive divider per spec)
  - Buffer amplifier (GALI-74+ MMIC)
    - Gain, bandwidth, linearity
    - Power supply and decoupling
  - Injection point (Tayloe detector, bypass LNA)
  - Isolation during normal RX (relay or switch)
- Calibration procedure:
  - Test signal generation
  - Feedback signal capture
  - LMS algorithm implementation
  - Coefficient convergence criteria
  - Calibration triggers (band change, temperature, periodic)
- Performance targets:
  - IMD specification (IM3, IM5)
  - ACPR specification (adjacent channel power ratio)
  - Pre-DPD vs post-DPD comparison
- STM32 implementation:
  - Processing load estimate
  - Update rate
  - Coefficient storage
- Coefficient storage and management:
  - Per-band coefficients
  - Non-volatile storage
  - Factory vs user calibration

**Sources**: 
- Extract from EER phase modulation.md
- Create detailed specification
- Verify feedback path against schematic

**Priority**: MEDIUM - Create in Phase 4

---

## Tier 4: Firmware & Software Architecture

### 14. STM32-FIRMWARE-ARCHITECTURE.md ⭐ NEW
**Purpose**: Embedded firmware structure and responsibilities

**Target Length**: 6000-8000 words

**Contents**:
- Firmware architecture overview:
  - Real-time OS or bare-metal? (decision and rationale)
  - Task/thread structure
  - Interrupt priorities
- Hardware abstraction layer:
  - Peripheral drivers (ADC, DAC, SPI, UART, USB, GPIO)
  - HAL for hardware control (attenuator, preselector, PA tank, relays)
- Real-time responsibilities:
  - ADC data acquisition:
    - DMA configuration (six channels, 192kS/s)
    - Buffer management (double-buffering, circular)
    - Timing and synchronization
  - DAC output:
    - EER amplitude signal generation
    - Sample rate, resolution
    - DMA configuration
  - GPIO control:
    - Attenuator (8 signals: 4 stages × 2 MOSFETs)
    - Preselector (13+ signals: L switches, C bank, fixed caps)
    - PA tank (inductor relays, capacitor PIN diodes)
    - LPF array (6 relay signals)
    - T/R switching (keying, interlocks)
  - SPI master to FPGA:
    - Register writes (frequency tuning, phase offsets)
    - Timing requirements
  - T/R sequencing:
    - Timing diagram (relay delays, PA enable, antenna switching)
    - Safety interlocks
- DSP chain:
  - Decimation (192kS/s → manageable rate)
  - Packetization for USB Ethernet
  - I/Q to polar conversion (TX path)
  - Interpolation (TX path)
- USB Ethernet stack:
  - lwIP configuration
  - DHCP server implementation
  - DNS server (captive portal, fallback)
  - mDNS responder
- Network protocol handler:
  - Packet parsing
  - Command dispatch
  - I/Q streaming
  - Telemetry reporting
- Calibration data management:
  - Load from non-volatile storage
  - Apply to hardware (FPGA registers, gain corrections)
  - Update from PC calibration routines
- Configuration storage:
  - Setbox state persistence
  - Band memory
  - User settings
- State machines:
  - Startup sequence
  - T/R switching
  - Band changes
  - Fault handling
- Interrupt priorities:
  - Critical (ADC DMA)
  - High (USB, SPI)
  - Medium (GPIO, timers)
  - Low (housekeeping)
- Timing budgets:
  - CPU load analysis
  - Worst-case execution time
  - Margin for future features
- Memory usage:
  - RAM allocation (buffers, stacks, heap)
  - Flash allocation (code, constants, calibration data)

**Sources**: 
- Extract from UI and summary.md
- Create new detailed specification
- Reference INTERFACES doc for protocols

**Priority**: HIGH - Create in Phase 3 (enables firmware development)

---

### 15. PC-APPLICATION-ARCHITECTURE.md ✏️ NEW (consolidation)
**Purpose**: Host PC application structure (Electron app)

**Target Length**: 6000-7000 words

**Contents**:
- Application architecture:
  - Electron framework rationale
  - Process model (main process, renderer processes)
  - Security considerations (node integration, context isolation)
- Native C++ DSP backend:
  - Why native? (performance for real-time DSP)
  - Integration with Electron (N-API, node-addon-api)
  - Threading model (worker threads for DSP)
- DSP responsibilities:
  - Modulation (all modes):
    - SSB (USB, LSB): Hilbert transform, filtering
    - CW: Keying envelope shaping, sidetone generation
    - AM: Carrier generation, modulation depth
    - FM: Frequency modulation, pre-emphasis/de-emphasis
    - Digital modes: FT8, RTTY, PSK31 (modem implementations)
  - Demodulation (all modes):
    - Mode-specific demodulation algorithms
    - AGC implementation
    - AFC (automatic frequency control)
  - Filtering:
    - FIR bandpass filters (user-adjustable)
    - Notch filters (manual, auto-notch)
    - Noise reduction (spectral subtraction, Wiener filtering)
  - Visualization:
    - FFT for spectrum display (size, windowing)
    - Waterfall rendering (30 FPS target)
    - Constellation plot for digital modes
  - Triple-QSD combining:
    - Amplitude/phase matching
    - Harmonic cancellation algorithms
    - Image rejection (QSD1 + QSD2)
  - Calibration algorithms:
    - Coefficient calculation
    - Real-time correction application
- UI framework:
  - Technology stack (HTML/CSS/JavaScript, React? Vue? Svelte?)
  - Component architecture
  - State management (Redux? MobX? Context API?)
- Setbox UI implementation:
  - Configuration hierarchy display
  - Inheritance inspector
  - Live vs saved state differentiation
  - Save/Save As/Revert operations
- User interaction patterns:
  - Keyboard shortcuts (frequency tuning, mode switching, etc.)
  - Mouse controls on waterfall (click to tune, scroll to tune, ctrl-scroll to zoom)
  - Touch support (if applicable)
- Network communication:
  - Connection to STM32 (discovery, connection establishment)
  - I/Q data reception (format, buffering, latency management)
  - Command transmission (frequency, mode, hardware settings)
  - Telemetry display (power, SWR, temperature)
- Audio interface:
  - Microphone input (Web Audio API? Native?)
  - Speaker output (audio routing, volume control)
  - Latency management (audio buffer sizing)
- Installation and distribution:
  - electron-builder configuration
  - Code signing (Windows, macOS)
  - Notarization (macOS)
  - Auto-update implementation
  - Platform-specific installers (.exe, .dmg, .AppImage)
- Cross-platform considerations:
  - Platform detection
  - OS-specific UI tweaks
  - File system access differences
  - Native module compilation

**Sources**: 
- Consolidate UI and summary.md + Audio codec.md
- Create detailed DSP specification
- Create UI implementation details

**Priority**: HIGH - Create in Phase 3 (enables software development)

---

### 16. NETWORK-PROTOCOL-SPEC.md ⭐ NEW
**Purpose**: Communication protocol between STM32 and PC

**Target Length**: 4000-5000 words

**Contents**:
- Physical layer:
  - USB Ethernet (RNDIS or CDC-ECM?)
  - Link-local IPv4 (169.254.x.x/16)
  - IPv6 (link-local fe80::/64)
- Network configuration:
  - mDNS:
    - Hostname: my-sdr.local (configurable?)
    - Service advertisement (_http._tcp)
  - DHCP server (STM32 side):
    - IP pool assignment
    - Lease time
  - DNS server (STM32 side):
    - Captive portal (redirect all queries to STM32 IP)
    - Fallback resolution for .local
- Transport layer decision:
  - UDP: Low latency, acceptable packet loss for I/Q streaming
  - TCP: Reliable delivery for commands, control
  - WebSocket: Bidirectional, works well with web technologies
  - **Decision needed**: Which for each data type?
- Packet format:
  - **I/Q data streaming** (RX path):
    - Format: Binary packed samples? JSON? MessagePack?
    - Frame structure (header, payload, footer/checksum)
    - Sample format (16-bit signed? Float32?)
    - Timestamp (for synchronization)
    - Sequence number (for loss detection)
  - **Command/control messages**:
    - Set frequency (NCO tuning words)
    - Set mode (SSB, CW, AM, FM, digital)
    - Hardware control (attenuator, preselector, PA tank, relays)
    - Calibration commands
  - **Status/telemetry** (from STM32):
    - Forward/reflected power (SWR)
    - Temperature sensors
    - Supply voltages/currents
    - Fault conditions
  - **Configuration management**:
    - Setbox state upload/download
    - Calibration data transfer
- Timing and synchronization:
  - I/Q packet rate (to achieve 192kS/s)
  - Latency budget (STM32 → PC processing delay)
  - Jitter tolerance
  - Clock synchronization (if needed)
- Error handling and recovery:
  - Packet loss detection
  - Retransmission strategy (if applicable)
  - Connection loss recovery
  - Graceful degradation
- Security considerations:
  - Authentication (needed? local network only)
  - Encryption (needed? local network only)
  - Access control (multiple clients?)
- Connection establishment and discovery:
  - PC scans for mDNS hostname
  - Captive portal fallback (if mDNS fails)
  - Connection handshake
  - Version negotiation (protocol version compatibility)
- Flow control:
  - Backpressure handling (PC can't keep up with I/Q stream)
  - Buffer management
  - Adaptive rate control?

**Sources**: 
- Extract from UI and summary.md
- Create detailed specification (currently undefined)

**Priority**: HIGH - Create in Phase 3 (critical for integration)

---

## Tier 5: Implementation & Validation

### 17. PCB-LAYOUT-GUIDELINES.md ⭐ NEW
**Purpose**: PCB design rules and constraints

**Target Length**: 4000-5000 words

**Contents**:
- PCB stackup:
  - Layer count (4-layer? 6-layer?)
  - Impedance control (50Ω traces for RF)
  - Copper weight (2oz for high-current sections)
  - Dielectric material
- Ground plane strategy:
  - Solid copper pour on ground layers
  - Stitching via spacing (<λ/10 at 30MHz)
  - Analog vs digital ground (single-point connection)
  - RF ground (continuous under RF sections)
- Power distribution:
  - Trace width for current capacity
  - Dedicated power planes (if layer count allows)
  - Star power distribution for analog
  - Decoupling capacitor placement (proximity to IC pins)
- RF routing rules:
  - 50Ω impedance control (trace width, spacing, stackup)
  - Differential pair routing (USB, I2S)
  - Via stitching around RF sections
  - Guard traces or ground pour (isolation)
  - Trace length limits (clock distribution, high-speed signals)
- Component placement:
  - Preselector layout:
    - Switch orientation (minimize parasitics)
    - Inductor placement (perpendicular to reduce coupling)
    - Capacitor bank arrangement
  - LPF array layout:
    - Filter spacing (>30mm to minimize coupling)
    - Relay placement (adjacent to filters)
    - Linear topology (input one end, output other end)
  - PA section:
    - Heatsink mounting area
    - MOSFET placement (thermal management)
    - Tank components close to PA
  - ADC/DAC:
    - Analog islands (separate ground, separate power)
    - Crystal/oscillator placement (away from noise sources)
  - STM32 and FPGA:
    - Decoupling capacitor proximity
    - Programming header accessibility
- Thermal considerations:
  - Copper pours for heat spreading
  - Heatsink mounting (mechanical, thermal interface)
  - Thermal vias under power components
  - Component spacing for cooling
- Mechanical constraints:
  - Board outline and mounting holes
  - Enclosure clearance (component height restrictions)
  - Connector placement and orientation
  - Cable routing considerations
- Sensitive analog routing:
  - Avoid routing digital signals near/under ADC
  - Short, direct paths for differential signals
  - Shield sensitive traces with ground
- Test points and debug:
  - Accessible test points (probe access)
  - Ground test points near signal test points
  - Debug header placement
- Assembly considerations:
  - Hand-wound component accessibility (toroids)
  - Hand-selected component marking
  - Rework access (can you remove/replace components?)
  - Polarized component orientation (clear marking)
- Silkscreen:
  - Component reference designators
  - Polarity marks
  - Pin 1 indicators
  - Test point labels
  - Voltage rail labels
  - Version/revision code

**Sources**: 
- Extract from LPF array doc (layout section)
- Create comprehensive guidelines
- Reference subsystem docs for specific requirements

**Priority**: MEDIUM - Create in Phase 5 (before PCB layout phase)

---

### 18. CALIBRATION-PROCEDURES.md ⭐ NEW
**Purpose**: Factory and user calibration methods

**Target Length**: 4000-5000 words

**Contents**:
- Self-calibration overview:
  - Using TX at -40 dBm (safe, below Part 15 limits)
  - Injecting test signals into RX path
  - 90 dB SNR for precise measurements
  - Regulatory compliance (no interference)
- QSD3 duty cycle optimization:
  - Inject carrier at 3f (test frequency)
  - Monitor QSD3 output level
  - Adjust FPGA duty cycle register
  - Null depth target (>60 dB for 0.1% accuracy)
  - Procedure step-by-step
- Amplitude/phase matching (QSD1/QSD2/QSD3):
  - Inject test tones at f-k, f, f+k
  - Measure complex gain (magnitude, phase) per QSD
  - Calculate correction matrices
  - Store coefficients per band
  - Verification measurements
- Preselector characterization:
  - Sweep test frequency (f-100kHz to f+100kHz in 10kHz steps)
  - Measure received signal strength per frequency
  - Build frequency response curve
  - Detect mistuning (peak not at target)
  - Auto-correction (adjust capacitor selection)
  - Store response curve per band
- Harmonic response measurement:
  - Inject 2f, 3f, 5f, 7f test signals
  - Measure actual rejection vs theoretical
  - Calculate correction coefficients for software combining
  - Store per-band harmonic response
- DPD coefficient training:
  - Transmit test signal (multi-tone or noise)
  - Capture feedback signal
  - Run LMS algorithm
  - Iterate until convergence
  - Verify linearity improvement
  - Store coefficients per band
- Calibration data storage:
  - Format (binary, JSON, human-readable?)
  - Location (STM32 flash, external EEPROM, PC file system)
  - Structure (per-band coefficients, global offsets)
  - Backup and restore
- Calibration triggers:
  - On band change (quick verification or full calibration?)
  - On temperature change (>10°C delta?)
  - Periodic (every N minutes of operation?)
  - User-initiated (menu command)
- User-initiated recalibration:
  - UI menu structure
  - Progress indication
  - Time estimate
  - Verification display
- Factory calibration:
  - Additional procedures (if any)
  - Tighter tolerances
  - Reference equipment needed
  - Data to record per unit (serial number, date, values)
- Verification and acceptance criteria:
  - Pass/fail thresholds
  - Performance metrics to verify
  - Regression testing (calibration improves performance)

**Sources**: 
- Extract from RX-ARCHITECTURE.md (Section 7)
- Create detailed step-by-step procedures
- Reference DPD-SYSTEM-DESIGN for DPD calibration

**Priority**: MEDIUM - Create in Phase 5

---

### 19. TEST-AND-VALIDATION.md ⭐ NEW
**Purpose**: Test procedures and acceptance criteria

**Target Length**: 6000-8000 words

**Contents**:
- **Unit Test Procedures** (per subsystem):
  - Attenuator:
    - Insertion loss per attenuation setting
    - Attenuation accuracy (±1 dB tolerance?)
    - Input impedance (50Ω verification)
    - Survival power test (+28 dBm)
  - Preselector:
    - Frequency response sweep (per band)
    - Q factor measurement
    - Tuning range verification
    - Harmonic rejection measurement
    - Switch isolation
  - QSD array:
    - Conversion gain
    - Noise figure
    - Harmonic rejection (each QSD)
    - I/Q balance
    - Channel-to-channel isolation
  - FPGA:
    - Clock output frequencies (verify all NCOs)
    - Clock output phase relationships
    - SPI communication (register read/write)
  - ADC:
    - SNR measurement
    - THD measurement
    - Channel crosstalk
    - Sample rate accuracy
  - PA:
    - Output power per band (50W target)
    - Efficiency measurement
    - Harmonic output (before LPF)
    - Thermal performance (heatsink temperature)
  - EER supply:
    - Output voltage range (0-25V)
    - Tracking bandwidth (>75 kHz)
    - Ripple and noise
    - Efficiency
    - Step response
  - LPF array:
    - Insertion loss per filter per band
    - Harmonic rejection (>60 dBc)
    - Isolation (unused filters)
    - Relay switching time
  - PA tank:
    - Tuning range per band
    - SWR at center frequency
    - Switch isolation
    - Power handling
    
- **Integration Test Procedures**:
  - RX sensitivity:
    - MDS (minimum detectable signal) per band
    - Procedure (signal generator, noise floor measurement)
    - Target specification
  - RX dynamic range:
    - IP3 (third-order intercept point)
    - Blocking dynamic range
    - IMD testing (two-tone test)
  - TX output power:
    - All bands, all modes
    - Dummy load test
    - Power meter verification
  - TX spectral purity:
    - Harmonic content (spectrum analyzer)
    - Spurious emissions (scan ±1 MHz)
    - Adjacent channel power (ACPR for SSB)
  - T/R switching:
    - Timing measurement (scope on T/R lines)
    - Hot switching verification (no damage)
    - Relay sequencing
    - Glitch detection (on output)
  - Calibration effectiveness:
    - Before/after comparison
    - Harmonic rejection improvement
    - Image rejection improvement
    - Linearity improvement (with DPD)
    
- **System Test Procedures**:
  - End-to-end TX/RX:
    - Loop-back test (TX output to RX input with attenuation)
    - Audio quality (subjective and objective)
    - Sidetone generation (CW mode)
  - All-mode operation:
    - SSB: Upper and lower sideband
    - CW: Keying envelope, sidetone
    - AM: Carrier, modulation depth
    - FM: Deviation, CTCSS
    - Digital modes: FT8 decode success rate, RTTY, PSK31
  - Network connectivity:
    - Discovery test (mDNS, captive portal)
    - I/Q streaming (packet loss, latency)
    - Command/response (round-trip time)
    - UI responsiveness
  - All-band operation:
    - Verify RX and TX on all 10 amateur bands
    - Band switching time
    - Settings persistence per band
    
- **Required Test Equipment**:
  - Signal generator (covering 1.8-30 MHz, <-140 dBm to +10 dBm)
  - Spectrum analyzer (covering 1-300 MHz, RBW down to 10 Hz)
  - Power meter (RF power, 50W range)
  - Dummy load (50Ω, 100W capacity)
  - Oscilloscope (>100 MHz bandwidth, 4+ channels)
  - Multimeter (for DC measurements)
  - Vector network analyzer (optional, for impedance measurements)
  - Frequency counter (optional, for clock verification)
  
- **Acceptance Criteria and Specifications**:
  - RX:
    - Sensitivity: <X µV for 10 dB SNR (specify per band)
    - Dynamic range: >Y dB (specify MDS to IP3)
    - Harmonic rejection: >70 dB (3rd harmonic)
  - TX:
    - Output power: 50W ±10% (all bands)
    - Efficiency: >Z% (with EER)
    - Harmonic rejection: >60 dBc (all bands, all modes)
    - Spectral purity: <-60 dBc spurious
  - System:
    - T/R switching time: <50 ms
    - Band switching time: <500 ms
    - Network latency: <100 ms round-trip
    
- **Failure Mode Analysis**:
  - Common failure modes and symptoms
  - Root cause analysis approach
  - Component failure indicators
  
- **Debug Strategies**:
  - Subsystem isolation (using test points, jumpers)
  - Signal injection/monitoring
  - Common issues and solutions
  - When to suspect hardware vs firmware vs software

**Sources**: 
- Create based on design requirements from all docs
- Reference acceptance criteria from architecture docs

**Priority**: MEDIUM - Create in Phase 5

---

### 20. BOM-AND-SOURCING.md ⭐ NEW
**Purpose**: Complete bill of materials with sourcing strategy

**Target Length**: Variable (mostly tabular data)

**Contents**:
- Master BOM:
  - Complete component list
  - Reference designators
  - Part numbers
  - Manufacturers
  - Descriptions (with specifications)
  - Quantity per assembly
  - Unit cost estimate
  - Extended cost
  
- Part Selection Rationale:
  - Why specific parts chosen
  - Critical parameters (voltage, current, frequency, etc.)
  - Alternatives considered
  
- Critical Components:
  - **ICs**:
    - STM32H753 (specify package, speed grade)
    - Lattice iCE40UP3K (specify package)
    - LM34936 (or LM5155 - resolve conflict)
    - AK5578 (8-channel ADC)
    - UCC27511 (gate driver)
    - TLV9062 (op-amp)
  - **RF Switches**:
    - AS183-92LF (preselector, quantity: 13)
    - SMP1302-079LF (PA tank, quantity: TBD)
  - **MOSFETs**:
    - SiR178DP (attenuator, quantity: 8)
    - STW25N55M5 (PA, quantity: 1)
    - CSD18543Q3A (EER supply, quantity: 4)
  - **Relays**:
    - Omron G5V-2 (PA tank, quantity: 3)
    - Omron G6K-2F-Y (LPF array, quantity: 6)
    
- Hand-Selected Components:
  - **LPF capacitors**: C0G/NP0 500V, hand-selected to ±2%
  - List of reference designators requiring hand-selection
  - Selection procedure (capacitance meter, tolerance verification)
  
- Hand-Wound Components:
  - **Inductors**: Specify core type, material, turns, wire gauge, tap positions
  - List of reference designators requiring hand-winding
  - Winding instructions (reference component design docs)
  
- Vendor Recommendations:
  - Primary vendors (Digikey, Mouser, LCSC)
  - Specialty vendors (for RF components, cores, wire)
  - Lead time considerations
  - Minimum order quantities
  
- Alternates and Substitutions:
  - Approved equivalents (for each critical component)
  - Substitution guidelines
  - Performance impact of substitutions
  
- Obsolescence Risk:
  - Parts that are obsolete or NRND
  - Single-source components (risk assessment)
  - Lifecycle status of critical ICs
  - Recommended actions (buy lifetime qty, find alternate, redesign)
  
- Cost Analysis:
  - Target BOM cost (per transceiver)
  - Cost breakdown by subsystem
  - High-cost items (opportunities for cost reduction)
  - Quantity price breaks
  
- Lead Time Considerations:
  - Long lead time items (typically ICs, relays)
  - Stocking strategy
  - Build planning

**Sources**: 
- Extract from all component design docs
- Create master list from schematics
- Add vendor/cost information

**Priority**: MEDIUM - Create in Phase 5 (for procurement)

---

## Implementation Phases

### Phase 1: Planning and Preparation ✓ (CURRENT)
**Objective**: Finalize documentation structure and identify critical issues

**Tasks**:
- ✅ Create DOCUMENTATION-PLAN.md (this document)
- ✅ Create DESIGN-NOTES.md (capture critical issues and decisions)
- ✅ Create SCHEMATIC-REVIEW-CHECKLIST.md
- ⏳ Review schematics to:
  - Resolve EER controller IC conflict (LM34936 vs LM5155)
  - Extract pin assignments for interfaces
  - Identify missing specifications
  - Capture implementation notes
- ⏳ Extract this planning chat into documents

**Deliverables**:
- Documentation structure approved
- Critical issues identified and prioritized
- Schematic review findings documented

---

### Phase 2: Foundation Documents (NEXT)
**Objective**: Create system-level documentation that provides context for all other docs

**Priority Order**:
1. PROJECT-OVERVIEW.md (newcomer onboarding)
2. SYSTEM-ARCHITECTURE.md (system context)
3. Resolve EER controller IC conflict

**Approach**: Start new chat titled "Create NexRig Foundation Documents"

**Deliverables**:
- PROJECT-OVERVIEW.md ready for Project Knowledge
- SYSTEM-ARCHITECTURE.md ready for Project Knowledge
- Clear system-level context established

---

### Phase 3: Core Architecture Documents
**Objective**: Create/revise subsystem and interface documentation

**Priority Order**:
1. INTERFACES-AND-PROTOCOLS.md (critical for firmware/software)
2. TX-ARCHITECTURE.md (consolidate, resolve conflicts)
3. RX-ARCHITECTURE.md (revise, merge 192kS/s update)
4. FPGA-ARCHITECTURE.md (revise, add details)
5. POWER-ARCHITECTURE.md (create new)
6. STM32-FIRMWARE-ARCHITECTURE.md (enable firmware development)
7. PC-APPLICATION-ARCHITECTURE.md (enable software development)
8. NETWORK-PROTOCOL-SPEC.md (critical interface)

**Approach**: 
- Potentially multiple chats (group related docs)
- TX-ARCHITECTURE and EER-SUPPLY-DESIGN together (resolve conflict)
- RX-ARCHITECTURE and FPGA-ARCHITECTURE together (clock generation cross-reference)
- Firmware/software/network docs together (related interfaces)

**Deliverables**:
- All Tier 2 (subsystems) documents complete
- All Tier 4 (firmware/software) documents complete
- Obsolete documents identified for removal

---

### Phase 4: Detailed Component Designs
**Objective**: Document component-level designs

**Priority Order**:
1. Extract PRESELECTOR-DESIGN.md (large, deserves separate doc)
2. PA-TANK-DESIGN.md (create new)
3. DPD-SYSTEM-DESIGN.md (create new)
4. Rename ATTENUATOR-DESIGN.md
5. Rename LPF-ARRAY-DESIGN.md
6. Revise EER-SUPPLY-DESIGN.md (should be done in Phase 3 with TX-ARCH)

**Approach**: 
- Can do 2-3 related docs per chat
- Extraction from existing docs is straightforward

**Deliverables**:
- All Tier 3 (component designs) documents complete

---

### Phase 5: Implementation Documentation
**Objective**: Create practical implementation and validation documents

**Priority Order**:
1. PCB-LAYOUT-GUIDELINES.md (needed before layout phase)
2. CALIBRATION-PROCEDURES.md (detailed procedures)
3. TEST-AND-VALIDATION.md (for bring-up and QA)
4. BOM-AND-SOURCING.md (for procurement)

**Approach**: 
- Separate chat per document (each is substantial)
- Can be done in parallel if multiple contributors

**Deliverables**:
- All Tier 5 (implementation) documents complete
- Ready for PCB layout, manufacturing, testing

---

### Phase 6: Consolidation and Cleanup
**Objective**: Remove obsolete documents, verify structure

**Tasks**:
- Remove obsolete documents from Project Knowledge:
  - Audio codec.md (split into SYSTEM, DSP, UI docs)
  - UI and summary.md (split into SYSTEM, DSP, UI docs)
  - Update to 192kS/s for rx.md (merged into RX-ARCHITECTURE)
  - Tx EER.md (merged into TX-ARCHITECTURE and EER-SUPPLY-DESIGN)
  - EER phase modulation.md (merged into TX-ARCHITECTURE)
- Verify cross-references between documents
- Start new test chat to verify AI can navigate new structure
- Update this DOCUMENTATION-PLAN.md with final status

**Deliverables**:
- Clean, non-redundant documentation structure
- All 20 documents in Project Knowledge
- Old documents archived or deleted

---

## Cross-Reference Strategy

### Document Relationships

**System-Level Documents Reference:**
- PROJECT-OVERVIEW → (references all tier 2 subsystem docs)
- SYSTEM-ARCHITECTURE → (references all tier 2 subsystem docs, INTERFACES)
- INTERFACES-AND-PROTOCOLS → (referenced by all firmware/software docs)

**Subsystem Documents Reference:**
- RX-ARCHITECTURE → FPGA-ARCHITECTURE (clocking), ATTENUATOR-DESIGN, PRESELECTOR-DESIGN, POWER-ARCHITECTURE
- TX-ARCHITECTURE → FPGA-ARCHITECTURE (NCO4), PA-TANK-DESIGN, EER-SUPPLY-DESIGN, LPF-ARRAY-DESIGN, DPD-SYSTEM-DESIGN, POWER-ARCHITECTURE
- FPGA-ARCHITECTURE → INTERFACES-AND-PROTOCOLS (SPI protocol)
- POWER-ARCHITECTURE → (referenced by all hardware subsystems)

**Component Documents Reference:**
- ATTENUATOR-DESIGN → (standalone, referenced by RX-ARCHITECTURE)
- PRESELECTOR-DESIGN → (standalone, referenced by RX-ARCHITECTURE)
- LPF-ARRAY-DESIGN → (standalone, referenced by TX-ARCHITECTURE)
- PA-TANK-DESIGN → (standalone, referenced by TX-ARCHITECTURE)
- EER-SUPPLY-DESIGN → (standalone, referenced by TX-ARCHITECTURE)
- DPD-SYSTEM-DESIGN → (standalone, referenced by TX-ARCHITECTURE)

**Firmware/Software Documents Reference:**
- STM32-FIRMWARE-ARCHITECTURE → INTERFACES-AND-PROTOCOLS, POWER-ARCHITECTURE (sequencing)
- PC-APPLICATION-ARCHITECTURE → NETWORK-PROTOCOL-SPEC
- NETWORK-PROTOCOL-SPEC → (referenced by STM32-FIRMWARE and PC-APPLICATION)

**Implementation Documents Reference:**
- PCB-LAYOUT-GUIDELINES → (references all hardware docs for constraints)
- CALIBRATION-PROCEDURES → RX-ARCHITECTURE (QSD calibration), DPD-SYSTEM-DESIGN
- TEST-AND-VALIDATION → (references all subsystem docs for acceptance criteria)
- BOM-AND-SOURCING → (references all component design docs)

### Cross-Reference Format

**In documents, use this format:**
```markdown
For detailed component specifications, see [PRESELECTOR-DESIGN.md](PRESELECTOR-DESIGN.md).

The SPI protocol between STM32 and FPGA is defined in [INTERFACES-AND-PROTOCOLS.md](INTERFACES-AND-PROTOCOLS.md#stm32-fpga-interface).
```

---

## Document Templates

### Standard Document Header
```markdown
# [Document Title]

**Document Type**: [System Architecture / Subsystem Architecture / Component Design / Implementation]  
**Version**: 1.0  
**Last Updated**: [Date]  
**Status**: [Draft / Review / Approved]  
**Supersedes**: [List any old documents this replaces]  
**Related Documents**: [List cross-references]

## Purpose
[One paragraph describing what this document covers and who should read it]

## Scope
[What is included and what is out of scope]

---

[Rest of content]

---

## Document Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | YYYY-MM-DD | Name | Initial version |
```

### Standard Section Structure (Subsystem Architecture)
```markdown
# [Subsystem Name] Architecture

## 1. Overview
- Purpose and role in system
- Key features
- Major components

## 2. Block Diagram
[ASCII or mermaid diagram]

## 3. Signal Path
[Detailed description of signal flow]

## 4. Detailed Design
[Component-level details, organized by function]

## 5. Interface Specifications
[Summary, reference INTERFACES doc for details]

## 6. Performance Analysis
[Calculations, predictions, margins]

## 7. Design Rationale
[Why choices were made, alternatives considered]

## 8. Implementation Notes
[PCB layout constraints, firmware requirements, etc.]

## 9. Testing and Validation
[How to verify this subsystem works]

## 10. References
[Cross-references to other docs, datasheets, etc.]
```

---

## Success Criteria

### Documentation Is Complete When:
- [ ] All 20 documents created and in Project Knowledge
- [ ] No redundant or obsolete documents remain
- [ ] All cross-references valid and tested
- [ ] All critical issues resolved (EER controller IC, etc.)
- [ ] All component values match schematics
- [ ] All interfaces fully specified
- [ ] Test chat can navigate documentation effectively
- [ ] Human readers can find information quickly

### Documentation Is Maintainable When:
- [ ] Each piece of information exists in exactly one place
- [ ] Changes propagate predictably (update one doc, not many)
- [ ] Version control strategy defined
- [ ] Ownership assigned (who maintains each doc)
- [ ] Update triggers identified (when to revise docs)

---

## Notes and Reminders

### Critical Items for Next Steps:
1. **Resolve EER Controller IC Conflict** (LM34936 vs LM5155) - check schematic
2. **Capture Environmental Spec** (commercial temperature grade: 0°C to +70°C)
3. **Extract Pin Assignments** from schematics for INTERFACES doc
4. **Verify All Component Values** against schematics during doc creation

### Items to Capture in DESIGN-NOTES.md:
- Commercial temperature grade specification
- EER controller IC conflict and resolution
- Any other schematic findings during review
- Implementation decisions not in architecture docs

---

**End of Documentation Plan**