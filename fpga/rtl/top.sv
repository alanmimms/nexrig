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
    input  logic        clk25MHz,       // 25 MHz input clock
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
    
    // PLL for clock generation
    // Generate 100 MHz system clock from 25 MHz input
    pll100MHz uPll (
        .clkIn      (clk25MHz),
        .clkOut     (sysClk),
        .locked     ()
    );
    
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