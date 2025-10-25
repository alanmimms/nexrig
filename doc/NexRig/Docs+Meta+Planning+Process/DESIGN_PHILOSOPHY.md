# Design Philosophy: Active Simplification

## Core Principle
New capabilities often make old subsystems redundant. Always check if new measurements/processing can eliminate existing hardware.

## Simplification Checklist
When adding any new capability:

1. **Superset Analysis**: What can this replace?
2. **Derived Measurements**: What do we measure indirectly that we could calculate?
3. **Shared Infrastructure**: What old hardware can leverage new processing?
4. **BOM Impact**: Quantify savings (components, cost, area)

## Trigger Questions
- Can we derive this from existing data?
- Does new capability provide superset of old measurement?
- Can DSP/calculation replace analog hardware?
- What hardware exists only to compensate for missing information?

## Example: Vector Analysis → VSWR
**Old**: Bruene coupler ($22, 10 components, calibration)
**New**: VSWR = (1 + |Γ|) / (1 - |Γ|) from vector Z measurement
**Result**: Hardware eliminated, more information available

## Pattern: Measurement Hierarchy
Direct measurement at lower level → Calculate all derived quantities
- Z_antenna → VSWR, return loss, mismatch loss
- Vector I/Q → Phase, magnitude, harmonics
- Time-domain → Frequency-domain via FFT
