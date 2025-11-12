# NexRig: System Overview
## Open-Source 50W HF SDR Transceiver

**Document Version:** 2.1
**Date:** January 2025
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
reduced current, with the H-bridge power amplifier operating at 36Ω
differential for optimal switching performance.

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

### Triple-QSD Direct Conversion Receiver

Traditional direct conversion receivers suffer from severe harmonic
response problems. A signal at 21 MHz appears identical to its 3rd
harmonic at 7 MHz (since 7 MHz × 3 = 21 MHz), making harmonic
rejection nearly impossible without very sharp analog filters.

NexRig solves this with a **triple-QSD architecture**. Three
independent quadrature sampling detectors sample the RF signal at
slightly different frequencies:
- **QSD0**: Samples at frequency f - k (e.g., 13.995 MHz for 14.000 MHz desired)
- **QSD1**: Samples at frequency f + k (e.g., 14.005 MHz for 14.000 MHz desired)
- **QSD2**: Samples at frequency f (e.g., 14.000 MHz exactly)

The host PC's native DSP combines these three complex baseband signals
using calibrated weights. The desired signal at frequency f sums
constructively across all three QSDs. The 3rd harmonic (3f) appears at
different baseband frequencies in each QSD and cancels when properly
weighted. The 5th harmonic similarly cancels.

This mathematical approach achieves **>40 dB harmonic rejection**
without requiring sharp analog filters, which are difficult to
implement and maintain across the entire HF spectrum.

### 800Ω Preselector Architecture

Amateur radio has traditionally operated at 50Ω system impedance, but
NexRig's preselector uses **800Ω nominal impedance** for several
compelling advantages:

**Higher Inductance**: At 800Ω, the required inductance for tuned
circuits is 16× larger than at 50Ω. Higher inductance values are
easier to wind with better Q factors (lower loss, sharper selectivity).

**Lower Capacitance**: Complementarily, the required capacitance is
1/16 that of a 50Ω design. Smaller capacitors cost less, have better
voltage handling, and introduce less loss.

**Reduced Current**: At the same power level, 800Ω impedance reduces
current by 4× compared to 50Ω. Lower current reduces resistive losses
in switches and relay contacts, and enables use of smaller, less
expensive components.

**Better Signal Handling**: Higher impedance with lower current means
components experience less thermal stress and switching transients,
improving reliability and extending component life.

The antenna connection remains 50Ω standard. Transformers at the input
and output of the preselector provide impedance matching while
maintaining excellent signal fidelity.

### EER Transmitter Architecture

The transmitter uses **Envelope Elimination and Restoration (EER)**
architecture, also known as Kahn technique. This approach separates
the RF signal into two components:

**Envelope (Amplitude)**: A DC voltage from 0-60V that modulates the
power amplifier's supply voltage, controlling output power
instantaneously.

**Phase (Constant Amplitude)**: A fixed-amplitude RF signal at the
desired frequency that drives the power amplifier switching.

The power amplifier uses a **4-FET quadrature-driven H-bridge** 
topology operating in Class-D switching mode. This architecture 
provides several critical advantages over traditional single-FET 
designs:

**Even Harmonic Cancellation**: The differential, push-pull nature of 
the H-bridge naturally cancels all even-order harmonics (2nd, 4th, 
6th, etc.), dramatically reducing the burden on the low-pass filter 
array. Only odd harmonics require filtering.

**Excellent Linearity**: The H-bridge output voltage is a highly 
linear function of the EER supply voltage, simplifying digital 
pre-distortion requirements.

**Distributed Thermal Stress**: Four smaller MOSFETs distribute heat 
generation, improving thermal management compared to a single large 
device.

**DC Isolation**: The H-bridge drives a transformer, providing 
galvanic isolation and eliminating DC-blocking capacitors.

The FPGA generates four precisely-timed gate drive signals (I+, I-, 
Q+, Q-) that control the H-bridge switching pattern. The 36Ω 
differential output is transformed to 200Ω single-ended for the 
low-pass filter array.

The **Veer buck/boost converter** generates the envelope voltage with
48 kHz bandwidth—fast enough to accurately reproduce SSB voice while
maintaining excellent efficiency (~85%). Combined efficiencies: 85%
(Veer) × 87% (H-bridge PA) ≈ **74% overall** at 50W output—
significantly better than traditional linear amplifiers at 40-50%.

