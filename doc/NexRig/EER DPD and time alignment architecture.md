# EER Transmitter DPD and Time-Alignment Architecture

## 1. High-Level Architecture

This document describes the Digital Pre-Distortion (DPD) and timing architecture for a high-performance, low-cost EER (Envelope Elimination and Restoration) transmitter.

The system uses a "split-processing" hybrid architecture, leveraging two components:

1.  **STM32 Microcontroller:** Acts as the primary Digital Signal Processor (DSP) and "coarse" controller. It handles all audio processing, modulation, and amplitude-path DPD.
2.  **Lattice iCE40UP3K FPGA:** Acts as a high-speed, picosecond-precision "fast-time" executor. It is responsible for generating the phase-modulated RF signal and applying high-resolution AM-to-PM DPD.

The core challenge is solving two problems:
* **Problem A: Coarse Time-Alignment:** The envelope signal path (STM32 -> DAC -> Supply Modulator) is extremely slow (microseconds) compared to the RF phase path (FPGA -> Gate Driver) (nanoseconds).
* **Problem B: Dynamic Distortion:** The power amplifier (PA) introduces non-linearities, primarily:
    * **AM-AM:** The amplitude path is not linear (e.g., 50% input power != 50% output power).
    * **AM-to-PM:** The amplitude of the envelope *pulls* the phase of the RF signal, introducing phase distortion.



---

## 2. System Architecture and Division of Labor

The two problems are solved by assigning tasks to the chip best suited for the job.

### STM32: The "Coarse" DSP

The STM32 handles all sample-rate (48 kS/s) processing and the entire amplitude path.

1.  **DSP Processing:** Generates the "ideal" digital I/Q signal and separates it into `Amplitude[n]` and `Phase[n]` data streams for each 48 kHz sample.
2.  **Amplitude (AM-AM) DPD:** The STM32 runs its *own* DPD for the amplitude path. The `Amplitude[n]` value is used as an address for a 1D Look-Up Table (LUT) stored in the STM32's memory. This LUT pre-warps the amplitude value to correct for the non-linearity of the DAC and the external buck/boost modulator.
3.  **Coarse Time-Alignment:** The STM32 uses a circular buffer to delay its *own* amplitude signal by **N samples**. This **N**-sample delay (e.g., 20 samples $\approx$ 416 \text{ \mu s}) is calibrated to perfectly match the coarse, static delay of the external supply modulator.
4.  **Final AM Output:** The pre-warped, delayed amplitude signal is sent to the STM32's internal **DAC**, which drives the external buck/boost supply modulator.
5.  **Data Transmission to FPGA:** At the *same time* the STM32 sends the *old* `Amplitude[n-N]` value to its DAC, it sends the *current* `Amplitude[n]` and `Phase[n]` values to the FPGA over a 32-bit I2S stream.

### FPGA: The "Fine-Time" Executor

The FPGA's only job is to execute the RF phase path with picosecond precision.

1.  **NCO (RF Signal Generation):** The `Phase[n]` data from the I2S stream is used to drive the 32-bit NCOs, generating the RF clock for the power MOSFET.
2.  **Phase (AM-to-PM) DPD:** The `Amplitude[n]` data from the I2S stream is used as the address for a **second DPD LUT** stored in the FPGA's SPRAM. This LUT stores the *time correction* (AM-to-PM) needed for that specific amplitude.
3.  **Variable Delay Line (VDL):** The output of the DPD LUT is a digital *delay code* (e.g., 0, 1, 2... 255) that controls a high-resolution VDL.
4.  **Final PM Output:** The NCO's output signal is passed through this VDL, which dynamically adjusts its delay on a picosecond scale, canceling the AM-to-PM distortion *before* it gets to the gate driver.

---

## 3. Implementation: The FPGA's Picosecond VDL

The VDL is the core of the FPGA's DPD system. It is not a hard macro but is built from general fabric, which requires a specific design and calibration.

### VDL Construction: `SB_CARRY` Chain

To create a stable delay with fine resolution, the VDL is built from a long chain of `SB_CARRY` primitives (the fast-carry logic inside each Logic Cell).

* **Why `SB_CARRY`?** The carry path is a dedicated, high-speed, low-jitter routing resource. The delay from one cell's `CIN` to its `COUT` is extremely small and consistent (e.g., ~50 ps).
* **Structure:** A 200- to 256-stage chain is created by cascading `SB_CARRY` cells. The `COUT` of *every* cell is "tapped" (routed) to a large multiplexer.
* **Control:** The DPD LUT's output code is the `select` input for this MUX. A code of `0` selects the first tap (no delay), and a code of `5` selects the output of the 5th cell, adding $\sim 250 \text{ ps}$ of delay.



### VDL Calibration Requirement

The `ps/tap` delay is not a guaranteed 50 ps. It is an analog value that **drifts** with chip temperature (PVT). A "cold" chip might be 45 ps/tap, while a "hot" chip is 55 ps/tap.

To fix this, the VDL must be calibrated. An "offline" calibration method is used to save resources:

1.  **Mode Switch:** The VDL's input is a MUX that can select either the *live NCO signal* (Run Mode) or a *stable PLL clock* (Calibrate Mode).
2.  **Calibration:** The system periodically enters "Calibrate Mode." A 100 MHz clock (10,000 ps period) is fed into the VDL.
3.  **Measurement:** Logic measures how many taps the clock edge propagates through in one 10,000 ps cycle.
    * *Example:* If the edge passes 200 taps, the logic calculates: `10,000 ps / 200 taps = 50 ps/tap`.
4.  **Store Value:** This `50 ps/tap` value is stored in a register.
5.  **Run Mode:** The DPD logic uses this stored `ps/tap` value to generate its DPD LUTs, ensuring the time corrections are always accurate to the current physical state of the chip.

---

## 4. Final DPD Signal Flow Summary

This diagram shows the complete signal flow inside the FPGA for the AM-to-PM correction.



1.  A 32-bit I2S frame arrives from the STM32.
2.  The stream is split.
3.  **Phase Path:** `Phase Data` $\rightarrow$ `NCO` $\rightarrow$ `VDL Input`.
4.  **Amplitude Path:** `Amplitude Data` $\rightarrow$ `AM-to-PM DPD LUT (in SPRAM)` $\rightarrow$ `Delay Code`.
5.  **Correction:** The `Delay Code` is applied to the `VDL Select` lines.
6.  **Final Output:** The `VDL Output` is the final, corrected RF signal sent to the power MOSFET's gate driver.

The final output time at the hardware pin is:

$$ T_{\text{final}} = T_{\text{NCO}} + T_{\text{static\_trim}} + T_{\text{DPD\_LUT}}[Amplitude] $$

Where:
* $T_{\text{NCO}}$: The ideal phase time from the NCO.
* $T_{\text{static\_trim}}$: A fixed, calibrated VDL offset to align the RF and Envelope paths.
* $T_{\text{DPD\_LUT}}[Amplitude]$: The dynamic, 50 ps-multiple time delay looked up from the DPD table, which cancels the AM-to-PM distortion.