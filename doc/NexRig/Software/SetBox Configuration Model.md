# SetBox Configuration Model

**Engine:** Lua 5.4 **Pattern:** Prototype-based Inheritance (via Metatables) **Storage Format:** Serialized Lua Tables or JSON

## 1. Overview

The **SetBox** model changes the paradigm of radio configuration from a "flat state" (where every knob is independent) to a **Hierarchical Context** (where settings inherit defaults and specific overrides).

This allows operators to define complex operating scenarios (e.g., "Field Day 40m CW") that inherit standard behaviors (e.g., "Standard 40m Settings") which in turn inherit global hardware limits (e.g., "Global Radio Config").

## 2. The Inheritance Model

The system utilizes Lua's `metatable` and `__index` metamethod to create efficient inheritance chains.

### 2.1 Hierarchy Levels

While the depth is unlimited, the standard hierarchy is:

1. **Global (Root):** Hardware limits, calibration data, operator callsign, default audio routing.
2. **Band (Child of Global):** Antenna selection, default power levels for the band, filter selection strategies.
3. **Mode (Child of Band):** Bandwidth, modulation type, AGC constants.
4. **Scenario (Child of Mode):** Contest-specific macros, specialized DSP settings (e.g., "Digi Mode" disabling speech processing).
### 2.2 Lua Implementation

In the Lua runtime, a SetBox is simply a table that points to a parent table.

Lua

```
-- 1. Global Configuration (The Root)
GlobalConfig = {
    callsign = "N0CALL",
    power_limit_watts = 100,
    audio_source = "Mic_Input_1",
    agc_speed = "Medium"
}

-- 2. Band Configuration (Inherits Global)
Band_20m = {
    frequency = 14200000,
    antenna_port = 1,
    -- Inherits 'callsign', 'power_limit_watts', etc.
}
setmetatable(Band_20m, { __index = GlobalConfig })

-- 3. Mode Configuration (Inherits Band)
Mode_20m_FT8 = {
    mode = "USB-D",
    bandwidth = 3000,
    agc_speed = "Fast",    -- OVERRIDE: FT8 needs fast AGC
    power_limit_watts = 50 -- OVERRIDE: 50W limit for high duty cycle
}
setmetatable(Mode_20m_FT8, { __index = Band_20m })
```

### 2.3 Resolution Logic

When the C++ host or the UI requests a setting (e.g., `CurrentConfig.power_limit_watts`), Lua performs the lookup:

1. Check `Mode_20m_FT8`: Found `50`. **Result: 50**.
2. Check `Mode_20m_FT8` for `callsign`: Not found.
    - Go to Parent (`Band_20m`): Not found.
    - Go to Parent (`GlobalConfig`): Found `"N0CALL"`. **Result: "N0CALL"**.

## 3. Hardware Abstraction & Hooks

Configuration changes trigger hardware actions through **Observer Hooks**. When a SetBox is activated or a value is changed, Lua executes the associated hardware bindings.

### 3.1 Property Hooks

Lua

```
-- Define a hook for when 'frequency' changes
HardwareHooks.frequency = function(new_freq)
    -- 1. C++ Host Command: Set VFO
    Radio.setVFO(new_freq)
    
    -- 2. Logic: Check if we need to switch LPF Banks
    if new_freq < 2500000 then
        Radio.setRelay("LPF_BANK", "160m")
    elseif new_freq < 6000000 then
        Radio.setRelay("LPF_BANK", "80m_60m")
    end
    
    -- 3. Logic: Preselector Tracking
    local cap_value = CalculatePreselector(new_freq)
    Radio.setPreselector(cap_value)
end
```

This decouples the UI ("I want to be on 14.1 MHz") from the hardware complexity ("Select LPF Bank 3, Capacitor 412, and Inductor 2").

## 4. Persistence

SetBoxes are stored as human-readable JSON or Lua files in the user's profile directory.

**Example JSON Representation (`Mode_20m_FT8.json`):**

JSON

```
{
  "name": "20m FT8 Operations",
  "parent": "Band_20m",
  "overrides": {
    "mode": "USB-D",
    "bandwidth": 3000,
    "agc_speed": "Fast",
    "power_limit_watts": 50
  }
}
```

When the application loads, it deserializes these files and reconstructs the Lua metatable chain dynamically.

## 5. Advantages of this Model

1. **Memory Efficiency:** Only "diffs" (overrides) are stored in memory for child configs.
2. **Safety:** A "Low Power" parent SetBox forces all children to respect the limit unless explicitly overridden.
3. **Portability:** Users can share SetBox files (e.g., "W1ABC's Contesting Setup") that reference standard parents, making configurations portable between different radios.

---

**Completion Status:** We have now completed the documentation refactor for the 100W / Native C++ architecture.

**Hardware Documents:**

1. `hardware/TX-100W-PA.md` (H-Bridge, 80V, FT240-43 cores)
2. `hardware/POWER-SYSTEM.md` (Dual Source, Veer, 150V FETs)
3. `hardware/FILTER-UNIT.md` (Merged LPFs, G2RL Relays, T80 cores)
4. `hardware/RX-FRONT-END.md` (800Ω Preselector, Triple QSD)

**Software Documents:**

1. `software/ARCHITECTURE.md` (C++ / Lua Split)
2. `software/SETBOX-MODEL.md` (Lua Configuration)