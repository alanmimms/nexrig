# Power System Architecture

Primary Input: External DC (13.8V Nominal)

Portable Input: USB-PD (20V @ 5A)

EER Output: 0V – 80V Modulated ("Veer" Rail)

Auxiliary Rails: +6V, +5V, +3.3V, +1.2V

## 1. Overview

The NexRig utilizes a **Prioritized Dual-Source** power architecture to balance portability with high-power performance.

1. **High Power Mode (100W):** When an external DC source (12V–15V) is connected, the system prioritizes this input to drive the full 100W RF output.
    
2. **Portable Mode (50W+):** When running on USB-PD only, the system limits RF output to stay within the 100W source limit of standard USB-C chargers.
    

## 2. Power Path Architecture

The system employs an **LTC4417 Prioritized PowerPath Controller** to arbitrate between the two power sources. Unlike simple diode-ORing, this controller selects the source based on _priority_, not voltage.

|**Priority**|**Source**|**Voltage Range**|**Behavior**|
|---|---|---|---|
|**1 (High)**|**External DC**|11.0V – 16.0V|If valid, system disconnects USB-PD and runs purely from External DC. Enables full 100W transmit power.|
|**2 (Low)**|**USB-PD**|19.0V – 21.0V|Selected only if External DC is absent or invalid (<11V). Firmware restricts PA output to safe limits (~50-70W carrier).|

- **Input Connector:** Anderson Powerpole (Standard) or XT60 (Compact variant).
    
- **Switching:** Seamless switchover allows connecting external power during operation without rebooting.
    

## 3. The "Veer" EER Supply

The Veer supply acts as a high-power Amplitude Modulator (Buck-Boost), converting the selected input rail (13.8V or 20V) into the dynamic drain voltage needed for the PA.

### 3.1 Specifications

- **Controller:** **Analog Devices LTC3779** (Synchronous 4-Switch Buck-Boost).
    
- **Input Voltage:** 11V – 22V (Covers both External DC and USB-PD ranges).
    
- **Output Voltage:** 0V – 80V (Envelope Tracking).
    
- **Power Capacity:** 150W Peak (supports 100W RF Output + losses).
    

### 3.2 High-Voltage Components

- **Power MOSFETs:** **Infineon BSC360N15NS3 G**
    
    - **Rating:** 150V $V_{DS}$ | 100A $I_D$.
        
    - **Safety:** The 150V rating is mandatory to survive ringing on the 80V rail during high-speed switching.
        
- **Inductor:** 6.8µH High-Current Shielded ($I_{sat}$ > 15A).
    
- **Output Caps:** 150V rated Low-ESR Polymer/Ceramic bank.
    

## 4. Auxiliary Power Rails

Internal logic and analog rails are derived from the selected main input (`V_PWR_MUX`) via cascaded regulators.

|**Rail**|**Source**|**Voltage**|**Components / Use**|
|---|---|---|---|
|**+6V**|**LMR43610**|+6.0V|Intermediate Buck. Feeds LDOs.|
|**+5V**|**LMR51430**|+5.0V|**Relays (G2RL-2)**, Gate Drivers (LMG1210).|
|**+3.3V**|**LMR51430**|+3.3V|Digital Logic (STM32 IO, FPGA IO, Display).|
|**+5VA**|LDO (TPS7A92)|+5.0V|Low-Noise Analog (ADC, Op-Amps, PGAs).|
|**+3.3VA**|LDO (TPS7A20)|+3.3V|Low-Noise Analog (STM32 ADC, Clock).|
|**FPGA1V2**|LDO (TPS7A20)|+1.2V|FPGA Core Logic.|

## 5. Safety & Protection

- **80V Hazard:** The Veer output rail carries high-voltage DC energy.
    
- **Reverse Polarity:** The External DC input includes P-FET reverse polarity protection (integrated into the PowerPath logic).
    
- **Input Surge:** TVS diodes clamp transients on both USB and External inputs