# Receiver Front End Architecture

Impedance Domain: 800Ω (Preselector) / Low-Z (QSD Sampling)

Architecture: Direct Conversion (Triple-QSD)

Frequency Coverage: 1.8 – 30 MHz Continuous

Sampling Rate: 96 kHz (x6 Channels)

## 1. Overview

The NexRig receiver utilizes a high-impedance (800Ω) front end to maximize filter Q-factor and selectivity before the mixing stage. Unlike traditional superheterodyne designs, it employs a **Triple-QSD (Quadrature Sampling Detector)** architecture. By sampling the signal at three slightly offset frequencies simultaneously, the system can mathematically cancel odd-order harmonics in the digital domain, eliminating the need for steep analog roofing filters.

## 2. Input Signal Conditioning

### 2.1 Protection

To survive in a 100W transceiver environment, the RX input includes robust protection against T/R switch leakage and nearby transmitters.

- **DC Block:** Capacitor `C301` isolates DC bias from the antenna port.
    
- **Transient Suppression:** **Eaton STS321150B100AH** TVS Diode (`D301`).
    
    - **Spec:** 350W Peak Pulse Power.
        
    - **Function:** Clamps high-voltage spikes (ESD, lightning, or RF leakage) to protect the downstream attenuator switches.
        

### 2.2 Digital Attenuator

- **Topology:** Cascaded Resistive Pi-Pads switched by **Skyworks AS183-92LF**.
    
- **Steps:** 0 dB to 45 dB in 3 dB increments (3, 6, 12, 24 dB stages).
    
- **Control:** Firmware controlled via shift registers (`U401`, `U402`) to maintain optimal ADC dynamic range.
    

## 3. 800Ω Digital Tracking Preselector

The preselector acts as a continuously tunable bandpass filter. It operates at **800Ω** to reduce the capacitance required for resonance, allowing for a wider tuning range and higher Q-factor.

### 3.1 Impedance Transformation

- **Input Transformer (`T1`):** Steps up the 50Ω input to 800Ω (1:16 Impedance Ratio / 1:4 Turns Ratio).
    
- **Core:** FT50-43 or similar broadband ferrite.
    

### 3.2 Tuned Circuit

Unlike fixed band-switched filters, this preselector tracks the VFO frequency precisely.

- **Inductors:** A bank of 4 switched inductors (`L1`–`L4`) provides coarse range selection.
    
    - Values: 8.2µH, 2.7µH, 820nH, 270nH.
        
    - Selection: **AS183-92LF** RF switches select the active inductor.
        
- **Capacitors:** A **Binary Capacitor Bank** (`C0`–`C10`) provides fine tuning.
    
    - **Resolution:** 11-bit effective resolution (4pF to ~4nF).
        
    - **Values:** Binary weighted (4pF, 8pF, 16pF... 2048pF).
        
    - **Logic:** The host CPU calculates the required capacitance for the current frequency and switches the bank via the **MCP23S17** I/O Expander (`U407`).
        

### 3.3 Output Transformation

- **Transformer (`T301`):** Steps down 800Ω to low impedance for the QSDs.
    
- **Winding:** Trifilar winding ensures perfect phase/amplitude balance driving the three separate QSD channels.
    

## 4. Triple-QSD Downconversion

The core innovation of the receiver is the use of three parallel Quadrature Sampling Detectors to achieve harmonic rejection without analog wall filters.

### 4.1 The QSD Core

- **Switching Element:** **TI TS3A4751** Analog Switch.
    
    - Selected for low $R_{ON}$ (0.9Ω) and high bandwidth to minimize conversion loss.
        
- **Bias:** DC biased to $V_{CC}/2$ (+1.65V) to handle the full AC swing of the incoming RF.
    

### 4.2 Frequency Configuration

- **QSD 0:** Samples at $f - k$ (Lower side).
    
- **QSD 1:** Samples at $f + k$ (Upper side).
    
- **QSD 2:** Samples at $f$ (Center/Fundamental).
    
- **DSP Logic:** The FPGA generates these three clock domains. The host software linearly combines the I/Q streams from all three QSDs. By weighting the streams correctly, the 3rd and 5th harmonics (which alias into the passband in standard direct conversion receivers) cancel out mathematically.
    

## 5. Analog Baseband

### 5.1 Variable Gain

- **PGAs:** Six **Maxim MAX9939** Programmable Gain Amplifiers (One for each I and Q channel of the 3 QSDs).
    
- **Control:** SPI interfaced to the STM32. Allows dynamic optimization of the noise figure vs. dynamic range.
    

### 5.2 Digitization

- **ADC:** **AKM AK5578EN**.
    
    - **Channels:** 8 Analog Inputs (6 used for RX I/Q, 2 reserved/mic).
        
    - **Resolution:** 32-bit (Effective number of bits ~24).
        
    - **Sample Rate:** 96 kHz standard operation.