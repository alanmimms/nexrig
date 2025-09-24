/**
 * WASM DSP Wrapper for AudioWorklet
 * Loads and provides interface to high-performance WASM DSP functions
 */

class WasmDspWrapper {
    constructor() {
        this.wasmModule = null;
        this.wasmReady = false;
        this.functions = {};
        this.memoryBuffers = new Map();

        // Function mode mappings
        this.DEMOD_MODES = {
            'usb': 0,
            'lsb': 1,
            'am': 2,
            'cw': 3
        };
    }

    async initialize() {
        try {
            // Import the WASM module
            // Note: In AudioWorklet, we need to use importScripts with full path
            if (typeof importScripts !== 'undefined') {
                // AudioWorklet environment - use absolute path
                importScripts('/app/wasm/sdr_dsp.js');
                this.wasmModule = await SdrDspModule();
            } else {
                // Main thread environment
                const SdrDspModule = await import('/app/wasm/sdr_dsp.js');
                this.wasmModule = await SdrDspModule.default();
            }

            // Wrap the C functions for JavaScript use
            this.functions = {
                init_hilbert_filter: this.wasmModule.cwrap('init_hilbert_filter', null, []),
                hilbert_transform_sample: this.wasmModule.cwrap('hilbert_transform_sample', 'number', ['number']),
                hilbert_transform_block: this.wasmModule.cwrap('hilbert_transform_block', null, ['number', 'number', 'number']),
                usb_demodulate_block: this.wasmModule.cwrap('usb_demodulate_block', null, ['number', 'number', 'number', 'number']),
                lsb_demodulate_block: this.wasmModule.cwrap('lsb_demodulate_block', null, ['number', 'number', 'number', 'number']),
                am_demodulate_block: this.wasmModule.cwrap('am_demodulate_block', null, ['number', 'number', 'number', 'number']),
                decimate_by_2: this.wasmModule.cwrap('decimate_by_2', 'number', ['number', 'number', 'number']),
                process_baseband_iq_block: this.wasmModule.cwrap('process_baseband_iq_block', 'number',
                    ['number', 'number', 'number', 'number', 'number']),
                allocate_memory: this.wasmModule.cwrap('allocate_memory', 'number', ['number']),
                free_memory: this.wasmModule.cwrap('free_memory', null, ['number'])
            };

            // Initialize the Hilbert filter
            this.functions.init_hilbert_filter();

            this.wasmReady = true;
            return true;

        } catch (error) {
            console.error('Failed to initialize WASM DSP module:', error);
            this.wasmReady = false;
            return false;
        }
    }

    // Allocate WASM memory for a Float32Array
    allocateFloat32Buffer(size) {
        const byteSize = size * 4; // Float32 = 4 bytes
        const ptr = this.functions.allocate_memory(byteSize);

        if (ptr === 0) {
            throw new Error('Failed to allocate WASM memory');
        }

        const buffer = {
            ptr: ptr,
            size: size,
            byteSize: byteSize,
            view: new Float32Array(this.wasmModule.HEAPF32.buffer, ptr, size)
        };

        this.memoryBuffers.set(ptr, buffer);
        return buffer;
    }

    // Free WASM memory buffer
    freeFloat32Buffer(buffer) {
        if (this.memoryBuffers.has(buffer.ptr)) {
            this.functions.free_memory(buffer.ptr);
            this.memoryBuffers.delete(buffer.ptr);
        }
    }