Digital pre-distortion in the host PC compensates for nonlinearities
in the Veer converter and PA, achieving excellent spectral purity
without requiring linear amplification.

### Vector Impedance Measurement

Instead of traditional VSWR meters, NexRig measures **vector antenna
impedance** directly using its receiver chain. During transmit, the
Bruene directional coupler samples forward and reflected signals. The
receiver's triple-QSD architecture digitizes both signals with
phase information preserved.

The host application's native DSP calculates the complex reflection
coefficient (Γ) and derives the antenna impedance:

```
Z_antenna = 50Ω × (1 + Γ) / (1 - Γ)
```

This provides complete Smith chart information: resistance,
reactance, VSWR, return loss, and mismatch loss—far more information
than a simple VSWR meter.

More importantly, the **antenna tuner** can calculate the exact L and
C values needed for a perfect match. Rather than iterative "tune and
measure" cycles, NexRig measures impedance once at low power,
calculates optimal tuner settings mathematically, and switches to
those settings instantly. The tuner uses relay-switched
binary-weighted capacitor and inductor banks to implement the
calculated L or C values precisely.

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
frequencies.

For each band, create mode-specific SetBoxes: "Contest-20m-CW"
inherits from Contest-20m and adds CW-specific parameters (narrow
filter, fast AGC, keyer speed). "Contest-20m-SSB" inherits from
Contest-20m but configures wider filters, voice processing, and slower
AGC.

Switching between SetBoxes instantly reconfigures the entire radio
with all appropriate settings. The operator focuses on operating
rather than configuration management.

### Example Hierarchy

```
Contest-Base
├── Contest-20m
│   ├── Contest-20m-CW
│   └── Contest-20m-SSB
└── Contest-40m
    ├── Contest-40m-CW
    └── Contest-40m-SSB
```

Operating on Contest-20m-CW configures the radio with:
- Power: 40W (from Contest-Base)
- Callsign: W1ABC/M (from Contest-Base)
- Frequency: 14.050 MHz (from Contest-20m)
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

## System Architecture

### Receiver Signal Path

**Antenna (50Ω)** → **50:800Ω Input Transformer** (voltage step-up, 
impedance matching)

→ **Digitally-Tunable Preselector** (tunable LC tank, 800Ω nominal 
impedance, AS169-73LF pHEMT switches for band/component selection)

→ **800:50Ω Output Transformer** (impedance matching back to 50Ω)

→ **T/R Relay** (reed relay, zero-voltage switching)

→ **50:800Ω Preselector Output Transformer** (return to high impedance 
for QSD input)

→ **Triple-QSD Array** (TS3A4751 analog switches, three independent 
sampling paths)

→ **Six MAX9939 Programmable Gain Amplifiers** (differential I/Q for 
each QSD, -14 to +44 dB range, SPI-controlled)

→ **AK5578 Eight-Channel Audio Codec** (six channels used for I/Q 
data, 96 kHz sampling, 24-bit resolution)

→ **STM32H753 via I²S** (signal combining, decimation, preliminary DSP)

→ **Ethernet to Host PC** (96 kS/s complex baseband, ~4.6 Mbps)

→ **Host Application Native DSP** (C++ implementation: demodulation, 
filtering, AGC, noise reduction, audio output)

### Transmitter Signal Path

**Host PC Microphone Input** → **Host Native DSP** (C++ implementation: 
SSB generation, pre-emphasis, limiting)

→ **Ethernet to STM32** (envelope and phase components, 48 kHz update 
rate)

→ **STM32 DAC** (envelope to Veer controller)

→ **Veer Buck/Boost Converter** (0-60V envelope modulation)

→ **STM32 to FPGA** (phase data via SPI/I2S)

→ **FPGA NCO** (upconverts phase signal to RF, generates quadrature 
signals)

→ **Quadrature Gate Drivers** (two half-bridge drivers for four 
MOSFETs)

→ **4-FET H-Bridge Power Amplifier** (Class-D switching, 36Ω 
differential output)

→ **5.5:1 Step-Up Transformer** (36Ω differential to 200Ω single-ended)

→ **PA Tank Circuits** (resonant filtering at 200Ω)

→ **Low-Pass Filter Array** (8 filters, 200Ω, relay-switched)

