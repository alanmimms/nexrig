# Software Architecture

Host Platform: Native C++ (Windows / macOS / Linux)

UI/Scripting Engine: Lua 5.4 + ImGui

Embedded OS: Zephyr RTOS (STM32H7)

Protocol: Ethernet (UDP Streaming / TCP Control)

## 1. System Overview

The NexRig software stack is designed for performance and extensibility. It abandons the traditional "monolithic firmware" model in favor of a **Split-Architecture** approach:

1. **The Radio Hardware (Headless):** Acts as a high-performance peripheral. It handles strictly real-time safety checks, hardware actuation, and raw data streaming.
2. **The Host Application (Intelligence):** Handles all Digital Signal Processing (DSP), modulation/demodulation, user interface rendering, and configuration logic.

This separation allows the complex business logic (the "SetBox" system) and DSP algorithms to be developed and updated on the PC without flashing firmware.

## 2. Host Application Architecture

The host application is a native executable built on C++17/20. It embeds a Lua Virtual Machine to handle high-level logic.

### 2.1 The "Twin-Engine" Model

|**Engine**|**Language**|**Responsibilities**|**Libraries**|
|---|---|---|---|
|**DSP Core**|**C++**|FFT, Filtering, Mixing, Audio I/O, Network Packet Unpacking.<br><br>  <br><br>_Priority: Real-Time._|`Liquid-DSP`, `PortAudio`/`Miniaudio`, `Sockets`|
|**Logic Core**|**Lua**|UI Layout, SetBox Inheritance, Band Plans, Mode Logic, Hardware State Management.<br><br>  <br><br>_Priority: User-Interactive._|`Lua 5.4`, `Sol3` (Binding), `ImGui` (Rendering)|

### 2.2 Threading Model

The application operates on two primary thread groups to prevent UI blocking from affecting RF performance.

1. **DSP Thread (High Priority):**
    - Driven by the Audio Interface callback or Network RX interrupt.
    - Processes incoming I/Q samples from the radio.
    - Performs demodulation/filtering.
    - **Constraint:** Zero memory allocation, no thread locking, no Lua state access. Communication via lock-free ring buffers.
2. **Main Thread (UI/Logic):**
    - Runs the **ImGui** render loop (60 FPS).
    - Executes the **Lua VM**.
    - Polls ring buffers for spectrum data (FFT results) to draw.
    - Handles mouse/keyboard input and updates the SetBox state.
    - Sends asynchronous control packets (TCP) to the radio when settings change.

### 2.3 Lua Integration Strategy

Lua is not merely a scripting layer; it defines the **Radio Personality**.

- **UI Definition:** ImGui calls are wrapped in C++, allowing the UI layout to be defined in Lua scripts. This enables rapid prototyping of new control panels.
- **SetBox Model:** The hierarchical configuration (Global $\rightarrow$ Band $\rightarrow$ Mode) is implemented using Lua tables and metatables.
- **Hardware Abstraction:** C++ exposes hardware primitives to Lua (e.g., `Radio.setFrequency(Hz)`, `Radio.setRelay(Bank, State)`). Lua scripts handle the complex logic of _when_ to set those relays based on band and mode.

## 3. Embedded Firmware (STM32H7)

The firmware running on the radio hardware is minimized to ensure reliability and safety.

### 3.1 Responsibilities

- **Safety Monitor:** Thermal shutdown, Over-Current protection, Reverse Polarity detection. These loops run in hardware/ISR to guarantee sub-millisecond response times.
- **Data Pump:** Moves I/Q data from the ADC to Ethernet (RX) and Ethernet to DAC/FPGA (TX) using DMA.
- **Hardware Abstraction:** Exposes registers (Attenuator step, Relay state, VFO frequency) via a standardized TCP protocol.

### 3.2 FPGA Interaction

The STM32 controls the Lattice iCE40UP5K FPGA via SPI.

- **Configuration:** The STM32 loads the FPGA bitstream from flash at boot.
- **Runtime:** The STM32 updates the NCO Frequency Control Word (FCW) and Phase Offsets based on commands from the Host.

## 4. Network Protocol

Communication uses standard IP protocols over 100Base-T Ethernet.

### 4.1 Discovery & Control (TCP)

- **Port:** 5001
- **Format:** JSON or Binary Structs (TBD).
- **Function:** SetBox updates, telemetry reporting (voltage, temp, SWR), firmware updates.
### 4.2 I/Q Streaming (UDP)

- **Port:** 5002
- **Format:** Packed Binary.
- **RX Stream:** 6 channels $\times$ 24-bit samples (Triple QSD raw data).
- **TX Stream:** Envelope (Amplitude) + Phase data.
- **Flow Control:** The STM32 buffers samples; flow is managed by the precise sample rate of the audio clock.