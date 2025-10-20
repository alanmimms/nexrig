# NexRig Documentation Structure Analysis & Recommendations

## Current State Analysis

### Existing Documents Overview

| Document | Primary Focus | Scope | Status |
|----------|---------------|-------|--------|
| **FPGA** | FPGA subsystem, NCO architecture | Subsystem | Good detail, focused |
| **Rx input Attenuator** | Attenuator circuit design | Component | Excellent detail |
| **Tx EER** | EER tracking power supply | Component | Detailed design |
| **EER phase modulation** | Full TX architecture | Subsystem | Broad coverage |
| **Audio codec** | System overview, setbox concept | System | High-level philosophy |
| **UI and summary** | DSP partitioning, Electron app | System + Software | Architecture decisions |
| **RX-ARCHITECTURE.md** | Complete RX signal path | Subsystem | Very comprehensive |
| **Update to 192kS/s for rx** | ADC upgrade rationale | Amendment | Should be merged |
| **Transmitter Low-Pass Filter Array** | TX output filtering | Component | Excellent detail |

### Content Distribution Analysis

**Well-Documented Areas:**
- ✅ Receiver front-end (preselector, attenuator, QSD array)
- ✅ FPGA clock generation and NCO architecture
- ✅ EER power supply and tracking modulation
- ✅ Transmitter output filtering
- ✅ System-level philosophy (setbox, DSP partitioning)
- ✅ UI application architecture

**Partially Documented Areas:**
- ⚠️ Transmitter signal path (scattered across multiple docs)
- ⚠️ PA tank circuit and impedance matching (mentioned but not detailed)
- ⚠️ Digital Pre-Distortion implementation (mentioned, not specified)
- ⚠️ STM32 firmware architecture (alluded to, not documented)
- ⚠️ Band switching logic and control sequencing (mentioned, not detailed)

**Undocumented or Under-Documented Areas:**
- ❌ Power supply architecture (12V distribution, sequencing, load switches)
- ❌ STM32-FPGA SPI interface protocol
- ❌ T/R switching and sequencing (timing, interlocks)
- ❌ USB Ethernet interface and networking stack
- ❌ Calibration data storage and management
- ❌ Thermal management strategy
- ❌ PCB layout guidelines and constraints (mentioned in LPF doc only)
- ❌ Test and validation procedures
- ❌ Network protocol between STM32 and PC
- ❌ PC application DSP chain details
- ❌ Frontend protection and fault handling

### Redundancy and Overlap Issues

**EER/Transmitter Content:**
- "Tx EER.md" focuses on LM34936 tracking supply
- "EER phase modulation.md" covers entire TX including LM5155 reference (conflict?)
- Overlap: Both discuss PA, modulation approach, power levels
- **Issue**: Which controller IC is actually used? (LM34936 vs LM5155)

**System Architecture Content:**
- "Audio codec.md" has system overview AND setbox philosophy AND brief subsystem descriptions
- "UI and summary.md" has DSP partitioning AND PC app architecture AND system connectivity
- Overlap: Both discuss STM32 responsibilities, system partitioning
- **Issue**: System-level architecture scattered across multiple docs

**RX Path Content:**
- "RX-ARCHITECTURE.md" is comprehensive and excellent
- "Update to 192kS/s for rx.md" modifies ADC specifications
- "Rx input Attenuator.md" provides detail on one component
- **Issue**: Amendment doc should be merged; component doc is fine to keep separate

## Recommended Documentation Structure

### Tier 1: Project & System Level (3 documents)

#### 1. **PROJECT-OVERVIEW.md** ⭐ NEW
**Purpose**: 30,000-foot view for newcomers and stakeholders

**Contents:**
- Project goals and philosophy (open-source SDR, setbox innovation)
- Target specifications (50W, HF bands, modes supported)
- Major architectural decisions and rationale
- Key innovations (triple-QSD, EER, preselector approach)
- Development status and roadmap
- How to navigate the documentation

**Sources**: Extract from Audio codec.md, create new high-level content

**Target audience**: New contributors, project overview, documentation index

---