→ **Bruene Directional Coupler** (forward/reflected power sampling)

→ **200:50Ω Output Transformer** (impedance matching to antenna)

→ **T/R Relay** (reed relay, zero-voltage switching)

→ **Antenna** (50Ω standard, 50W output)

### Block Diagram

```
┌─────────────┐         ┌──────────────┐
│   Host PC   │◄───────►│  STM32H753   │
│  Electron   │ Ethernet│   Zephyr     │
│ Native DSP  │         │   RTOS       │
└─────────────┘         └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │ Lattice FPGA │
                        │  iCE40UP3K   │
                        └──────┬───────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼────┐           ┌─────▼─────┐        ┌──────▼─────┐
   │Triple-  │           │ 4-FET     │        │   Veer     │
   │QSD RX   │           │ H-Bridge  │        │Buck/Boost  │
   │         │           │  Class-D  │        │  0-60V     │
   └────┬────┘           │    PA     │        └──────┬─────┘
        │                └─────┬─────┘               │
        │                      │                     │
   ┌────▼────┐           ┌─────▼─────┐              │
   │Preselector          │LPF Array  │              │
   │  800Ω   │           │  200Ω     │              │
   └────┬────┘           └─────┬─────┘              │
        │                      │                     │
        └──────────┬───────────┴─────────────────────┘
                   │
              ┌────▼────┐
              │ Antenna │
              │  50Ω    │
              └─────────┘
```

---

## Power Architecture

### USB Power Delivery (USB-PD)

NexRig uses **USB-PD negotiation** for all operating power. A USB-C
connector on the rear panel accepts 20V @ 5A (100W maximum) from any
USB-PD compliant power supply or power bank.

**Voltage Profiles**:
- **Receive-Only**: 12V minimum (15-20W typical consumption)
- **Full Transmit**: 20V preferred for 50W output (75W total
  consumption)
- **Reduced Power**: Lower voltages supported with automatic power
  limiting

The STM32 firmware performs USB-PD negotiation at startup,
automatically selecting the highest voltage available. The system
operates at reduced capability if only 12V or 15V is available,
gracefully degrading to receive-only operation if power delivery is
insufficient for transmit.

### Internal Power Distribution

From the USB-PD input, internal regulators derive:
- **+12V rail**: PA bias, relay coils, preselector switches
- **+5V rail**: Digital logic, STM32, FPGA, PGAs, ADC
- **+3.3V rail**: STM32 core, FPGA core, sensitive analog
- **Veer output**: 0-60V variable (EER envelope modulation)

All supplies include comprehensive monitoring with automatic shutdown
on overvoltage, undervoltage, or overtemperature conditions.

### Zero-Voltage Relay Switching

**All relay operations occur at zero voltage**. The STM32 firmware
ensures complete power removal from the switched circuit *before*
changing relay states. This isn't zero-crossing detection—it's
deterministic software control that guarantees zero voltage.

**Example: Band Change**
1. Software disables PA and Veer outputs (force voltage to zero)
2. Wait 5ms for filter capacitors to discharge
3. Switch LPF relays to new band
4. Verify relay state via optional sense lines
5. Re-enable PA and Veer (resume transmission)

Total switching time: ~10ms, imperceptible to the operator but
extending relay life by 1000× or more.

### Thermal Management

The H-bridge architecture distributes thermal stress across four
smaller MOSFETs rather than concentrating it in a single large device.
Each MOSFET dissipates approximately 1.5-2W during 50W transmission.

Temperature monitoring occurs at multiple points:
- **STM32 internal sensor**: Monitors board ambient temperature
- **PA heatsink sensor**: Thermistor directly on heatsink
- **Veer inductor sensor**: Thermistor on buck/boost inductor
- **FPGA internal sensor**: Die temperature monitoring

If any temperature exceeds safe thresholds, the firmware:
1. Reduces transmit power progressively (10W steps)
2. Displays warning to operator
3. If temperature continues rising, forces receive-only mode
4. Logs thermal event for diagnostics

Normal operating temperatures:
- **PA heatsink**: 40-60°C at 50W continuous
- **Veer inductor**: 50-70°C under envelope modulation
- **Board ambient**: 35-45°C typical

---

## Connectivity Architecture

### Physical Interfaces

**Power Input**: USB-C connector, USB-PD negotiation only (no data)