    // High-performance combined processing function
    processIqBlock(iSamples, qSamples, mode = 'usb') {
        if (!this.wasmReady) {
            throw new Error('WASM DSP module not ready');
        }

        const inputLength = iSamples.length;
        const outputLength = Math.floor(inputLength / 2);

        // Allocate WASM memory buffers
        const iBuffer = this.allocateFloat32Buffer(inputLength);
        const qBuffer = this.allocateFloat32Buffer(inputLength);
        const audioBuffer = this.allocateFloat32Buffer(outputLength);

        try {
            // Copy input data to WASM memory
            iBuffer.view.set(iSamples);
            qBuffer.view.set(qSamples);

            // Call WASM processing function
            const actualOutputLength = this.functions.process_baseband_iq_block(
                iBuffer.ptr,
                qBuffer.ptr,
                inputLength,
                audioBuffer.ptr,
                this.DEMOD_MODES[mode] || 0
            );

            // Copy result back to JavaScript
            const result = new Float32Array(actualOutputLength);
            result.set(audioBuffer.view.subarray(0, actualOutputLength));

            return result;

        } finally {
            // Clean up WASM memory
            this.freeFloat32Buffer(iBuffer);
            this.freeFloat32Buffer(qBuffer);
            this.freeFloat32Buffer(audioBuffer);
        }
    }

    // Individual demodulation functions (for flexibility)
    usbDemodulate(iSamples, qSamples) {
        if (!this.wasmReady) {
            throw new Error('WASM DSP module not ready');
        }

        const length = iSamples.length;
        const iBuffer = this.allocateFloat32Buffer(length);
        const qBuffer = this.allocateFloat32Buffer(length);
        const audioBuffer = this.allocateFloat32Buffer(length);

        try {
            iBuffer.view.set(iSamples);
            qBuffer.view.set(qSamples);

            this.functions.usb_demodulate_block(
                iBuffer.ptr,
                qBuffer.ptr,
                audioBuffer.ptr,
                length
            );

            const result = new Float32Array(length);
            result.set(audioBuffer.view);
            return result;

        } finally {
            this.freeFloat32Buffer(iBuffer);
            this.freeFloat32Buffer(qBuffer);
            this.freeFloat32Buffer(audioBuffer);
        }
    }

    lsbDemodulate(iSamples, qSamples) {
        if (!this.wasmReady) {
            throw new Error('WASM DSP module not ready');
        }

        const length = iSamples.length;
        const iBuffer = this.allocateFloat32Buffer(length);
        const qBuffer = this.allocateFloat32Buffer(length);
        const audioBuffer = this.allocateFloat32Buffer(length);

        try {
            iBuffer.view.set(iSamples);
            qBuffer.view.set(qSamples);

            this.functions.lsb_demodulate_block(
                iBuffer.ptr,
                qBuffer.ptr,
                audioBuffer.ptr,
                length
            );

            const result = new Float32Array(length);
            result.set(audioBuffer.view);
            return result;

        } finally {
            this.freeFloat32Buffer(iBuffer);
            this.freeFloat32Buffer(qBuffer);
            this.freeFloat32Buffer(audioBuffer);
        }
    }

    amDemodulate(iSamples, qSamples) {
        if (!this.wasmReady) {
            throw new Error('WASM DSP module not ready');
        }

        const length = iSamples.length;
        const iBuffer = this.allocateFloat32Buffer(length);
        const qBuffer = this.allocateFloat32Buffer(length);
        const audioBuffer = this.allocateFloat32Buffer(length);

        try {
            iBuffer.view.set(iSamples);
            qBuffer.view.set(qSamples);

            this.functions.am_demodulate_block(
                iBuffer.ptr,
                qBuffer.ptr,
                audioBuffer.ptr,
                length
            );

            const result = new Float32Array(length);
            result.set(audioBuffer.view);
            return result;

        } finally {
            this.freeFloat32Buffer(iBuffer);
            this.freeFloat32Buffer(qBuffer);
            this.freeFloat32Buffer(audioBuffer);
        }
    }

    // Clean up all allocated memory
    cleanup() {
        for (const buffer of this.memoryBuffers.values()) {
            this.functions.free_memory(buffer.ptr);
        }
        this.memoryBuffers.clear();
    }
}

// Export for use in AudioWorklet
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WasmDspWrapper;
} else if (typeof self !== 'undefined') {
    // AudioWorklet global scope
    self.WasmDspWrapper = WasmDspWrapper;
}