# NexRig: System Overview
## Open-Source 50W HF SDR Transceiver

**Document Version:** 1.0
**Date:** October 2025
**License:** MIT License (hardware, firmware, and software)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Key Innovations](#key-innovations)
3. [System Architecture](#system-architecture)
4. [Power Architecture](#power-architecture)
5. [Connectivity Architecture](#connectivity-architecture)
6. [Host PC Application](#host-pc-application)
7. [Operating Concept: SetBoxes](#operating-concept-setboxes)
8. [Target Users](#target-users)
9. [System Specifications](#system-specifications)

---

## Introduction

NexRig is an open-source software-defined radio (SDR) transceiver designed for the HF amateur radio bands (1.8-29.7 MHz). Unlike traditional commercial transceivers, NexRig combines modern computing capabilities with sophisticated RF engineering to create a platform that is both powerful and accessible to the amateur radio community.

The entire project—hardware schematics, PCB designs, firmware source code, FPGA designs, and host application software—is released under the MIT License. This permissive license encourages experimentation, modification, and contribution from the global amateur radio community.

### Design Philosophy

NexRig represents a fundamental rethinking of transceiver architecture:

**Digital-First Engineering**: Where traditional radios use analog
circuits, NexRig leverages digital control and processing. The Host
PC, STM32H753 microcontroller, and Lattice iCE40UP3K FPGA handle tasks
traditionally performed by analog components for flexibility and
precision.

**Impedance Domain Optimization**: Rather than forcing all subsystems
to operate at the traditional 50Ω impedance, NexRig uses optimized
impedance domains for each function. The receiver preselector operates
nominally at 800Ω for superior selectivity and lower component stress.
The transmitter uses a 200Ω internal domain for higher-Q filters and
reduced current.

**Zero-Voltage Switching**: All relay switching in NexRig occurs at
zero voltage—not through zero-crossing detection, but by completely
disabling power to the circuit before switching. This extends relay
life from 10⁵ operations to 10⁸+ operations and eliminates contact
arcing.

**Separation of Power and Data**: NexRig gets its power from USB-PD
input. USB Power Delivery (USB-PD) negotiation gives flexible,
high-power capability up to 100W. Data connectivity uses standard
Ethernet, keeping power and data physically and electrically separate
for reliability and flexibility.

**Software-Defined Configuration**: The SetBox paradigm replaces
traditional knobs and buttons with hierarchical configuration
inheritance. Complex operating scenarios become simple profile
switches, with all parameters managed intelligently by the software.

---

## Key Innovations

### Triple-QSD Receiver Architecture

NexRig's receiver uses three independent Quadrature Sampling Detectors
(QSDs) operating simultaneously to achieve superior harmonic rejection
without traditional image frequency problems.

**QSD0** operates at frequency offset *f-k*, providing the primary
receive signal path with excellent sensitivity.

**QSD1** operates at frequency offset *f+k*, enabling image rejection
through complex signal combining with QSD0. The complementary
frequency offsets allow software to separate desired signals from
images that would plague traditional superheterodyne architectures.

**QSD2** operates directly at frequency *f* with a specialized 33.33%
duty cycle clock (6× oversampling). This unusual duty cycle provides
greater than 40 dB rejection of third-harmonic responses, effectively
eliminating a major spurious response mechanism in direct-conversion
receivers.

The three QSD paths feed six channels (I and Q for each QSD) all
synchronized to a common clock into MAX9939 programmable gain
amplifiers and then into an AK5578 eight-channel audio codec sampling
at 96 kHz. The STM32 combines the three complex baseband signals in
software, creating a receiver with exceptional dynamic range and
spurious-free response.

### Envelope Elimination and Restoration (EER) Transmitter

Traditional linear power amplifiers maintain constant high voltage
while varying current to create amplitude modulation. This is
inherently inefficient, typically achieving only 25-50% efficiency and
requiring substantial heat dissipation.

NexRig implements EER (also known as Kahn technique), which separates
the transmitted signal into amplitude and phase components:

**Amplitude Path**: The STM32's DAC provides an envelope signal that
controls a tracking buck/boost converter. This converter (the "Veer"
supply) modulates the power amplifier's supply voltage from 0-60V,
creating amplitude modulation with minimal loss. The converter
operates at 500 kHz switching frequency with 5 kHz bandwidth,
sufficient for SSB voice and some digital modes.

**Phase Path**: The FPGA's numerically-controlled oscillator (NCO)
generates a phase-modulated square wave carrier. This drives the power
amplifier's gate through a transformer-coupled driver, creating the
phase component of the transmitted signal.

The power amplifier operates in Class-E switching mode, not as a
linear amplifier. Since it switches between off and fully-on states
(controlled by the phase path), and the supply voltage tracks the
desired envelope, the PA achieves approximately 85% efficiency.
Combined with 85% efficiency in the Veer converter, overall system
efficiency reaches 67%—far superior to the ~40% typical of linear
amplifiers.

This efficiency advantage translates directly to reduced heat
generation (25W vs 70W for 50W output), smaller heatsink requirements,
extended operating time on battery power, and improved reliability
through reduced thermal stress on components. The use of digital
predistortion in the modulation means the transmitter emits a cleaner
signal.

### Vector Impedance Measurement

Rather than using a traditional Bruene directional coupler only for
VSWR indication, NexRig employs the coupler as a vector network
analyzer component. During transmit operations, the coupler's forward
and reverse signal samples are routed through multiplexers to two of
the receiver's QSDs (QSD0 and QSD1).

The QSDs measure both the magnitude and phase of the forward and
reverse signals, providing complex impedance information: *V_forward*
= *I_fwd* + j·*Q_fwd* and *V_reverse* = *I_rev* + j·*Q_rev*.

From these complex measurements, the host application calculates:

**Complex Reflection Coefficient**: Γ = *V_reverse* / *V_forward*
(magnitude and phase)

**VSWR**: (1 + |Γ|) / (1 - |Γ|)

**Antenna Impedance**: *Z_antenna* = 50 × (1 + Γ) / (1 - Γ) = *R* + j·*X*

With knowledge of the actual antenna complex impedance, the antenna
tuner can be adjusted deterministically rather than through
trial-and-error. If the antenna presents 73 + j42Ω at 7.15 MHz, the
system calculates that a 534 pF series capacitor cancels the reactive
component, leaving 73Ω resistive. An L-network (series and shunt
reactive components) then transforms this 73Ω to the required 50Ω. The
tuner uses relay-switched binary-weighted capacitor and inductor banks
to implement the calculated L or C values precisely.

This measurement and calculation occurs in approximately 50-100ms at
low power (0.5-1W) after each band change, before full-power
transmission begins. The operator experiences instantaneous, optimal
antenna matching across all bands without manual adjustment or
iterative tuning procedures.

### SetBox Configuration Paradigm

Traditional radios force operators to adjust many independent
parameters every time they change bands, modes, or operating
situations. A contest operator switching from 20-meter CW to 40-meter
SSB might need to change: frequency, mode, antenna selection, power
level, audio equalization, AGC settings, noise reduction, filter
bandwidth, and more.

NexRig's SetBox software configuration system uses hierarchical
inheritance. Create a "Contest-Base" SetBox defining common contest
settings—perhaps reduced power for battery operation and your contest
callsign. Create "Contest-20m" and "Contest-40m" SetBoxes inheriting
from Contest-Base but adding band-specific antenna selections and
frequency memories. Create "Contest-20m-CW" and "Contest-40m-SSB"
SetBoxes that inherit from their respective band configurations and
add mode-specific parameters.

When you switch from Contest-20m-CW to Contest-40m-SSB, the system
instantly reconfigures everything—antenna, power, frequency, mode,
audio processing, waterfall colors, even active keyboard shortcuts.
Settings common to all contest operations (inherited from
Contest-Base) remain consistent, while band and mode specifics adjust
automatically.

The SetBox hierarchy makes complex operating scenarios trivial to
manage while maintaining complete control for operators who want to
adjust individual parameters.

---

## System Architecture

### High-Level Block Diagram

```
                                    ┌─────────────────────────┐
                                    │   Host PC (Electron)    │
                                    │  ┌──────────────────┐   │
                                    │  │  User Interface  │   │
                                    │  │  (React/WebAudio)│   │
                                    │  └────────┬─────────┘   │
                                    │           │             │
                                    │  ┌────────▼─────────┐   │
                                    │  │   DSP Processing │   │
                                    │  │  (Demod/Filters) │   │
                                    │  └────────┬─────────┘   │
                                    └───────────┼─────────────┘
                                                │ Ethernet
                                    ╔═══════════▼═══════════╗
                                    ║   NexRig Hardware     ║
                                    ╟───────────────────────╢
┌──────────────┐                    ║  ┌─────────────────┐ ║
│   Antenna    │◄──────────────────►║  │   STM32H753     │ ║
└──────────────┘                    ║  │  (Zephyr RTOS)  │ ║
      ▲                             ║  └─────┬───────────┘ ║
      │                             ║        │             ║
      │  TX: 50W                    ║  ┌─────▼───────────┐ ║
      │  RX: Antenna impedance      ║  │ Lattice FPGA    │ ║
      │      monitoring             ║  │  (iCE40UP3K)    │ ║
      │                             ║  │  NCO + Clocks   │ ║
      │                             ║  └─────┬───────────┘ ║
      │                             ║        │             ║
┌─────┴──────────┐                  ║  ┌─────▼───────────┐ ║
│  TX/RX Switch  │                  ║  │   AK5578 ADC    │ ║
│  (Reed Relay)  │                  ║  │  6ch × 96 kHz   │ ║
└─────┬──────────┘                  ║  └─────────────────┘ ║
      │                             ╚═══════════════════════╝
      │                                      ▲
┌─────▼──────────┐                           │ USB-PD
│  Bruene        │                    ┌──────┴────────┐
│  Directional   │                    │  Power Supply │
│  Coupler       │                    │  (100W max)   │
└────────────────┘                    └───────────────┘
      │
      ├─ Forward/Reverse samples
      │  to QSD0/QSD1 during TX
      │
      ▼
┌─────────────────────────────┐
│  RX Signal Path:            │
│  Attenuator → Preselector → │
│  QSD0/1/2 → PGA → ADC       │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│  TX Signal Path:            │
│  DSP → DAC + NCO → EER PA → │
│  LPF Array → Antenna        │
└─────────────────────────────┘
```

### Signal Flow: Receive Path

**Antenna** → **Reed Relay T/R Switch** (closed to RX in receive mode)

→ **Digital Attenuator** (0-45 dB in 3 dB steps via reed relay-switched pads)

→ **Preselector** (tunable LC tank, 800Ω nominal impedance, AS169-73LF pHEMT switches for band/component selection)

→ **50:800Ω Input Transformer** (voltage step-up, impedance matching)

→ **Triple-QSD Array** (TS3A4751 analog switches, three independent sampling paths)

→ **Six MAX9939 Programmable Gain Amplifiers** (differential I/Q for each QSD, -14 to +44 dB range, SPI-controlled)

→ **AK5578 Eight-Channel Audio Codec** (six channels used for I/Q data, 96 kHz sampling, 24-bit resolution)

→ **STM32H753 via I²S** (signal combining, decimation, preliminary DSP)

→ **Ethernet to Host PC** (96 kS/s complex baseband, ~4.6 Mbps)

→ **Host Application** (advanced DSP: demodulation, filtering, AGC, noise reduction, audio output)

### Signal Flow: Transmit Path

**Host PC Microphone Input** → **Host DSP** (SSB generation, pre-emphasis, limiting)

→ **Ethernet to STM32** (envelope and phase components, 48 kHz update rate)

→ **STM32 DAC** (envelope signal, 0-3.3V) → **Veer Buck/Boost Converter** (0-60V tracking supply)

→ **Power Amplifier Supply** (amplitude modulation)

**STM32 to FPGA** (via SPI: NCO frequency and phase control words)

→ **FPGA NCO** (32-bit phase accumulator, phase-modulated square wave)

→ **UCC27511A Gate Driver** (transformer-coupled to PA MOSFET gate)

→ **Class-E Power Amplifier** (IRFP250NPBF, 72Ω load impedance, switching mode operation)

→ **72:200Ω Transformer** (3:5 turns ratio to high-impedance domain)

→ **200Ω Low-Pass Filter Array** (5th-order elliptic, band-switched via reed relays, autotransformer matching)

→ **200:50Ω Transformer** (4:1 impedance ratio to antenna impedance)

→ **Bruene Directional Coupler** (forward/reverse sampling for impedance measurement)

→ **Reed Relay T/R Switch** → **Antenna** (50W continuous)

### Signal Flow: Impedance Measurement (During TX)

**Transmit at Low Power** (0.5-1W)

→ **Bruene Coupler Samples** (forward and reverse signal samples)

→ **Multiplexers** (switch QSD0 and QSD1 inputs from RX path to Bruene outputs)

→ **QSD0 and QSD1** (measure complex forward and reverse signals)

→ **MAX9939 PGAs** → **AK5578 ADC** → **STM32** → **Ethernet** → **Host Application**

→ **Complex Impedance Calculation** (Γ, VSWR, Z = R + jX)

→ **Antenna Tuner Control** (deterministic L/C calculation, relay commands back to STM32)

→ **Zero-Voltage Switching** (Veer to 0V, wait, switch relays, restore power)

→ **Resume Full-Power Transmission** (50W with optimal match)

---

## Power Architecture

### USB Power Delivery (USB-PD)

NexRig uses **USB Power Delivery negotiation** for its power input,
providing flexibility in power sourcing without the limitations of
traditional barrel jack connectors and fixed-voltage supplies. The
system negotiates up to **20V at 5A (100W capability)** using the
STUSB4500 autonomous USB-PD controller.

**CRITICAL**: The USB-PD connector carries **power only—no data
whatsoever**. This is a dedicated power-only USB-C port. The STUSB4500
handles PD negotiation autonomously without STM32 intervention,
ensuring power availability even during firmware updates or crashes.

A dedicated power-only connector provides several advantages:

**Safety**: Electrical isolation between power and data prevents
ground loops and protects sensitive data interfaces from power supply
noise.

**Flexibility**: The radio can be powered from USB-PD power banks,
laptop chargers, or dedicated USB-PD supplies. The negotiated 20V
provides headroom for efficient buck conversion to the various system
voltages.

**Reliability**: Separate connectors mean a power supply failure or
connector issue doesn't affect data connectivity, and vice versa.

### Power Distribution

From the negotiated 20V USB-PD input, several voltage domains are generated:

**+12V Rail** (derived from USB-PD VBUS via buck converter): Powers
analog RF circuits, relays, and high-power sections. Current capacity:
8A continuous.

**+5V Rail** (derived from 12V via buck converter): Powers STM32H753,
FPGA, digital logic, and codec. Current capacity: 2A.

**+3.3V Digital Rail** (derived from 5V via buck regulator): Powers
STM32 and other 3.3V digital logic. Current capacity: 1A.

**+3.3VA Rail** (derived from 5V via LDO): Powers low-noise analog
sections, QSD switches, and references. Current capacity: 500 mA.

**Veer Variable Rail** (0-60V derived from USB-PD VBUS via
buck/boost): Tracks transmit envelope for EER amplitude modulation.
Peak current: 8A (limited by converter and current sensing).

### Zero-Voltage Switching

All reed relay switching in NexRig occurs with **zero voltage across
the relay contacts**. This is not achieved through zero-crossing
detection of AC signals, but rather through active circuit control:

**Principle**: Before any relay switches, the circuit powering that
relay path is completely disabled. Voltage drops to zero. After
waiting for transients to settle (typically 2-5ms), the relay
actuates. The circuit is then re-enabled, ramping power back up
smoothly.

**Implementation Example (TX/RX Switch)**:
1. Detect PTT (push-to-talk) request from host
2. Command Veer buck/boost to 0V output (transmitter envelope to zero)
3. Wait 5ms for capacitor discharge and energy dissipation
4. Actuate TX/RX reed relay (no voltage, no current through contacts)
5. Wait 10ms for relay mechanical settling
6. Re-enable Veer tracking (transmitter power ramps up smoothly)

**Benefits**: Relay contact life extends from 10⁵ cycles (rated for
resistive switching) to 10⁸+ cycles (mechanical life limit). No
contact arcing means no metal transfer, no pitting, and no
degradation. Smaller, cheaper relays can be specified since
voltage/current ratings apply only to steady-state, not switching.

**Application**: This technique applies to:
- TX/RX antenna switching
- TX filter band selection (high voltage, high current during operation)
- RX preselector switching (lower voltage but critical for low noise)
- Digital attenuator pads

### Monitoring and Protection

The **STM32H753 continuously monitors** temperature and voltage
throughout the device:

**Temperature Sensors**:
- Internal STM32 die temperature (thermal shutdown if >85°C)
- PA MOSFET temperature (NTC thermistor on heatsink, shutdown if >90°C)
- Veer buck/boost inductor temperature (thermal foldback if excessive)
- Ambient temperature (for calibration compensation and fan control if present)

**Voltage Monitoring**:
- USB-PD input voltage (verify 20V negotiation success, detect supply dropout)
- +12V rail (brownout detection, log events)
- +5V rail (critical for digital logic stability)
- Veer output voltage (verify tracking accuracy, detect over/undervoltage)
- Forward PA power (via Bruene coupler during TX)
- Reflected PA power (VSWR calculation, protection)
- USB-PD power at less than 100W may still be used for receive-only
  and/or lower than full power output transmit

**Protection Actions**:
- **Thermal Shutdown**: Veer to 0V, disable PA, notify host, wait for cooldown
- **Overvoltage**: Disable affected rail, safe state, log event
- **High VSWR** (>3:1): Reduce power to 10W, notify host, allow operator override
- **Supply Dropout**: Safe state (relays to RX, disable TX), retain
  calibration data, notify host when restored

All monitoring data is available to the host application via Ethernet
for display, logging, and advanced diagnostics.

---

## Connectivity Architecture

### Ethernet: The Sole Data Path

NexRig uses **standard Ethernet** for all communication between
hardware and host PC. There is **no USB data connection**—the STM32's
USB peripheral is not used for data transfer.

**Physical Connection**: Standard RJ45 Ethernet jack on the NexRig
hardware. Standard Ethernet cable to host PC (crossover not required;
modern NICs auto-negotiate MDIX).

**Network Configuration**: The STM32 acts as an Ethernet device with a
static IP address (e.g., 192.168.7.2). The host PC configures its
Ethernet interface in the same subnet (e.g., 192.168.7.1). No DHCP
server required.

**Protocol Stack**: The STM32 runs a lightweight TCP/IP stack (likely
lwIP under Zephyr RTOS) providing:
- **TCP sockets** for reliable command/control messages
- **UDP sockets** for low-latency, high-throughput I/Q streaming
- **JSON or CBOR** message format for control/status
- **Binary framing** for I/Q data

### Data Streams

**Receive I/Q Data** (STM32 → Host):
- Six channels (I and Q for QSD0, QSD1, QSD2)
- 96 kHz sample rate per channel (after decimation from 96 kHz AK5578)
- 24-bit samples (3 bytes per sample)
- Total data rate: 6 channels × 96,000 samples/sec × 3 bytes = ~1.7 MB/s (13.8 Mbps)
- UDP transport for minimal latency

**Transmit Audio** (Host → STM32):
- Envelope amplitude samples (12-bit resolution, 48 kHz rate)
- Phase samples (16-bit resolution, 48 kHz rate)
- Total data rate: (12 + 16) bits × 48,000 samples/sec = ~168 kB/s (1.3 Mbps)
- TCP or UDP depending on latency requirements

**Control/Status Messages** (Bidirectional):
- Relay switching commands (band, attenuator, T/R)
- PGA gain adjustments
- FPGA frequency/phase settings
- Temperature/voltage telemetry
- Calibration data
- TCP transport for reliability
- Low bandwidth (~100 kB/s peak)

Total bandwidth: ~15 Mbps well within 100 Mbps Ethernet capability
(Fast Ethernet), leaving substantial headroom.

### Why Ethernet?

**Ubiquity**: Every laptop and desktop has Ethernet, either built-in
or via inexpensive USB-Ethernet adapters. No custom drivers required.

**Deterministic Performance**: Ethernet provides consistent,
predictable latency and bandwidth. No competition with other USB
devices for bus time.

**Isolation**: Electrical isolation (via magnetics in the Ethernet
PHY) prevents ground loops and protects both host and hardware from
fault conditions.

**Distance**: Standard Ethernet cables run 100 meters without issues.
Radio equipment can be positioned remotely from the operating PC--even
over an Internet connection.

**Simplicity**: Standard TCP/IP networking—no custom USB drivers, no
operating system dependencies, no certification requirements.

---

## Host PC Application

### Electron-Based Native Application

The NexRig user interface is a **native desktop application** built
using the Electron framework. Electron allows writing cross-platform
applications using web technologies (HTML, CSS, JavaScript) while
providing access to native operating system capabilities.

**NOT a browser application**: Although Electron internally uses
Chromium for rendering, the NexRig application is a standalone
executable that installs like any native application. There are no
browser security restrictions, no certificate warnings, no web server
required.

**Cross-Platform**: A single codebase produces native applications for:
- Windows (10/11)
- macOS (11.0+)
- Linux (Ubuntu, Fedora, Arch, etc.)

The application is packaged using electron-builder, creating
platform-specific installers (`.exe`, `.dmg`, `.AppImage`, `.deb`)
with appropriate signing and notarization.

### Application Architecture

**Electron Main Process** (Node.js environment):
- Manages application lifecycle (startup, shutdown, updates)
- Creates and controls application window
- Handles Ethernet socket connections (TCP/UDP)
- Interfaces with native OS features (file system, audio devices)
- Manages SetBox storage (JSON files on disk)

**Electron Renderer Process** (Chromium environment):
- React-based user interface components
- DSP processing using Web Audio API and JavaScript
- Waterfall display using Canvas2D or WebGL
- Real-time visualizations (S-meter, spectrum, constellation)

**Inter-Process Communication (IPC)**: The Main and Renderer processes
communicate via Electron's IPC mechanism. I/Q data flows: Ethernet →
Main Process → IPC → Renderer Process → Web Audio API → Host audio
output.

### DSP Responsibilities

The host application performs **computationally intensive DSP**
unsuitable for real-time embedded processing:

**Triple-QSD Combining**: The three complex baseband signals (from
QSD0, QSD1, QSD2) are combined with calibrated weights to maximize
signal and reject images/harmonics.

**Demodulation**: SSB, CW, AM, FM, and digital mode (PSK, FT8, RTTY)
demodulation algorithms implemented in JavaScript or WebAssembly.

**Filtering**: User-adjustable passband filters, notch filters, and
noise reduction filters applied in the frequency domain (FFT-based).

**AGC (Automatic Gain Control)**: Adaptive gain control with
configurable attack/release times to maintain consistent audio levels.

**Audio Processing**: Equalization, compression, and limiting for
transmit audio. De-emphasis and bass/treble controls for receive
audio.

**Visualization**: Real-time FFT for waterfall and spectrum displays,
constellation diagrams for digital modes, waveform display.

### User Interface Highlights

**Waterfall Display**: Primary tuning interface. Mouse wheel scrolling
tunes frequency. Click-and-drag selects signals. Zoom controls adjust
span.

**SetBox Selector**: Dropdown or tree view showing available
configurations. One-click switching between operating scenarios.

**Control Panel**: Consolidated access to frequency, mode, power,
antenna selection, audio controls, and advanced settings.

**Status Indicators**: S-meter, VSWR, temperature, power output,
voltage rails—all updated in real-time.

**Digital Mode Integration**: Built-in decoders for popular digital
modes with automatic frequency tracking and logging.

---

## Operating Concept: SetBoxes

### The Problem with Traditional Radios

A typical contest operator switching from 20-meter CW to 40-meter SSB
must manually adjust:
- Frequency (VFO)
- Mode (CW → SSB)
- Antenna selection (20m beam → 40m dipole)
- Power level (perhaps different per band)
- Audio equalization (CW sidetone → SSB mic)
- Filter bandwidth (CW narrow → SSB wide)
- AGC settings (CW fast → SSB slow)
- Waterfall span and color scheme
- Keyboard shortcuts (CW keyer → SSB processing)

Traditional radios force operators to remember and execute this
sequence every time they change bands or modes. Memory channels help
with frequency but leave all other settings independent.

### The SetBox Solution

A **SetBox** is a named configuration containing values for every
adjustable parameter in the system. SetBoxes form **inheritance
hierarchies**, where child SetBoxes inherit parameter values from
parents and override only what changes.

**Example Hierarchy**:

```
Global-Defaults
    ├─ Contest-Base (inherits from Global-Defaults)
    │   ├─ Contest-20m (inherits from Contest-Base)
    │   │   ├─ Contest-20m-CW (inherits from Contest-20m)
    │   │   └─ Contest-20m-SSB (inherits from Contest-20m)
    │   └─ Contest-40m (inherits from Contest-Base)
    │       ├─ Contest-40m-CW (inherits from Contest-40m)
    │       └─ Contest-40m-SSB (inherits from Contest-40m)
    └─ Ragchew-Base (inherits from Global-Defaults)
        ├─ Ragchew-20m-SSB
        └─ Ragchew-40m-SSB
```

**Global-Defaults** might define:
- Default power: 50W
- Default AGC: Medium
- Default antenna: Auto-select by band

**Contest-Base** inherits everything from Global-Defaults but overrides:
- Power: 40W (battery conservation)
- Callsign: W1ABC/M (mobile operation)
- Audio compression: Enabled

**Contest-20m** inherits from Contest-Base and overrides:
- Frequency: 14.000 MHz starting point
- Antenna: Force 20m beam selection

**Contest-20m-CW** inherits from Contest-20m and overrides:
- Mode: CW
- Filter bandwidth: 500 Hz
- Sidetone frequency: 600 Hz
- AGC: Fast
- Keyboard shortcuts: CW-specific

When the operator switches to Contest-20m-CW, the system applies:
- Power: 40W (from Contest-Base)
- Callsign: W1ABC/M (from Contest-Base)
- Audio compression: Enabled (from Contest-Base)
- Frequency: 14.000 MHz (from Contest-20m)
- Antenna: 20m beam (from Contest-20m)
- Mode: CW (from Contest-20m-CW)
- Filter: 500 Hz (from Contest-20m-CW)
- Sidetone: 600 Hz (from Contest-20m-CW)
- AGC: Fast (from Contest-20m-CW)

Switching to Contest-40m-SSB instantly reconfigures to:
- Power: 40W (from Contest-Base, unchanged)
- Callsign: W1ABC/M (from Contest-Base, unchanged)
- Frequency: 7.200 MHz (from Contest-40m)
- Antenna: 40m dipole (from Contest-40m)
- Mode: SSB (from Contest-40m-SSB)
- Filter: 2.4 kHz (from Contest-40m-SSB)
- Mic EQ: Voice-optimized (from Contest-40m-SSB)
- AGC: Slow (from Contest-40m-SSB)

### Benefits

**Consistency**: Settings common to all contest operations (power,
callsign) are defined once in Contest-Base and automatically apply to
all child SetBoxes.

**Flexibility**: Any parameter can be overridden at any level of the
hierarchy. Want more power on 40m SSB for DX? Override in
Contest-40m-SSB without affecting other configurations.

**Simplicity**: Switching between complex operating scenarios becomes
a single SetBox selection. The system handles all parameter changes
atomically.

**Transparency**: The user interface shows exactly where each active
parameter value comes from in the inheritance chain. Adjusting a
parameter prompts: "Save to current SetBox?" or "Save as new child
SetBox?"

**Experimentation**: Trying new settings is safe. Create a new child
SetBox, experiment, and discard if unsuccessful. The parent SetBox
remains unchanged.

---

## Target Users

### Amateur Radio Operators

**Experienced Operators**: Hams who understand radio theory and want
maximum control over their equipment. NexRig provides direct access to
every parameter while simplifying complex operations through SetBoxes.

**Digital Mode Enthusiasts**: Built-in decoders and optimized
configurations for PSK31, FT8, RTTY, and other digital modes. The host
PC's computational power enables sophisticated decoding and automatic
frequency tracking.

**Contesters**: Rapid band/mode switching via SetBoxes. Multiple
receiver windows. Logging integration. Voice memories and CW keying.

**Experimenters**: Open-source design invites modification. Add new
digital modes, implement advanced DSP algorithms, design custom UI
panels—all without hardware changes.

### Developers and Researchers

**RF Engineers**: Complete schematics and design documentation enable
detailed analysis and optimization. The modular architecture supports
subsystem replacement without redesigning the entire radio.

**Software Developers**: Electron/React UI is accessible to web
developers. Contribution doesn't require embedded systems expertise.
The API between hardware and software is well-documented and stable.

**Educators**: NexRig serves as a teaching platform for SDR concepts,
DSP algorithms, RF engineering, and software architecture. Students
can experiment with real hardware while understanding complete signal
flow.

### Open-Source Community

Anyone interested in advancing amateur radio technology. Contributions
range from documentation improvements to hardware revisions to
software enhancements. The MIT License ensures that improvements
benefit the entire community.

---

## System Specifications

### Frequency Coverage

**Receive**: 1.0 - 30 MHz continuous (general coverage)
**Transmit**: Amateur bands only (software-enforced):
- 160m: 1.8 - 2.0 MHz
- 80m: 3.5 - 4.0 MHz
- 60m: 5.3 - 5.4 MHz (channels)
- 40m: 7.0 - 7.3 MHz
- 30m: 10.1 - 10.15 MHz
- 20m: 14.0 - 14.35 MHz
- 17m: 18.068 - 18.168 MHz
- 15m: 21.0 - 21.45 MHz
- 12m: 24.89 - 24.99 MHz
- 10m: 28.0 - 29.7 MHz

### Power Specifications

**Transmit Power**: 50W continuous, all modes
**Power Input**: 20V @ 5A via USB-PD (100W capability)
**Typical Power Consumption**:
- Receive only: 15W
- Transmit @ 50W: 75W (67% efficiency)
- Standby: 8W

### Receiver Performance

**Architecture**: Triple-QSD direct conversion with complementary harmonic rejection
**Preselection**: Variable LC tuning, 800Ω nominal impedance
**Sampling Rate**: 96 kHz (six channels: I/Q for each of three QSDs)
**ADC Resolution**: 24-bit (AK5578)
**Dynamic Range**: >100 dB (achievable with triple-QSD combining and gain ranging)
**MDS (Minimum Detectable Signal)**: Better than -130 dBm (estimated, 500 Hz BW, 10 dB SNR)

### Transmitter Performance

**Architecture**: EER (Envelope Elimination and Restoration) with Class-E PA
**Efficiency**: ~67% overall (85% Veer × 85% PA)
**Spurious Emissions**: <-40 dBc (harmonics and non-harmonic)
**IMD (Intermodulation Distortion)**: <-30 dBc (two-tone test, 50W PEP)
**Frequency Stability**: Crystal-controlled (40 MHz TCXO reference, ~±1 ppm)

### Impedance Domains

**Receiver Preselector**: 800Ω nominal (optimized for selectivity and reduced component stress)
**Transmitter Internal**: 200Ω (LPF array, high-Q filters)
**Antenna Interface**: 50Ω (standard)
**PA Load**: 72Ω (optimized for 60V supply, 50W output)

### Physical Interfaces

**Power**: USB-C connector, USB-PD negotiation, 20V @ 5A (power only, no data)
**Data**: RJ45 Ethernet, 100 Mbps (Fast Ethernet)
**Antenna**: SO-239 or Type-N connector (TBD)
**Auxiliary**: 3.5mm jack for external PTT, CW key, or footswitch

### Control and Monitoring

**Microcontroller**: STM32H753, 480 MHz Cortex-M7, 1MB flash, 1MB RAM, Zephyr RTOS
**FPGA**: Lattice iCE40UP3K, 40 MHz TCXO reference, NCO and clock generation
**Temperature Monitoring**: STM32 internal, PA heatsink, Veer inductor, ambient
**Voltage Monitoring**: USB-PD input, +12V, +5V, Veer output
**Protection**: Thermal shutdown, overvoltage protection, high-VSWR power reduction

### Host Software

**Platform**: Electron (native desktop application)
**Operating Systems**: Windows 10/11, macOS 11+, Linux (Ubuntu/Fedora/Arch)
**UI Framework**: React with modern JavaScript (ES2022+)
**DSP**: Web Audio API, FFT-based processing, JavaScript/WebAssembly
**Configuration**: JSON-based SetBox storage with hierarchical inheritance

---

## Conclusion

NexRig represents a modern approach to amateur radio transceiver
design, combining sophisticated RF engineering with flexible software
control. The triple-QSD receiver architecture, EER transmitter, vector
impedance measurement, and SetBox configuration system provide
capabilities typically found only in commercial equipment costing
thousands of dollars.

The open-source nature of the project—hardware, firmware, and
software—encourages experimentation, learning, and community
contribution. Whether you're an experienced RF engineer, a software
developer, or an amateur radio operator seeking a powerful and
flexible transceiver, NexRig offers a platform for exploration and
innovation.

The following documents provide detailed technical information:

- **RX-ARCHITECTURE.md**: Complete receiver design (preselector, QSDs, PGAs, ADC, AGC)
- **TX-ARCHITECTURE.md**: Complete transmitter design (EER PA, Veer supply, LPF array)
- **SYSTEM-INTEGRATION.md**: Power system, connectivity, protocols, firmware/FPGA design, calibration
- **CONSTRUCTION-TESTING.md**: Assembly procedures, testing, calibration, validation

Welcome to the NexRig project. We look forward to your contributions and innovations.

---

**Document Revision**: 1.0
**Last Updated**: October 2025
**Project Repository**: https://github.com/alanmimms/nexrig.git
**License**: MIT License - See LICENSE.md