**Data Connection**: RJ45 Ethernet jack, 100BASE-TX (Fast Ethernet)

**RF Connection**: SO-239 or Type-N connector (TBD), 50Ω impedance

**Auxiliary I/O**: 3.5mm TRS jack for PTT, CW key, or footswitch

### Network Architecture

NexRig uses standard Ethernet for all host communication. This provides
several advantages over USB:

**Simplicity**: No USB device firmware complexity. The STM32 acts as
an Ethernet endpoint using standard TCP/IP.

**Reliability**: Ethernet is highly resistant to RF interference and
ground loops. Transformer isolation in the magnetics provides galvanic
isolation.

**Flexibility**: The radio can be located remotely from the host PC
with standard Cat5e/Cat6 cable (up to 100m). Multiple radios can share
a network switch.

**Standardization**: No custom drivers required. Any OS with Ethernet
networking can communicate with NexRig.

### Protocol Stack

**Application Layer**: JSON messages over WebSocket (for control) and
raw binary (for I/Q data)

**Transport Layer**: TCP for control messages, UDP for I/Q streaming

**Network Layer**: IPv4 with static IP configuration (192.168.7.x
default) or DHCP

**Link Layer**: Ethernet 802.3, 100BASE-TX, full-duplex

The STM32 runs a lightweight TCP/IP stack (lwIP) under Zephyr RTOS,
handling all network communication with minimal overhead.

### Data Rates

**Receiver I/Q Data**: 96 kHz × 6 channels × 24 bits = 13.8 Mbps raw

After protocol overhead and compression: **~15 Mbps peak** (well within
100 Mbps Ethernet capability)

**Transmitter I/Q Data**: 48 kHz × 2 channels × 16 bits = 1.5 Mbps

**Control Messages**: <1 Mbps typical (SetBox changes, frequency
updates, status monitoring)

Total bandwidth utilization: **~20 Mbps peak**, leaving substantial
margin for reliability and future expansion.

---

## Host PC Application

### Architecture Overview

The host application is an **Electron desktop application** running on
Windows, macOS, or Linux. Unlike browser-based solutions, Electron
with native Node.js addons provides:

**Performance**: Native C++ DSP implementation achieves 10-100×
performance improvement over JavaScript, enabling sophisticated
real-time processing.

**Integration**: Direct access to OS audio APIs (WASAPI, CoreAudio,
ALSA) for low-latency microphone input and speaker output.

**Capabilities**: Native TCP/UDP sockets for efficient I/Q data
streaming, filesystem access for logging and recordings, and serial
port support for external accessories.

**UI Quality**: Modern React UI framework with hardware-accelerated
rendering, responsive design, and professional appearance.

### DSP Processing

All demodulation, filtering, and signal processing occurs in **native
C++ code** rather than JavaScript. This includes:

**Receiver DSP**:
- Triple-QSD combining with calibrated weights
- Digital downconversion and decimation
- SSB/CW/AM/FM demodulation
- Adaptive noise reduction
- Automatic gain control (AGC)
- Audio equalization and filtering
- S-meter calculation

**Transmitter DSP**:
- SSB generation (microphone input → I/Q samples)
- Speech processing and clipping
- Pre-emphasis and equalization
- Polar conversion (I/Q → envelope + phase)
- Digital pre-distortion (compensate PA nonlinearities)

**Analysis Tools**:
- FFT-based waterfall and spectrum display
- Vector impedance calculation
- Antenna tuner optimization
- Calibration and alignment

### User Interface

The React-based UI provides:

**Main Display**: Spectrum waterfall, frequency readout, S-meter,
mode/filter indicators

**VFO Control**: Click-to-tune waterfall, direct frequency entry,
memory recall, RIT/XIT

**Operating Panels**: Mode-specific controls (SSB audio, CW keyer,
digital mode decoder)

**SetBox Management**: Hierarchy browser, parameter inheritance
display, quick-switch buttons

**Settings**: Comprehensive configuration for all hardware and software
parameters

**Logging**: Integrated contest/DX logging with ADIF import/export

**Remote**: Optional web interface for headless operation or remote
access

### Configuration Storage

All configuration uses **JSON format** stored in the user's home
directory:

