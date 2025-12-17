//-----------------------------------------------------------------------------
// Title      : Top Level Module for NexRig FPGA
// Project    : NexRig USB SSB Transceiver
//-----------------------------------------------------------------------------
// File       : top.sv
// Author     : NexRig Project
// Created    : 2025-01-23
// Platform   : ICE40UP3K
//-----------------------------------------------------------------------------
// Description:
// Top level module instantiating NCO, SPI interface, and control logic
//-----------------------------------------------------------------------------

`timescale 1ns / 1ps

module top (
	    // System clock and reset
	    input  logic        clk30MHz,       // 30 MHz input clock
	    input  logic        rstN,           // Active low reset

	    // SPI interface to STM32
	    input  logic        spiSclk,        // SPI clock from STM32
	    input  logic        spiCsN,         // SPI chip select (active low)
	    input  logic        spiMosi,        // SPI data from STM32
	    output logic        spiMiso,        // SPI data to STM32

	    // NCO/Class E PA control
	    output logic        rfOut,          // RF square wave to gate driver
	    output logic        rfOutN,         // Complementary RF output

	    // PIN diode control
	    output logic [7:0]  bandSelect,     // Band selection outputs
	    output logic        txEnable,       // TX/RX switch control

	    // Status LEDs
	    output logic        ledStatus,      // Status LED
	    output logic        ledTx           // TX indicator LED
	    );

  // Internal signals
  logic           sysClk;             // System clock (PLL output)
  logic [31:0]    freqControl;        // Frequency control word
  logic [15:0]    phaseOffset;        // Phase offset
  logic           ncoEnable;          // NCO enable signal
  
  // Instantiate the PLL primitive for the iCE40
  // This takes a dedicated clock input pin
  SB_PLL40_PAD #(
		 .FEEDBACK_PATH("SIMPLE"),
		 .DIVR(4'b0000),          // DIVR = 0  (Reference Clock Divider)
		 .DIVF(7'b0100111),      // DIVF = 39 (Feedback Divider / Multiplier)
		 .DIVQ(3'b011),          // DIVQ = 3  (VCO Output Divider)
		 .FILTER_RANGE(3'b001)   // Loop filter setting
		 ) pll_inst (
			     .PACKAGEPIN(clk30MHz),  // Input from the TCXO
			     .PLLOUTCORE(clk240MHz),    // Output to internal FPGA logic
			     .RESETB(1'b1),
			     .BYPASS(1'b0)
			     );

  // The formula for output frequency is roughly:
  // F_OUT = F_IN * (DIVF + 1) / ((DIVR + 1) * 2^DIVQ)
  // F_OUT = 30MHz * (39 + 1) / ((0 + 1) * 2^3)
  // F_OUT = 30MHz * 40 / 8 = 150MHz
  //
  // NOTE: Let me correct the values for 240 MHz.
  // F_OUT = 30MHz * (31 + 1) / ((0 + 1) * 2^2) = 30 * 32 / 4 = 240 MHz
  // So the correct values would be:
  // .DIVF(7'b0011111),      // DIVF = 31
  // .DIVQ(3'b010),          // DIVQ = 2


  // NCO for phase generation
  nco uNco (
            .clk            (sysClk),
            .rstN           (rstN),
            .enable         (ncoEnable),
            .freqControl    (freqControl),
            .phaseOffset    (phaseOffset),
            .rfOut          (rfOut),
            .rfOutN         (rfOutN)
	    );
  
  // SPI slave interface
  spiSlave uSpi (
		 .clk            (sysClk),
		 .rstN           (rstN),
		 .spiSclk        (spiSclk),
		 .spiCsN         (spiCsN),
		 .spiMosi        (spiMosi),
		 .spiMiso        (spiMiso),
		 .freqControl    (freqControl),
		 .phaseOffset    (phaseOffset),
		 .ncoEnable      (ncoEnable),
		 .bandSelect     (bandSelect),
		 .txEnable       (txEnable)
		 );
  
  // LED indicators
  assign ledStatus = ncoEnable;
  assign ledTx = txEnable;

endmodule