#### 2. **SYSTEM-ARCHITECTURE.md** ⭐ NEW (consolidation)
**Purpose**: System-level block diagram and subsystem interaction

**Contents:**
- Complete system block diagram
- Subsystem responsibilities (STM32, FPGA, PC app)
- Major signal paths (RX: antenna → PC, TX: PC → antenna)
- Control paths (user → UI → STM32 → hardware)
- Power architecture overview
- Interface definitions between subsystems
- System timing and sequencing
- Setbox architecture and configuration management

**Sources**: Consolidate from Audio codec.md + UI and summary.md + create new content

**Target audience**: System engineers, integration work, cross-subsystem design

---

#### 3. **INTERFACES-AND-PROTOCOLS.md** ⭐ NEW
**Purpose**: Define all interface contracts between subsystems

**Contents:**
- STM32 ↔ FPGA (SPI protocol, register map, timing)
- STM32 ↔ PC (USB Ethernet, packet format, network protocol)
- STM32 ↔ Hardware (GPIO mapping, control signals, ADC channels)
- PC ↔ User (WebSocket/IPC for UI updates, command structure)
- Calibration data format and storage
- Configuration persistence (setbox serialization)

**Sources**: Extract from multiple docs + create new specifications

**Target audience**: Firmware and software developers, integration testing

---

### Tier 2: Hardware Subsystem Architecture (4 documents)

#### 4. **RX-ARCHITECTURE.md** ✏️ REVISED (consolidation)
**Purpose**: Complete receiver signal path documentation

**Contents**:
- Signal path overview (antenna → attenuator → preselector → QSD → ADC → STM32)
- Input protection (Schottky clamp design)
- Attenuator architecture (reference detailed doc)
- Preselector design (switched L/C tank, Q factor rationale)
- Triple-QSD mixer array (QSD1, QSD2, QSD3 characteristics)
- FPGA clock generation for QSD (4-phase, 6-phase, offsets)
- ADC subsystem (AKM AK5578, 192 kS/s, channel mapping)
- Calibration approach (duty cycle, amplitude/phase matching)
- Performance predictions (sensitivity, dynamic range, harmonic rejection)

**Sources**: Merge RX-ARCHITECTURE.md + Update to 192kS/s + relevant FPGA sections

**Changes from current**:
- ✅ Incorporate 192 kS/s ADC upgrade
- ✅ Add clear component cross-references
- ✅ Remove redundant FPGA clock details (reference FPGA-ARCHITECTURE instead)
- ✅ Add design evolution notes

**Target audience**: RF engineers, receiver design review

---

#### 5. **TX-ARCHITECTURE.md** ✏️ NEW (consolidation)
**Purpose**: Complete transmitter signal path documentation

**Contents**:
- Signal path overview (PC → STM32 → FPGA → PA → Tank → LPF → antenna)
- DSP chain (STM32: I/Q → polar conversion, interpolation)
- FPGA phase modulation (NCO4, phase accumulator)
- PA architecture (Class-E, STW25N55M5, gate drive transformer)
- PA tank circuit (switched inductor/capacitor banks, 6Ω → 50Ω matching)
- EER tracking supply (which controller? LM34936 or LM5155? - RESOLVE)
- Envelope modulator control (DAC → feedback loop → supply voltage)
- Output filtering (reference LPF array doc)
- Digital Pre-Distortion (feedback path, LMS algorithm, memory polynomial)
- Band switching sequencing
- Performance predictions (power, efficiency, distortion)

**Sources**: Consolidate Tx EER.md + EER phase modulation.md + resolve conflicts

**Critical**: Resolve LM34936 vs LM5155 controller discrepancy

**Target audience**: RF engineers, transmitter design review, PA designers

---

#### 6. **FPGA-ARCHITECTURE.md** ✏️ REVISED
**Purpose**: FPGA digital signal generation subsystem

**Contents**:
- System role and responsibilities
- Master clocking (40 MHz TCXO, PLL, 240 MHz internal)
- NCO implementations (NCO1-4: architecture, resolution, frequency range)
- QSD clock generation:
  - NCO1: 4(f-k) for QSD1
  - NCO2: 4(f+k) for QSD2
  - NCO3: 6f for QSD3 with 33.33% duty cycle decoder
  - NCO4: TX phase modulation
