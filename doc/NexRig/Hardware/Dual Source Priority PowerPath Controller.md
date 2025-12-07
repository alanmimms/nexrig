To implement "Option 3" (Dual Source with Priority), you need a **PowerPath Controller**. Simple diode-ORing is insufficient because the USB-PD voltage (20V) is _higher_ than the external DC (13.8V), so a diode-OR would incorrectly drain the USB source first until it collapsed.

You need a **Priority Mux** that selects the External DC whenever it is valid, regardless of voltage.

#### 1. The Solution: Analog Devices LTC4417

This is the industry-standard "Prioritized PowerPath Controller."

- **Function:** It drives external P-Channel MOSFETs to switch between three inputs (V1, V2, V3) based on priority, not voltage.
    
- **Architecture:**
    
    - **V1 (Highest Priority):** Connect to the **External DC Jack** (13.8V).
        
    - **V2 (Medium Priority):** Connect to **USB-PD VBUS** (20V).
        
    - **Output:** Connects to the **Veer Supply Input** and **Auxiliary Buck Regulators**.
        
- **Logic:** When you plug in the external battery/PSU (12V–15V), the LTC4417 detects it is within the "Valid" window (set by resistive dividers) and _hard switches_ the system to V1, disconnecting USB-PD current. When you unplug external power, it seamlessly switches back to V2 (USB-PD) for receive/low-power operation.
    

#### 2. Component Selection

- **Controller:** **LTC4417** (or **LTC4421** if you prefer N-Channel FETs for slightly lower loss at 15A, though P-Channels are easier to implement).
    
- **MOSFETs:** You need back-to-back P-FETs to prevent backfeeding. Look for **-30V or -40V rated P-Channels** with $R_{DS(on)} < 5m\Omega$ (e.g., **Vishay Si7655DN** or similar).
    
- **Connector:** For the 100W input, the **Anderson Powerpole** is the amateur radio standard (ARES/RACES compliance). The **XT60** is a valid, compact alternative often used in modern portable SDRs (like the Lab599 TX-500). Given your "commercial" aspiration, Powerpoles are generally preferred by the customer base for base/mobile ops.