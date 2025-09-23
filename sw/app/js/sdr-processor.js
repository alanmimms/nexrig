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
        this.tuningFreq = 0; // Hz
        this.mode = 'usb';
        
        // I/Q buffer from WebSocket
        this.iqBuffer = [];
        this.sampleIndex = 0;
        this.tuningPhase = 0; // Phase accumulator for frequency shifting
        
        // Simple 8-tap Hilbert filter for performance
        this.hilbertTaps = this.generateHilbertFilter(8);
        this.hilbertDelay = new Float32Array(8);
        this.hilbertIndex = 0;
        
        // Simple 8-tap audio filter
        this.audioTaps = this.generateLowPassFilter(8);
        this.audioDelay = new Float32Array(8);
        this.audioIndex = 0;
        
        // AGC
        this.agcGain = 1.0;
        this.agcTarget = 0.1;
        
        // Listen for messages from main thread
        this.port.onmessage = (event) => {
            this.handleMessage(event.data);
        };
        
        // Debug counters
        this.processCallCount = 0;
        this.iqDataCount = 0;
        
        // Test tone generator
        this.testTonePhase = 0;
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
                for (let i = 0; i < samples.i.length; i++) {
                    this.iqBuffer.push({
                        i: samples.i[i] / 8388607.0, // 24-bit to float
                        q: samples.q[i] / 8388607.0
                    });
                }
                this.iqDataCount++;
                // Remove console.log from audio thread
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
        
        // Send debug more frequently to monitor buffer
        if (this.processCallCount % 100 === 0) {
            this.port.postMessage({
                type: 'debug',
                processCount: this.processCallCount,
                bufferSize: this.iqBuffer.length
            });
        }
        
        // Process audio samples - consume I/Q data to prevent buildup
        for (let i = 0; i < blockSize; i++) {
            let audioSample = 0;
            
            // Always try to process I/Q data to keep buffer from growing
            if (this.iqBuffer.length >= 2) {
                // Take 2 samples for decimation  
                const iqSample = this.iqBuffer.shift();
                this.iqBuffer.shift(); // Discard second sample for decimation
                
                // Debug: Log first few samples to verify we're getting I/Q data
                if (this.processCallCount <= 10) {
                    this.port.postMessage({
                        type: 'debug',
                        processCount: this.processCallCount,
                        bufferSize: this.iqBuffer.length,
                        message: `Got IQ sample: I=${iqSample.i.toFixed(3)}, Q=${iqSample.q.toFixed(3)}`
                    });
                }
                
                // Increment sample index first to get proper phase progression
                this.sampleIndex++;
                
                // Frequency-selective demodulation using phase accumulator
                // Mix down the tuned frequency to baseband, then demodulate
                const phaseIncrement = 2 * Math.PI * this.tuningFreq / this.iqSampleRate;
                this.tuningPhase += phaseIncrement;
                
                // Keep phase in reasonable range to avoid precision loss
                if (this.tuningPhase > 2 * Math.PI) {
                    this.tuningPhase -= 2 * Math.PI;
                }
                if (this.tuningPhase < -2 * Math.PI) {
                    this.tuningPhase += 2 * Math.PI;
                }
                
                const cosPhase = Math.cos(this.tuningPhase);
                const sinPhase = Math.sin(this.tuningPhase);
                
                // Complex multiply to bring tuned frequency to baseband
                const iBaseband = iqSample.i * cosPhase + iqSample.q * sinPhase;
                const qBaseband = iqSample.q * cosPhase - iqSample.i * sinPhase;
                
                // Temporary: Use magnitude detection to debug baseband tuning
                audioSample = Math.sqrt(iBaseband * iBaseband + qBaseband * qBaseband) * 0.5;
                
                // Debug: Log first few baseband conversions to verify code path
                if (this.processCallCount <= 15 && i === 0) { // Only log first sample of each process call
                    this.port.postMessage({
                        type: 'debug',
                        processCount: this.processCallCount,
                        bufferSize: this.iqBuffer.length,
                        message: `Phase Debug: Tune=${this.tuningFreq}Hz, sampleIdx=${this.sampleIndex}, phaseInc=${phaseIncrement.toFixed(6)}, phase=${this.tuningPhase.toFixed(6)}, cos=${cosPhase.toFixed(6)}, sin=${sinPhase.toFixed(6)}`
                    });
                }
                
            } else {
                // Generate test tone when no I/Q data available
                audioSample = 0.05 * Math.sin(this.testTonePhase);
                this.testTonePhase += 2 * Math.PI * 1000 / this.sampleRate;
            }
            
            // Output to audio with clipping
            outputChannel[i] = Math.max(-1, Math.min(1, audioSample));
        }
        
        // Aggressively consume any excess I/Q samples to prevent buffer growth
        while (this.iqBuffer.length > 1000) {
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