- SPI slave interface (register map summary - detail in INTERFACES doc)
- SystemVerilog implementation notes
- Pin assignments and I/O standards
- Clock output to STM32

**Sources**: Current FPGA.md + extract relevant sections from RX-ARCHITECTURE

**Changes from current**:
- ✅ Add explicit pin assignment section
- ✅ Reference INTERFACES doc for detailed SPI protocol
- ✅ Add NCO4 details from TX documentation

**Target audience**: FPGA developers, digital design review

---

#### 7. **POWER-ARCHITECTURE.md** ⭐ NEW
**Purpose**: System power distribution and management

**Contents**:
- Input power (12V DC, current budget)
- Power domains:
  - Digital 3.3V (STM32, FPGA core, logic)
  - Digital 1.2V (FPGA core if needed)
  - Analog 5V (ADC, op-amps)
  - RF 12V (relays, PIN diode bias)
  - PA supply (0-25V variable from EER converter)
- Load switch control and sequencing
- Power-up sequence (FPGA before STM32 configuration? Order?)
- Current budgeting per rail
- Decoupling strategy per subsystem
- Thermal considerations
- Protection (overcurrent, thermal shutdown)

**Sources**: Extract from multiple docs + create new content

**Target audience**: Power supply design, system integration, thermal analysis

---

### Tier 3: Detailed Component/Circuit Designs (6 documents)

#### 8. **ATTENUATOR-DESIGN.md** ✏️ RENAME
**Purpose**: Switched-pad attenuator detailed design

**Current**: "Rx input Attenuator.md" - excellent detail, keep almost as-is

**Changes**:
- Rename for consistency
- Add control signal mapping (which STM32 GPIOs?)
- Add to "References" section in RX-ARCHITECTURE

**Target audience**: Circuit designers, PCB layout, component selection

---

#### 9. **PRESELECTOR-DESIGN.md** ⭐ NEW (extract from RX-ARCHITECTURE)
**Purpose**: Preselector LC tank detailed design

**Contents**:
- Q factor selection rationale (Q≤20 for switch protection)
- Switched inductor bank (L1/L2/L3, AS183-92LF switch selection)
- Binary-weighted capacitor bank (8-bit, switch topology)
- Fixed capacitors (160m/80m bands)
- Band plan and component selection per band
- Tuning resolution analysis
- Control signals (which STM32 GPIOs?)
- Parasitic capacitance handling
- Voltage protection with Schottky clamp
- Performance characteristics per band

**Sources**: Extract from RX-ARCHITECTURE.md (Section 2.2 and 2.3)

**Rationale**: This is ~4000 words of detailed component design that deserves separate doc

**Target audience**: Circuit designers, component selection, PCB layout

---

#### 10. **LPF-ARRAY-DESIGN.md** ✏️ RENAME
**Purpose**: Transmitter output low-pass filter array

**Current**: "Transmitter Low-Pass Filter Array.txt" - excellent, keep almost as-is

**Changes**:
- Rename to .md for consistency
- Add control signal mapping (which STM32 GPIOs for relay control?)
- Cross-reference from TX-ARCHITECTURE
- Add to bill of materials section

**Target audience**: Circuit designers, filter design, component winding

---

#### 11. **PA-TANK-DESIGN.md** ⭐ NEW
**Purpose**: PA output tank and impedance matching

**Contents**:
- Tank circuit topology (Class-E matching requirements)
- Switched inductor bank (values, cores, switching relays)
- Binary-weighted capacitor bank (PIN diode switching, hot-side topology)
- Band coverage strategy (which combinations for which bands)
- 6Ω → 50Ω transformation method
- Component stress analysis (voltage, current, power)
- Control signals and switching logic
- Tuning algorithm (how to select L/C for target frequency)
- Component specifications and sourcing

**Sources**: Extract from EER phase modulation.md + create detailed design

**Rationale**: Currently scattered, needs focused component-level documentation