```
~/.nexrig/
├── setboxes/
│   ├── Contest-Base.json
│   ├── Contest-20m.json
│   ├── Contest-20m-CW.json
│   └── ...
├── calibration/
│   ├── rx-gain-cal.json
│   ├── tx-dpd-tables.json
│   └── antenna-tuner-presets.json
└── logs/
    ├── 2025-01-15-contest.adi
    └── ...
```

This file-based approach enables:
- Version control (Git) for configuration backups
- Easy sharing of SetBoxes between operators
- Simple backup and restore procedures
- No database dependencies or corruption risks

---

## Operating Concept: SetBoxes

The SetBox paradigm fundamentally changes how operators interact with
the radio. Rather than adjusting individual parameters, operators
define **complete operating contexts** that the software manages
automatically.

### Traditional Operation vs SetBoxes

**Traditional Radio** (20m → 40m SSB):
1. Change frequency knob
2. Select different antenna
3. Adjust power level
4. Change filter bandwidth
5. Adjust microphone gain
6. Set AGC speed
7. Enable speech processor
8. Configure audio EQ

**NexRig with SetBoxes**:
1. Click "Contest-40m-SSB"

The system instantly reconfigures all eight parameters (and dozens
more) according to the SetBox definition. The operator focuses on
making contacts rather than managing configuration.

### Inheritance in Practice

SetBoxes inherit parameters from parent SetBoxes. This creates a
powerful organizational structure:

**Base Level** (Global SetBox):
```json
{
  "callsign": "W1ABC",
  "power": 50,
  "audio_input": "USB Microphone",
  "audio_output": "Built-in Speakers"
}
```

**Band Level** (20m SetBox inherits from Global):
```json
{
  "parent": "Global",
  "frequency": 14.200,
  "antenna": "20m Beam"
}
```

**Mode Level** (20m-SSB inherits from 20m inherits from Global):
```json
{
  "parent": "20m",
  "mode": "USB",
  "filter_bandwidth": 2400,
  "mic_eq": "Voice Optimized",
  "agc": "Slow"
}
```

When operating on 20m-SSB, the effective configuration is:
```json
{
  "callsign": "W1ABC",           // from Global
  "power": 50,                   // from Global
  "audio_input": "USB Microphone", // from Global
  "audio_output": "Built-in Speakers", // from Global
  "frequency": 14.200,           // from 20m
  "antenna": "20m Beam",         // from 20m
  "mode": "USB",                 // from 20m-SSB
  "filter_bandwidth": 2400,      // from 20m-SSB
  "mic_eq": "Voice Optimized",   // from 20m-SSB
  "agc": "Slow"                  // from 20m-SSB
}
```

### Dynamic Override

Any parameter can be temporarily overridden without modifying the
SetBox:

1. Operator adjusts power from 50W to 30W
2. UI highlights the power control (indicates override)
3. Prompts: "Save to 20m-SSB?" or "Create new SetBox?"

This allows quick adjustments during operation while maintaining clean
configuration management. Overrides are session-only unless explicitly
saved.

### Common Use Cases

**DXpedition**: SetBoxes for each band with pile-up specific settings
(fast AGC, narrow filters, split operation enabled)

**Contesting**: Band/mode specific SetBoxes with voice memories,
auto-CQ functionality, and rapid QSY capability

**Casual Operating**: Separate SetBoxes for morning coffee (40m SSB,
low power, relaxed settings) vs evening DX (20m/15m, full power,
optimized for weak signal work)

**Portable/Field**: Battery-conservation SetBoxes with reduced power,
simplified displays, and portable antenna selections

**Digital Modes**: Dedicated SetBoxes for FT8, PSK31, RTTY, each with
appropriate power levels, audio routing, and decoder configuration

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

**Software Developers**: React UI framework and well-documented DSP
APIs make contribution accessible. Native DSP development uses
standard C++ toolchains. Contribution doesn't require embedded systems
expertise. The API between hardware and software is well-documented
and stable.

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
- Transmit @ 50W: 75W (74% efficiency)
- Standby: 8W

### Receiver Performance

**Architecture**: Triple-QSD direct conversion with complementary harmonic rejection
**Preselection**: Variable LC tuning, 800Ω nominal impedance
**Sampling Rate**: 96 kHz (six channels: I/Q for each of three QSDs)
**ADC Resolution**: 24-bit (AK5578)
**Dynamic Range**: >100 dB (achievable with triple-QSD combining and gain ranging)
**MDS (Minimum Detectable Signal)**: Better than -130 dBm (estimated, 500 Hz BW, 10 dB SNR)

