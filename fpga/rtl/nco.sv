//-----------------------------------------------------------------------------
// Title      : Numerically Controlled Oscillator (NCO) for Class E PA
// Project    : NexRig USB SSB Transceiver
//-----------------------------------------------------------------------------
// File       : nco.sv
// Author     : NexRig Project
// Created    : 2025-01-23
//-----------------------------------------------------------------------------
// Description:
// 32-bit phase accumulator NCO for phase modulation control
// Generates square wave output for Class E switching at RF frequency
// Phase modulation achieved by adding phase offset to accumulator
//-----------------------------------------------------------------------------

`timescale 1ns / 1ps

module nco (
    input  logic        clk,            // System clock (100 MHz)
    input  logic        rstN,           // Active low reset
    input  logic        enable,         // NCO enable
    input  logic [31:0] freqControl,    // Frequency control word
    input  logic [15:0] phaseOffset,    // Phase offset for modulation
    output logic        rfOut,          // Square wave RF output
    output logic        rfOutN          // Complementary output (for differential drive)
);

    // Internal signals
    logic [31:0] phaseAccumulator;
    logic [31:0] phaseNext;
    logic [31:0] phaseModulated;
    
    // Phase accumulator
    always_ff @(posedge clk or negedge rstN) begin
        if (!rstN) begin
            phaseAccumulator <= 32'h0;
        end else if (enable) begin
            phaseAccumulator <= phaseNext;
        end
    end
    
    // Phase calculation with modulation
    assign phaseNext = phaseAccumulator + freqControl;
    assign phaseModulated = phaseNext + {phaseOffset, 16'h0};  // Phase offset in upper bits
    
    // Generate square wave output from MSB of phase accumulator
    // MSB toggles at carrier frequency
    always_ff @(posedge clk or negedge rstN) begin
        if (!rstN) begin
            rfOut <= 1'b0;
            rfOutN <= 1'b1;
        end else if (enable) begin
            rfOut <= phaseModulated[31];     // MSB is the square wave output
            rfOutN <= ~phaseModulated[31];  // Complementary for differential
        end else begin
            rfOut <= 1'b0;
            rfOutN <= 1'b0;  // Both low when disabled (MOSFET off)
        end
    end

endmodule