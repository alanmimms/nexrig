/**
 * SDR AudioWorklet Processor
 * High-performance DSP running on dedicated audio thread
 */

class SdrProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        // Removed console.log from audio thread

        // DSP parameters
        this.sampleRate = 48000;
        this.iqSampleRate = 96000;
        this.decimationRatio = 2; // 96kHz -> 48kHz
        this.tuningFreq = 0; // Hz (handled by hardware, kept for compatibility)
        this.mode = 'usb';

        // I/Q buffer from WebSocket
        this.iqBuffer = [];
        this.sampleCounter = 0;  // Count processed samples for phase calculation

        // JavaScript DSP implementation for now
        this.hilbertTaps = this.generateHilbertFilter(16); // More taps for better quality
        this.hilbertDelay = new Float32Array(16);
        this.hilbertIndex = 0;

        // AGC - much less aggressive
        this.agcGain = 5.0;  // Start with higher gain
        this.agcTarget = 0.3; // Higher target level

        // Fractional resampler state for stable decimation
        this.resamplerPhase = 0.0;
        this.resamplerRate = this.iqSampleRate / this.sampleRate; // 96000/48000 = 2.0

        // Listen for messages from main thread
        this.port.onmessage = (event) => {
            this.handleMessage(event.data);
        };

        // Debug counters
        this.processCallCount = 0;
        this.iqDataCount = 0;

        // WASM DSP support
        this.wasmDsp = null;
        this.useWasm = false;

        // Test tone for debugging
        this.testTonePhase = 0;
        this.audioTestMode = false;
    }

    
    handleMessage(data) {
        switch (data.type) {
            case 'test':
                // Send response back to main thread instead of console.log
                this.port.postMessage({
                    type: 'testResponse',
                    message: 'AudioWorklet received test message: ' + data.message
                });
                break;
                
            case 'iqData':
                // Add I/Q samples to buffer
                const samples = data.samples;
                if (samples && samples.i && samples.q) {
                    for (let i = 0; i < samples.i.length; i++) {
                        this.iqBuffer.push({
                            i: samples.i[i] / 8388607.0, // 24-bit to float
                            q: samples.q[i] / 8388607.0
                        });
                    }
                    this.iqDataCount++;

                    // Debug: Log when we receive I/Q data
                    if (this.iqDataCount <= 5 || this.iqDataCount % 100 === 0) {
                        this.port.postMessage({
                            type: 'debug',
                            message: `Received I/Q data #${this.iqDataCount}: ${samples.i.length} samples, buffer now has ${this.iqBuffer.length}`
                        });
                    }
                } else {
                    this.port.postMessage({
                        type: 'debug',
                        message: 'ERROR: Received iqData message with invalid samples'
                    });
                }
                break;
                
            case 'setTuning':
                this.tuningFreq = data.frequency;
                // Send immediate confirmation
                this.port.postMessage({
                    type: 'debug',
                    message: `Tuning changed to: ${this.tuningFreq}Hz`
                });
                break;
                
            case 'setMode':
                this.mode = data.mode;
                break;

            case 'initWasm':
                // Initialize WASM DSP wrapper with pre-loaded module
                try {
                    // Import the WASM DSP wrapper class into AudioWorklet context
                    importScripts('./js/wasmDspWrapper.js');

                    this.wasmDsp = new WasmDspWrapper();
                    // Initialize with the pre-loaded WASM module
                    this.wasmDsp.initialize(data.wasmModule).then((success) => {
                        if (success) {
                            this.useWasm = true;
                            this.port.postMessage({
                                type: 'debug',
                                message: 'WASM DSP initialized successfully in AudioWorklet'
                            });
                        } else {
                            this.port.postMessage({
                                type: 'debug',
                                message: 'WASM DSP initialization failed, using JavaScript fallback'
                            });
                        }
                    }).catch((error) => {
                        this.port.postMessage({
                            type: 'debug',
                            message: `WASM DSP initialization error: ${error.message}`
                        });
                    });
                } catch (error) {
                    this.port.postMessage({
                        type: 'debug',
                        message: `WASM DSP import error: ${error.message}, using JavaScript fallback`
                    });
                }
                break;
        }
    }
    
    process(inputs, outputs, parameters) {
        const output = outputs[0];
        const outputChannel = output[0];
        const blockSize = outputChannel.length; // 128 samples

        this.processCallCount++;

        // Send immediate debug on first few calls
        if (this.processCallCount <= 5) {
            this.port.postMessage({
                type: 'debug',
                processCount: this.processCallCount,
                bufferSize: this.iqBuffer.length,
                message: 'AudioWorklet process() is running!'
            });
        }

        // Monitor buffer health
        if (this.processCallCount % 100 === 0) {
            this.port.postMessage({
                type: 'debug',
                processCount: this.processCallCount,
                bufferSize: this.iqBuffer.length,
                message: `Buffer: ${this.iqBuffer.length} samples available`
            });
        }

        // TEMPORARY: Test tone for 3 seconds to verify audio path
        if (this.processCallCount < 48000 / 128 * 3) { // 3 seconds
            for (let i = 0; i < blockSize; i++) {
                // Generate loud 1kHz test tone
                const testSample = 0.3 * Math.sin(2 * Math.PI * 1000 * this.testTonePhase / this.sampleRate);
                outputChannel[i] = testSample;
                this.testTonePhase++;
            }
            // Debug more samples
            if (this.processCallCount < 10) {
                this.port.postMessage({
                    type: 'debug',
                    message: `TEST TONE: 1kHz @ ${outputChannel[0].toFixed(4)}, processCount: ${this.processCallCount}, blockSize: ${blockSize}`
                });
            }
        } else {
            // WASM or JavaScript DSP processing
            if (this.useWasm && this.wasmDsp) {
                // High-performance WASM block processing
                this.processWithWasm(outputChannel, blockSize);
            } else {
                // JavaScript fallback processing
                this.processWithJavaScript(outputChannel, blockSize);
            }
        }

        // Remove consumed I/Q samples from buffer - different logic for WASM vs JavaScript
        if (this.useWasm && this.wasmDsp) {
            // WASM block processing consumes samples differently
            const samplesConsumed = blockSize * 2; // 2:1 decimation
            if (this.iqBuffer.length >= samplesConsumed) {
                this.iqBuffer.splice(0, samplesConsumed);
            }
        } else {
            // JavaScript processing already handled buffer consumption in processWithJavaScript
            // Debug buffer state after processing
            if (this.processCallCount > 1125 && this.processCallCount < 1135) {
                this.port.postMessage({
                    type: 'debug',
                    message: `Buffer after JS processing: ${this.iqBuffer.length} samples remaining`
                });
            }
        }

        // Report buffer status for debugging
        if (this.processCallCount % 50 === 0) {
            const dspMode = this.useWasm ? 'WASM' : 'JavaScript';
            this.port.postMessage({
                type: 'debug',
                message: `Audio processing active (${dspMode}): ${this.iqBuffer.length} I/Q samples in buffer`
            });
        }
        
        // Keep buffer size reasonable but don't throw away too much data
        // Only trim if we have way too much buffered (more than 1 second at 96kHz)
        while (this.iqBuffer.length > 96000) {
            this.iqBuffer.shift();
        }
        
        return true; // Keep processor alive
    }

    processWithWasm(outputChannel, blockSize) {
        // High-performance WASM block processing
        if (this.iqBuffer.length < blockSize * 2) {
            // Not enough I/Q data for block processing
            outputChannel.fill(0);
            return;
        }

        try {
            // Extract I/Q samples for block processing
            const iSamples = new Float32Array(blockSize * 2);
            const qSamples = new Float32Array(blockSize * 2);

            for (let i = 0; i < blockSize * 2; i++) {
                if (i < this.iqBuffer.length) {
                    iSamples[i] = this.iqBuffer[i].i;
                    qSamples[i] = this.iqBuffer[i].q;
                }
            }

            // Process entire block with WASM
            const audioSamples = this.wasmDsp.processIqBlock(iSamples, qSamples, this.mode);

            // Copy results to output with AGC and clipping
            for (let i = 0; i < blockSize; i++) {
                if (i < audioSamples.length) {
                    const sample = this.automaticGainControl(audioSamples[i]);
                    outputChannel[i] = Math.max(-1, Math.min(1, sample));
                } else {
                    outputChannel[i] = 0;
                }
            }

            // Update resampler phase for buffer management
            this.resamplerPhase += blockSize * this.resamplerRate;

        } catch (error) {
            // WASM processing failed, fall back to JavaScript
            this.port.postMessage({
                type: 'debug',
                message: `WASM processing error: ${error.message}, falling back to JavaScript`
            });
            this.useWasm = false;
            this.processWithJavaScript(outputChannel, blockSize);
        }
    }

    processWithJavaScript(outputChannel, blockSize) {
        // Audio-rate-driven processing: Always produce exactly blockSize samples
        // This is the master clock - I/Q buffer should accommodate our needs

        // Require minimum buffer to prevent starvation cycles
        const minBufferSize = 1024; // ~10ms worth of I/Q data at 96kHz
        if (this.iqBuffer.length < minBufferSize) {
            // Not enough buffer - output silence and wait for more data
            outputChannel.fill(0);
            if (this.processCallCount % 50 === 0 || this.processCallCount < 20) {
                this.port.postMessage({
                    type: 'debug',
                    message: `BUFFER STARVATION: need ${minBufferSize}+ samples, have ${this.iqBuffer.length}, outputting silence`
                });
            }
            return;
        }

        for (let i = 0; i < blockSize; i++) {
            let audioSample = 0;

            // Simple 2:1 decimation - need 2 I/Q samples per audio sample
            const iqIndex = i * 2;

            // Check if we have enough I/Q samples for this audio sample
            if (this.iqBuffer.length > iqIndex + 1) {
                const iq = this.iqBuffer[iqIndex];
                const iSample = iq.i;
                const qSample = iq.q;

                // Apply frequency shift if tuning offset is set
                let iShifted = iSample;
                let qShifted = qSample;

                if (this.tuningFreq !== 0) {
                    // Calculate the phase for this sample
                    const sampleTime = (this.sampleCounter + iqIndex) / this.iqSampleRate;
                    const phase = 2 * Math.PI * this.tuningFreq * sampleTime;
                    const cosPhase = Math.cos(-phase); // Negative to shift down
                    const sinPhase = Math.sin(-phase);

                    // Complex multiplication for frequency shift
                    iShifted = iSample * cosPhase - qSample * sinPhase;
                    qShifted = iSample * sinPhase + qSample * cosPhase;
                }

                // Debug first few samples to check I/Q levels
                if (i === 0 && this.processCallCount > 1125 && this.processCallCount < 1135) {
                    this.port.postMessage({
                        type: 'debug',
                        message: `I/Q Debug: I=${iShifted.toFixed(6)}, Q=${qShifted.toFixed(6)}, tuning=${this.tuningFreq}Hz, count=${this.processCallCount}`
                    });
                }

                // Demodulation
                switch (this.mode) {
                    case 'usb':
                        // TEMPORARY: Just use I channel directly to test
                        audioSample = iShifted * 2.0; // Use frequency-shifted sample

                        // Original USB: I + Hilbert(Q)
                        // const qHilbert = this.hilbertTransform(qSample);
                        // audioSample = iSample + qHilbert;

                        // Debug demodulated audio - ALWAYS log to see if it's zero
                        if (i === 0 && this.processCallCount > 1125 && this.processCallCount < 1135) {
                            this.port.postMessage({
                                type: 'debug',
                                message: `USB Direct I: I=${iSample.toFixed(6)}, Q=${qSample.toFixed(6)}, Audio=${audioSample.toFixed(6)}`
                            });
                        }
                        break;
                    case 'lsb':
                        // LSB: I - Hilbert(Q)
                        const qHilbertLsb = this.hilbertTransform(qSample);
                        audioSample = iSample - qHilbertLsb;
                        break;
                    case 'am':
                    case 'cw':
                        // AM/CW: magnitude
                        audioSample = Math.sqrt(iSample * iSample + qSample * qSample);
                        break;
                    default:
                        audioSample = iSample; // Direct I channel
                }

                // AGC
                audioSample = this.automaticGainControl(audioSample);
            } else {
                // Not enough I/Q samples - output silence
                audioSample = 0;
                // Debug: Log buffer underrun occasionally
                if (i === 0 && this.processCallCount % 20 === 0) {
                    this.port.postMessage({
                        type: 'debug',
                        message: `Buffer underrun: need I/Q sample at ${iqIndex}, but only have ${this.iqBuffer.length} samples`
                    });
                }
            }

            // Output to audio with clipping
            outputChannel[i] = Math.max(-1, Math.min(1, audioSample));

            // Debug: Log audio samples after test tone ends
            if (i === 0 && this.processCallCount > 1125 && this.processCallCount < 1145) {
                this.port.postMessage({
                    type: 'debug',
                    message: `Audio output: raw=${audioSample.toFixed(6)}, clipped=${outputChannel[i].toFixed(6)}, AGC=${this.agcGain.toFixed(3)}`
                });
            }
        }

        // Remove processed I/Q samples from buffer (each audio sample uses 2 I/Q samples)
        const samplesConsumed = blockSize * 2;
        if (this.iqBuffer.length >= samplesConsumed) {
            this.iqBuffer.splice(0, samplesConsumed);
        } else {
            // Clear whatever we have if we don't have enough
            this.iqBuffer.length = 0;
        }

        // Update sample counter for frequency shift timing
        this.sampleCounter += samplesConsumed;

        // Debug: Log buffer state occasionally
        if (this.processCallCount % 50 === 0 || this.processCallCount < 20) {
            this.port.postMessage({
                type: 'debug',
                message: `Audio block complete: consumed ${samplesConsumed} I/Q samples, ${this.iqBuffer.length} remain, call ${this.processCallCount}`
            });
        }
    }

    
    hilbertTransform(sample) {
        // Circular buffer for efficiency
        this.hilbertDelay[this.hilbertIndex] = sample;
        
        let output = 0;
        for (let i = 0; i < this.hilbertTaps.length; i++) {
            const delayIndex = (this.hilbertIndex - i + this.hilbertTaps.length) % this.hilbertTaps.length;
            output += this.hilbertTaps[i] * this.hilbertDelay[delayIndex];
        }
        
        this.hilbertIndex = (this.hilbertIndex + 1) % this.hilbertTaps.length;
        return output;
    }
    
    audioFilter(sample) {
        // Circular buffer for efficiency
        this.audioDelay[this.audioIndex] = sample;
        
        let output = 0;
        for (let i = 0; i < this.audioTaps.length; i++) {
            const delayIndex = (this.audioIndex - i + this.audioTaps.length) % this.audioTaps.length;
            output += this.audioTaps[i] * this.audioDelay[delayIndex];
        }
        
        this.audioIndex = (this.audioIndex + 1) % this.audioTaps.length;
        return output;
    }
    
    automaticGainControl(sample) {
        const amplitude = Math.abs(sample);

        if (amplitude > this.agcTarget) {
            // Much slower attack
            this.agcGain -= 0.00001 * (amplitude - this.agcTarget);
        } else {
            // Much slower decay
            this.agcGain += 0.000001 * (this.agcTarget - amplitude);
        }

        // Allow more gain range
        this.agcGain = Math.max(1.0, Math.min(20.0, this.agcGain));
        return sample * this.agcGain;
    }
    
    generateHilbertFilter(numTaps) {
        const taps = new Float32Array(numTaps);
        const center = Math.floor(numTaps / 2);
        
        for (let i = 0; i < numTaps; i++) {
            if (i !== center) {
                const n = i - center;
                if (n % 2 !== 0) {
                    taps[i] = 2.0 / (Math.PI * n);
                }
            }
        }
        
        // Hamming window
        for (let i = 0; i < numTaps; i++) {
            const window = 0.54 - 0.46 * Math.cos(2 * Math.PI * i / (numTaps - 1));
            taps[i] *= window;
        }
        
        return taps;
    }
    
    generateLowPassFilter(numTaps) {
        // Simple low-pass for audio band (200-3000 Hz)
        const taps = new Float32Array(numTaps);
        const cutoff = 3000 / (this.sampleRate / 2); // Normalized frequency
        const center = Math.floor(numTaps / 2);
        
        for (let i = 0; i < numTaps; i++) {
            const n = i - center;
            if (n === 0) {
                taps[i] = cutoff;
            } else {
                taps[i] = Math.sin(Math.PI * cutoff * n) / (Math.PI * n);
            }
            
            // Hamming window
            const window = 0.54 - 0.46 * Math.cos(2 * Math.PI * i / (numTaps - 1));
            taps[i] *= window;
        }
        
        return taps;
    }
}

registerProcessor('sdr-processor', SdrProcessor);