### Transmitter Performance

**Architecture**: EER (Envelope Elimination and Restoration) with 4-FET Class-D H-Bridge PA
**PA Topology**: Quadrature-driven full-bridge, differential 36Ω output
**Efficiency**: ~74% overall (85% Veer × 87% H-bridge PA)
**Spurious Emissions**: <-40 dBc (harmonics and non-harmonic)
**IMD (Intermodulation Distortion)**: <-30 dBc (two-tone test, 50W PEP)
**Harmonic Suppression**: Even harmonics >60 dBc (inherent H-bridge cancellation)
**Frequency Stability**: Crystal-controlled (40 MHz TCXO reference, ~±1 ppm)

### Impedance Domains

**Receiver Preselector**: 800Ω nominal (optimized for selectivity and reduced component stress)
**Transmitter Internal**: 200Ω (LPF array, high-Q filters)
**H-Bridge Output**: 36Ω differential (optimized for 60V supply, Class-D switching)
**Antenna Interface**: 50Ω (standard)

### Physical Interfaces

**Power**: USB-C connector, USB-PD negotiation, 20V @ 5A (power only, no data)
**Data**: RJ45 Ethernet, 100 Mbps (Fast Ethernet)
**Antenna**: SO-239 or Type-N connector (TBD)
**Auxiliary**: 3.5mm jack for external PTT, CW key, or footswitch

### Control and Monitoring

**Microcontroller**: STM32H753, 480 MHz Cortex-M7, 1MB flash, 1MB RAM, Zephyr RTOS
**FPGA**: Lattice iCE40UP3K, 40 MHz TCXO reference, NCO and quadrature phase generation
**Temperature Monitoring**: STM32 internal, PA heatsink, Veer inductor, ambient
**Voltage Monitoring**: USB-PD input, +12V, +5V, Veer output
**Protection**: Thermal shutdown, overvoltage protection, high-VSWR power reduction

### Host Software

**Platform**: Electron (native desktop application)
**Operating Systems**: Windows 10/11, macOS 11+, Linux (Ubuntu/Fedora/Arch)
**UI Framework**: React with modern JavaScript (ES2022+)
**DSP**: Native C++ libraries (FFTW, liquid-dsp, or custom)
**Audio**: Native OS audio APIs (WASAPI/CoreAudio/ALSA)
**Configuration**: JSON-based SetBox storage with hierarchical inheritance

---

## Conclusion

NexRig represents a modern approach to amateur radio transceiver
design, combining sophisticated RF engineering with flexible software
control.

The triple-QSD receiver architecture, 4-FET H-bridge EER transmitter,
vector impedance measurement, and SetBox configuration system provide
capabilities typically found only in commercial equipment costing
thousands of dollars.

The H-bridge power amplifier architecture delivers superior performance
over traditional single-FET designs through inherent even harmonic
cancellation, distributed thermal stress, excellent linearity, and
galvanic isolation—all while maintaining high efficiency and enabling
sophisticated digital control.

The open-source nature of the project—hardware, firmware, and
software—encourages experimentation, learning, and community
contribution. Whether you're an experienced RF engineer, a software
developer, or an amateur radio operator seeking a powerful and
flexible transceiver, NexRig offers a platform for exploration and
innovation.

The following documents provide detailed technical information:

- **RX-ARCHITECTURE.md**: Complete receiver design (preselector, QSDs, PGAs, ADC, AGC)
- **TX-ARCHITECTURE-updated.md**: Complete transmitter design (4-FET H-bridge PA, EER, Veer supply, LPF array)
- **TX-H-BRIDGE.md**: Detailed H-bridge specifications and component selection
- **LPF_Array_Design_200ohm.md**: Low-pass filter array design
- **SYSTEM-INTEGRATION.md**: Power system, connectivity, protocols, firmware/FPGA design, calibration
- **CONSTRUCTION-TESTING.md**: Assembly procedures, testing, calibration, validation

Welcome to the NexRig project. We look forward to your contributions and innovations.

---

**Document Revision**: 2.1
**Last Updated**: January 2025
**Project Repository**: https://github.com/alanmimms/nexrig.git
**License**: MIT License - See LICENSE.md
