//-----------------------------------------------------------------------------
// Title      : SPI Slave Interface
// Project    : NexRig USB SSB Transceiver
//-----------------------------------------------------------------------------
// File       : spiSlave.sv
// Author     : NexRig Project
// Created    : 2025-01-23
//-----------------------------------------------------------------------------
// Description:
// SPI slave interface for communication with STM32
// Handles frequency control, phase offset, and GPIO control registers
//-----------------------------------------------------------------------------

`timescale 1ns / 1ps

module spiSlave (
    input  logic        clk,            // System clock
    input  logic        rstN,           // Active low reset
    
    // SPI interface
    input  logic        spiSclk,        // SPI clock from master
    input  logic        spiCsN,         // Chip select (active low)
    input  logic        spiMosi,        // Master out, slave in
    output logic        spiMiso,        // Master in, slave out
    
    // Control registers
    output logic [31:0] freqControl,    // Frequency control word
    output logic [15:0] phaseOffset,    // Phase offset
    output logic        ncoEnable,      // NCO enable
    output logic [7:0]  bandSelect,     // Band selection
    output logic        txEnable        // TX enable
);

    // SPI state machine states
    typedef enum logic [2:0] {
        IDLE,
        ADDR_BYTE,
        DATA_BYTES
    } spiState_t;
    
    spiState_t state, nextState;
    
    // Internal registers
    logic [7:0]  address;
    logic [7:0]  byteCounter;
    logic [31:0] shiftReg;
    logic        writeEn;
    
    // Synchronize SPI signals to system clock
    logic spiClkSync, spiClkPrev;
    logic spiCsNSync;
    logic spiMosiSync;
    
    always_ff @(posedge clk) begin
        spiClkSync <= spiSclk;
        spiClkPrev <= spiClkSync;
        spiCsNSync <= spiCsN;
        spiMosiSync <= spiMosi;
    end
    
    // Detect rising edge of SPI clock
    logic spiClkRising;
    assign spiClkRising = spiClkSync && !spiClkPrev;
    
    // SPI shift register operation
    always_ff @(posedge clk or negedge rstN) begin
        if (!rstN) begin
            shiftReg <= 32'h0;
            address <= 8'h0;
            byteCounter <= 8'h0;
            writeEn <= 1'b0;
        end else if (spiCsNSync) begin
            // Reset when CS is high
            byteCounter <= 8'h0;
            writeEn <= 1'b0;
            state <= IDLE;
        end else if (spiClkRising) begin
            // Shift in data on rising edge of SPI clock
            shiftReg <= {shiftReg[30:0], spiMosiSync};
            
            if (byteCounter == 8'd7) begin
                // First byte is address
                address <= {shiftReg[6:0], spiMosiSync};
                state <= DATA_BYTES;
            end else if (byteCounter == 8'd39) begin
                // After 32 data bits, enable write
                writeEn <= 1'b1;
            end
            
            byteCounter <= byteCounter + 8'd1;
        end else begin
            writeEn <= 1'b0;
        end
    end
    
    // Register write logic
    always_ff @(posedge clk or negedge rstN) begin
        if (!rstN) begin
            freqControl <= 32'h0;
            phaseOffset <= 16'h0;
            ncoEnable <= 1'b0;
            bandSelect <= 8'h0;
            txEnable <= 1'b0;
        end else if (writeEn) begin
            case (address)
                8'h00: freqControl <= shiftReg;           // Frequency control word
                8'h04: phaseOffset <= shiftReg[15:0];     // Phase offset
                8'h08: begin
                    ncoEnable <= shiftReg[0];             // Control register
                    txEnable <= shiftReg[1];
                end
                8'h0C: bandSelect <= shiftReg[7:0];       // Band selection
            endcase
        end
    end
    
    // SPI MISO output (status readback)
    always_ff @(posedge clk or negedge rstN) begin
        if (!rstN) begin
            spiMiso <= 1'b0;
        end else begin
            case (address)
                8'h00: spiMiso <= freqControl[31 - (byteCounter[4:0])];
                8'h04: spiMiso <= (byteCounter[4:0] < 16) ? 
                                  phaseOffset[15 - byteCounter[3:0]] : 1'b0;
                8'h08: spiMiso <= (byteCounter[4:0] == 0) ? ncoEnable :
                                  (byteCounter[4:0] == 1) ? txEnable : 1'b0;
                8'h0C: spiMiso <= (byteCounter[4:0] < 8) ? 
                                  bandSelect[7 - byteCounter[2:0]] : 1'b0;
                default: spiMiso <= 1'b0;
            endcase
        end
    end

endmodule