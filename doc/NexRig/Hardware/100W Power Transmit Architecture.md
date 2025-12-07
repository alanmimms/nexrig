# 100W Power Transmit Architecture

- **Component:** 4-FET Quadrature Class-D H-Bridge
    
- **Power Output:** 100W Continuous (CW/Digi/SSB)
    
- **Frequency Range:** 1.8 – 30 MHz
    
- **Impedance Domain:** 36Ω Differential to 200Ω Single-Ended
    

## 1. Overview

The Power Amplifier (PA) uses a **Class-D H-Bridge topology** driven by quadrature signals. Unlike traditional linear amplifiers, the PA operates as a high-speed switch. The output amplitude is controlled by modulating the drain voltage ($V_{DD}$) via the EER Envelope Supply (0V–80V), while the phase is controlled by the precise timing of the gate drive signals.

This topology naturally cancels even-order harmonics (2nd, 4th, etc.) due to its differential push-pull action, significantly reducing the filtering requirements of the Low-Pass Filter (LPF) array.

## 2. Architecture

### 2.1 Signal Path

1. **Input:** Four 3.3V logic-level signals ($I+, I-, Q+, Q-$) arrive from the FPGA.
    
2. **Gate Drive:** Two **TI LMG1210** half-bridge drivers boost these signals to drive the GaN FET gates.
    
3. **Switching Core:** Four **EPC2207 eGaN FETs** switch the EER supply voltage across the transformer primary.
    
4. **Impedance Transformation:** A wideband transformer (`T2301`) steps up the 36Ω differential output to a 200Ω single-ended signal.
    
5. **Output:** The 200Ω signal is fed directly to the LPF Array. **Note:** There is no resonant "PA Tank" circuit; signal reconstruction relies on the LPFs and the transformer inductance.
    

## 3. Key Components

### 3.1 H-Bridge MOSFETs

- **Part:** **EPC2207** (eGaN FET)
    
- **Quantity:** 4 (Q2301, Q2302, Q2304, Q2306)
    
- **Spec:** 200V $V_{DS}$ | 14A Pulse | 22 mΩ $R_{DS(on)}$
    
- **Selection Criteria:**
    
    - **Voltage Safety:** The 80V rail requires >150V rating to survive switch-node ringing. The 200V rating provides a 2.5x safety factor against the nominal 80V rail.
        
    - **Efficiency:** Low $Q_g$ (5.6 nC) minimizes driver power consumption at 30 MHz.
        

### 3.2 High-Side Bias Sync

- **Part:** **EPC2207** (Same as H-Bridge)
    
- **Quantity:** 2 (Q2303, Q2305)
    
- **Function:** Acts as a synchronous bootstrap switch to recharge the high-side gate driver capacitors.
    
- **Rationale:** Replaces standard bootstrap diodes to reduce voltage drop and improve high-duty-cycle performance. Using the same part number simplifies the BOM.
    

### 3.3 Wideband Output Transformer

- **Part:** Custom Winding
    
- **Core:** Two stacked **FT240-43** ferrite toroids.
    
    - _Design Note:_ The schematic may reference "FT240-61", but **Mix 43 is required** for 1.8 MHz operation. Mix 61 has insufficient permeability ($\mu_i=125$) at 160m, which would cause low magnetizing inductance and core saturation. Mix 43 ($\mu_i=850$) provides the necessary inductance for the 3-turn primary.
        
- **Winding:**
    
    - **Primary:** 3 turns #18 AWG Bifilar (Center tapped for DC feed).
        
    - **Secondary:** 7 turns #18 AWG.
        
- **Transformation:** 3:7 turns ratio creates an impedance transformation of approximately **1:5.4**.
    
    - Input: 36Ω Differential.
        
    - Output: ~200Ω Single-Ended.
        
- **Flux Density:** The large stacked FT240 core volume is required to prevent saturation at 100W/1.8 MHz.
    

## 4. Thermal & Mechanical Design

### 4.1 Dissipation

At 100W output with an estimated 85% drain efficiency, the PA stage dissipates approximately **17W** of heat.

### 4.2 Cooling Requirements

- **Heatsink:** The PCB is designed to mount directly to a milled aluminum chassis or heat spreader.
    
- **Thermal Vias:** The layout uses dense via stitching under the GaN FETs to transfer heat from the top-layer pads to the bottom-layer thermal interface.
    
- **Interface:** A high-performance thermal gap pad or phase-change material is required between the PCB bottom and the chassis.
    

## 5. High Voltage Safety (80V Rail)

The EER supply generates up to **80V DC**. This voltage is present on the transformer center tap and the drain tabs of the MOSFETs.

- **Capacitor Ratings:** All bypass capacitors on the `Veer` rail must be rated **≥100V** (ideally 160V).
    
- **Clearance:** PCB layout maintains IPC-2221 creepage distances for 100V operation between the High Voltage rail and Logic Ground.