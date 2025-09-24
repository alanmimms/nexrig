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

        // AGC
        this.agcGain = 1.0;
        this.agcTarget = 0.1;

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

        // AUDIO RE-ENABLED - Testing for horizontal bars with original signal processing
        // Fractional resampler for stable decimation
        for (let i = 0; i < blockSize; i++) {
            let audioSample = 0;

            // Calculate required I/Q sample index for this audio sample
            const requiredIqIndex = Math.floor(this.resamplerPhase);

            // Check if we have enough I/Q samples
            if (this.iqBuffer.length > requiredIqIndex + 1) {
                // Linear interpolation between two I/Q samples
                const iq1 = this.iqBuffer[requiredIqIndex];
                const iq2 = this.iqBuffer[requiredIqIndex + 1];
                const frac = this.resamplerPhase - requiredIqIndex;

                const iSample = iq1.i + frac * (iq2.i - iq1.i);
                const qSample = iq1.q + frac * (iq2.q - iq1.q);

                // Demodulation
                switch (this.mode) {
                    case 'usb':
                        // USB: I + Hilbert(Q)
                        const qHilbert = this.hilbertTransform(qSample);
                        audioSample = iSample + qHilbert;
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
                // No I/Q data - track underrun
                audioSample = 0;
            }

            // Advance resampler phase
            this.resamplerPhase += this.resamplerRate;

            // Output to audio with clipping
            outputChannel[i] = Math.max(-1, Math.min(1, audioSample));
        }

        // Remove consumed I/Q samples from buffer
        const samplesConsumed = Math.floor(this.resamplerPhase);
        if (samplesConsumed > 0 && this.iqBuffer.length >= samplesConsumed) {
            this.iqBuffer.splice(0, samplesConsumed);
            this.resamplerPhase -= samplesConsumed;
        }

        // Report buffer status for waterfall debugging
        if (this.processCallCount % 50 === 0) {
            this.port.postMessage({
                type: 'debug',
                message: `AUDIO DISABLED - Waterfall Debug Mode: ${this.iqBuffer.length} I/Q samples in buffer`
            });
        }
        
        // Keep buffer size reasonable but don't throw away too much data
        // Only trim if we have way too much buffered (more than 1 second at 96kHz)
        while (this.iqBuffer.length > 96000) {
            this.iqBuffer.shift();
        }
        
        return true; // Keep processor alive
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
            this.agcGain -= 0.001 * (amplitude - this.agcTarget);
        } else {
            this.agcGain += 0.0001 * (this.agcTarget - amplitude);
        }
        
        this.agcGain = Math.max(0.1, Math.min(10.0, this.agcGain));
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