**Target audience**: RF designers, PA matching, component selection

---

#### 12. **EER-SUPPLY-DESIGN.md** ✏️ REVISED (resolve conflict)
**Purpose**: EER tracking power supply detailed design

**Contents**:
- Topology (4-switch synchronous buck-boost)
- Controller IC (**RESOLVE**: LM34936 or LM5155? Document conflict, choose one)
- Power stage (MOSFETs, inductor, current sense)
- Control loop (feedback, compensation, bandwidth requirements)
- DAC interface (amplitude signal from STM32)
- Filtering and decoupling
- Monitoring (ADC feedback for voltage measurement)
- Layout considerations
- Component specifications and BOM

**Sources**: Consolidate Tx EER.md + relevant sections from EER phase modulation.md

**Critical action**: Document the controller IC conflict and resolve it

**Target audience**: Power supply designers, control loop analysis, component selection

---

#### 13. **DPD-SYSTEM-DESIGN.md** ⭐ NEW
**Purpose**: Digital Pre-Distortion implementation

**Contents**:
- DPD rationale (linearize Class-E PA)
- Memory polynomial model (structure, coefficients)
- Feedback path design:
  - Output coupler (resistive divider spec)
  - GALI-74+ buffer amplifier
  - Injection into Tayloe detector
- Calibration procedure (LMS algorithm)
- Coefficient storage and management
- Performance targets (IMD, ACPR specifications)
- STM32 implementation notes (processing load, update rate)

**Sources**: Extract from EER phase modulation.md + create detailed spec

**Rationale**: Important subsystem, currently only briefly described

**Target audience**: DSP engineers, linearization design, calibration procedures

---

### Tier 4: Firmware & Software Architecture (3 documents)

#### 14. **STM32-FIRMWARE-ARCHITECTURE.md** ⭐ NEW
**Purpose**: Embedded firmware structure and responsibilities

**Contents**:
- Firmware architecture overview
- Hardware abstraction layer (HAL for peripherals)
- Real-time responsibilities:
  - ADC data acquisition (DMA configuration)
  - DAC output (EER amplitude signal generation)
  - GPIO control (attenuator, preselector, PA tank, relays)
  - SPI master to FPGA
  - T/R sequencing and timing
- DSP chain (decimation, I/Q → polar conversion, interpolation)
- USB Ethernet stack (lwIP configuration)
- Network protocol handler (packet processing)
- Calibration data management
- Configuration storage (setbox state)
- State machines (startup, T/R switching, band changes)
- Interrupt priorities and timing budgets
- Memory usage (RAM/Flash allocation)

**Sources**: Extract from UI and summary.md + create new content

**Rationale**: Firmware architecture currently only briefly mentioned

**Target audience**: Firmware developers, real-time system design

---

#### 15. **PC-APPLICATION-ARCHITECTURE.md** ✏️ NEW (consolidation)
**Purpose**: Host PC application structure (Electron app)

**Contents**:
- Application architecture (Electron framework, process model)
- Native C++ DSP backend (why native, what it handles)
- DSP responsibilities:
  - Modulation/demodulation (all modes)
  - Filtering (FIR, notch, noise reduction)
  - Visualization (waterfall, spectrum, constellation)
  - Triple-QSD combining and calibration
  - Harmonic cancellation algorithms
- UI framework (HTML/CSS/JS, React or similar?)
- Setbox UI implementation (inheritance, configuration management)
- User interaction patterns (keyboard shortcuts, mouse controls)
- Network communication (receiving I/Q, sending commands)
- Audio interface (microphone input, speaker output)
- Installation and distribution (electron-builder, auto-updates)
- Cross-platform considerations (Windows, macOS, Linux)

**Sources**: Consolidate UI and summary.md + Audio codec.md

**Rationale**: PC app details scattered, needs unified documentation

**Target audience**: Software developers, UI designers, DSP implementers

---

#### 16. **NETWORK-PROTOCOL-SPEC.md** ⭐ NEW
**Purpose**: Communication protocol between STM32 and PC

**Contents**:
- Physical layer (USB Ethernet, link-local IPv4/IPv6)
- Network configuration:
  - mDNS (hostname: my-sdr.local)
  - DHCP server (STM32 assigns IP to PC)
  - DNS server (captive portal, fallback)
- Transport layer (UDP? TCP? WebSocket?)
- Packet format:
  - I/Q data streaming (RX path, format, framing)
  - Command/control messages (TX settings, hardware control)
  - Status/telemetry (monitoring, calibration data)
- Timing and synchronization
- Error handling and recovery
- Security considerations (if any)
- Connection establishment and discovery flow

**Sources**: Extract from UI and summary.md + create detailed spec

**Rationale**: Critical interface, needs complete specification

**Target audience**: Firmware and software developers, network debugging

---

### Tier 5: Implementation & Validation (4 documents)

#### 17. **PCB-LAYOUT-GUIDELINES.md** ⭐ NEW
**Purpose**: PCB design rules and constraints

**Contents**:
- Stackup requirements (layer count, impedance control)
- Ground plane strategy (solid copper, stitching vias)
- RF routing rules (trace width, spacing, length matching)
- Power distribution (trace widths, decoupling placement)
- Component placement guidelines:
  - Preselector layout (switch orientation, minimizing parasitics)
  - LPF array layout (filter spacing, relay placement)
  - PA thermal management (heatsink mounting)
  - ADC/DAC analog islands
- Thermal considerations (copper pours, heatsink interfaces)
- Mechanical constraints (enclosure fit, connector placement)
- Test points and debug access
- Assembly notes (hand-wound components, hand-selected parts)

**Sources**: Extract from LPF array doc + create new content

**Rationale**: Critical for successful PCB design, currently minimal documentation

**Target audience**: PCB designers, layout review, manufacturing

---

#### 18. **CALIBRATION-PROCEDURES.md** ⭐ NEW
**Purpose**: Factory and user calibration methods

**Contents**:
- Self-calibration overview (using TX at -40 dBm)
- QSD3 duty cycle optimization (3f nulling procedure)
- Amplitude/phase matching (QSD1/QSD2/QSD3 calibration)
- Preselector characterization (frequency sweep, response mapping)
- Harmonic response measurement (actual vs theoretical)
- DPD coefficient training (LMS procedure)
- Calibration data storage format
- Calibration triggers (band change, temperature, periodic)
- User-initiated recalibration procedures
- Verification and acceptance criteria

**Sources**: Extract from RX-ARCHITECTURE.md (Section 7) + create procedures

**Rationale**: Calibration strategy exists but detailed procedures needed

**Target audience**: Test engineers, manufacturing, field service

---

#### 19. **TEST-AND-VALIDATION.md** ⭐ NEW
**Purpose**: Test procedures and acceptance criteria

**Contents**:
- Unit test procedures (per subsystem):
  - Attenuator (insertion loss, attenuation accuracy)
  - Preselector (frequency response, Q factor, tuning range)
  - QSD array (conversion gain, noise figure, harmonic rejection)
  - PA (output power, efficiency, harmonics)
  - EER supply (tracking bandwidth, ripple, efficiency)
  - LPF array (insertion loss, harmonic rejection)
- Integration test procedures:
  - RX sensitivity and dynamic range
  - TX output power and spectral purity
  - T/R switching timing and glitches
  - Calibration effectiveness
- System test procedures:
  - End-to-end TX/RX performance
  - All-mode operation (SSB, CW, AM, FM, digital)
  - Network connectivity and UI responsiveness
- Required test equipment
- Acceptance criteria and specifications
- Failure mode analysis
- Debug strategies for common issues

**Sources**: Create new content based on design requirements

**Rationale**: Essential for bringing up hardware and validating performance

**Target audience**: Test engineers, manufacturing, QA, field troubleshooting

---

#### 20. **BOM-AND-SOURCING.md** ⭐ NEW
**Purpose**: Complete bill of materials with sourcing strategy

**Contents**:
- Master BOM (all components with specifications)
- Part selection rationale (why specific parts chosen)
- Critical components:
  - ICs (STM32H753, Lattice iCE40UP3K, LM34936/LM5155, AK5578)
  - RF switches (AS183-92LF, SMP1302-079LF)
  - MOSFETs (SiR178DP, STW25N55M5, CSD18543Q3A)
  - Relays (Omron G5V-2, G6K-2F-Y)
- Hand-selected components (capacitors, tolerances)
- Hand-wound components (inductors, cores, wire specs)
- Vendor recommendations (Digikey, Mouser, LCSC)
- Alternates and substitutions (approved equivalents)
- Obsolescence risk (parts with single-source or EOL concerns)
- Cost analysis (target BOM cost, cost-reduction opportunities)
- Lead time considerations

**Sources**: Extract from all component design docs + create master list

**Rationale**: Essential for procurement, manufacturing quotes, longevity planning

**Target audience**: Purchasing, manufacturing, cost analysis, supply chain

---

### Summary: Recommended Structure

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

TOTAL: 20 documents
- ⭐ NEW: 13 documents (need creation)
- ✏️ REVISED: 5 documents (need consolidation/editing)
- ✏️ RENAME: 2 documents (minimal changes)
```

## Critical Actions Required

### 1. Resolve EER Controller IC Conflict
**Issue**: Two different controllers mentioned
- Tx EER.md: LM34936 (4-switch buck-boost)
- EER phase modulation.md: LM5155 (SEPIC)

**Action**: Determine which is actually used, update all references

### 2. Extract Preselector Detail
**Issue**: ~4000 words of component-level preselector design buried in RX-ARCHITECTURE

**Action**: Move to separate PRESELECTOR-DESIGN.md for better organization

### 3. Document Missing Subsystems
**Critical undocumented areas**:
- Power supply architecture and sequencing
- STM32-FPGA interface protocol details
- T/R switching timing and interlocks
- Network protocol specification
- Firmware architecture

### 4. Create Integration Documentation
**Missing implementation docs**:
- PCB layout guidelines
- Calibration procedures
- Test and validation
- Complete BOM with sourcing

## Prioritization Recommendation

### Phase 1: Foundation (do first)
1. PROJECT-OVERVIEW.md (onboarding)
2. SYSTEM-ARCHITECTURE.md (system context)
3. Resolve EER controller conflict
4. Consolidate TX-ARCHITECTURE.md

### Phase 2: Complete Hardware Docs (do second)
5. Extract PRESELECTOR-DESIGN.md
6. Create POWER-ARCHITECTURE.md
7. Document PA-TANK-DESIGN.md
8. Revise EER-SUPPLY-DESIGN.md
9. Document DPD-SYSTEM-DESIGN.md

### Phase 3: Enable Software Development (do third)
10. INTERFACES-AND-PROTOCOLS.md (critical for firmware/software)
11. STM32-FIRMWARE-ARCHITECTURE.md
12. PC-APPLICATION-ARCHITECTURE.md
13. NETWORK-PROTOCOL-SPEC.md

### Phase 4: Implementation Support (do fourth)
14. PCB-LAYOUT-GUIDELINES.md (for layout phase)
15. CALIBRATION-PROCEDURES.md
16. TEST-AND-VALIDATION.md
17. BOM-AND-SOURCING.md

## Benefits of This Structure

### For Human Readers
- ✅ Clear hierarchy: System → Subsystem → Component
- ✅ Find information by domain (RX, TX, firmware, etc.)
- ✅ Each doc has focused scope
- ✅ Cross-references guide to related content

### For AI Assistant (Project Knowledge)
- ✅ Reduced redundancy (information in one place)
- ✅ Clear document responsibilities (no overlap)
- ✅ Manageable document sizes (5000-8000 words typical)
- ✅ Logical grouping aids retrieval
- ✅ More docs fit in context window

### For Project Management
- ✅ Documents align with development phases
- ✅ Easy to assign ownership (RX team owns RX docs, etc.)
- ✅ Version control per subsystem
- ✅ Clear definition of "done" per area

### For Maintenance
- ✅ Updates localized (change PA → only PA-TANK-DESIGN.md affected)
- ✅ Less chance of creating inconsistencies
- ✅ Easier to keep current as design evolves