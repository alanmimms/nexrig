/**
 * Advanced DSP Module for NexRig
 * Handles SSB demodulation, filtering, and audio processing
 */

class AdvancedDsp {
    constructor() {
        this.audioContext = null;
        this.sampleRate = 96000; // I/Q sample rate
        this.audioSampleRate = 48000; // Audio output rate
        this.bufferSize = 256; // Balanced latency vs performance (~5.3ms at 48kHz)
        
        // DSP state
        this.iqBuffer = [];
        this.audioBuffer = [];
        this.decimationRatio = this.sampleRate / this.audioSampleRate; // 2:1
        this.sampleIndex = 0; // Track absolute sample position for phase continuity
        this.nextPlayTime = 0; // Track when to schedule next audio buffer
        
        // Demodulation parameters
        this.mode = 'usb'; // usb, lsb, cw, am
        this.tuningFreq = 0; // Hz offset from center
        this.bandwidth = 2400; // Hz
        
        // Filter coefficients (simple Hilbert transform approximation) - reduced for performance
        this.hilbertTaps = this.generateHilbertFilter(16);
        this.hilbertDelayLine = new Array(this.hilbertTaps.length).fill(0);
        
        // Audio filter (low-pass for audio band) - reduced for performance
        this.audioFilterTaps = this.generateLowPassFilter(200, 3000, this.audioSampleRate, 16);
        this.audioDelayLine = new Array(this.audioFilterTaps.length).fill(0);
        
        // AGC
        this.agcGain = 1.0;
        this.agcTarget = 0.1;
        this.agcAttack = 0.001;
        this.agcDecay = 0.0001;
    }
    
    async initialize() {
        try {
            // Don't create AudioContext yet - wait for user gesture
            console.log('DSP initialized, AudioContext will be created on user gesture');
            return true;
        } catch (error) {
            console.error('Failed to initialize DSP:', error);
            return false;
        }
    }
    
    async createAudioContext() {
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: this.audioSampleRate
                });
                
                // Load and initialize AudioWorklet processor
                try {
                    await this.audioContext.audioWorklet.addModule('./js/sdr-processor.js?v=' + Date.now());
                    console.log('AudioWorklet module loaded successfully');
                    
                    this.workletNode = new AudioWorkletNode(this.audioContext, 'sdr-processor', {
                        numberOfInputs: 0,
                        numberOfOutputs: 1,
                        outputChannelCount: [1]
                    });
                    this.workletNode.connect(this.audioContext.destination);
                    console.log('AudioWorkletNode created and connected');
                    
                    // Listen for messages from AudioWorklet
                    this.workletNode.port.onmessage = (event) => {
                        if (event.data.type === 'debug') {
                            if (event.data.message) {
                                console.log(`AudioWorklet: ${event.data.message} (call ${event.data.processCount}, buffer: ${event.data.bufferSize})`);
                            } else {
                                console.log(`AudioWorklet: Process called ${event.data.processCount} times, buffer: ${event.data.bufferSize}`);
                            }
                        } else if (event.data.type === 'testResponse') {
                            console.log(event.data.message);
                        }
                    };
                    
                    // Test message to worklet
                    this.workletNode.port.postMessage({
                        type: 'test',
                        message: 'Hello from main thread'
                    });
                    
                } catch (error) {
                    console.error('Failed to load AudioWorklet:', error);
                    throw error;
                }
                
                console.log('AudioContext and SDR Worklet created, state:', this.audioContext.state);
                return true;
            } catch (error) {
                console.error('Failed to create AudioContext or Worklet:', error);
                return false;
            }
        }
        return true;
    }
    
    processIqData(iqData) {
        if (!this.audioContext || this.audioContext.state !== 'running' || !this.workletNode) {
            // Silently return if AudioContext not ready
            return;
        }
        
        // Check if we're getting valid data
        if (!iqData || !iqData.i || !iqData.q || iqData.i.length === 0) {
            console.warn('DSP: Invalid or empty I/Q data received');
            return;
        }
        
        // Send I/Q data to AudioWorklet processor
        this.workletNode.port.postMessage({
            type: 'iqData',
            samples: {
                i: iqData.i,
                q: iqData.q
            }
        });
        
        // Removed debug logging for performance
    }
    
    // Old DSP methods removed - now handled by AudioWorklet
    
    demodulateBlock() {
        const blockSize = this.bufferSize * this.decimationRatio;
        const iqBlock = this.iqBuffer.splice(0, blockSize);
        const audioSamples = [];
        
        for (let i = 0; i < iqBlock.length; i += this.decimationRatio) {
            // Get I/Q sample
            const iSample = iqBlock[i].i;
            const qSample = iqBlock[i].q;
            
            // Frequency shift to tune the desired signal to baseband
            // Use absolute sample index for phase continuity
            const tuningPhase = 2 * Math.PI * this.tuningFreq * this.sampleIndex / this.sampleRate;
            const cosPhase = Math.cos(tuningPhase);
            const sinPhase = Math.sin(tuningPhase);
            
            // Increment sample index for next sample
            this.sampleIndex += this.decimationRatio;
            
            // Complex multiply to shift frequency
            const iShifted = iSample * cosPhase + qSample * sinPhase;
            const qShifted = qSample * cosPhase - iSample * sinPhase;
            
            // Debug: Log input and output levels occasionally for CW detection
            if (Math.random() < 0.001 && (Math.abs(iSample) > 0.05 || Math.abs(qSample) > 0.05)) {
                console.log(`DSP Debug: Input I=${iSample.toFixed(3)}, Q=${qSample.toFixed(3)}, Tuning=${this.tuningFreq}Hz, Output I=${iShifted.toFixed(3)}, Q=${qShifted.toFixed(3)}`);
            }
            
            // Special debug for CW frequency range (24-26 kHz tuning)
            if (Math.random() < 0.001 && this.tuningFreq > 24000 && this.tuningFreq < 26000) {
                const inputMagnitude = Math.sqrt(iSample*iSample + qSample*qSample);
                if (inputMagnitude > 0.05) {
                    console.log(`DSP CW Debug: Tuning=${this.tuningFreq}Hz, Input mag=${inputMagnitude.toFixed(3)}, I=${iSample.toFixed(3)}, Q=${qSample.toFixed(3)}, Mode=${this.mode}`);
                }
            }
            
            // SSB demodulation
            let audioSample = 0;
            
            switch (this.mode) {
                case 'usb':
                    // USB: I + Hilbert(Q) - proper SSB demodulation
                    const qHilbert = this.hilbertTransform(qShifted);
                    audioSample = iShifted + qHilbert;
                    
                    // Debug: Occasionally log the demodulation components
                    if (Math.random() < 0.001 && Math.abs(iShifted) > 0.01) {
                        console.log(`USB Demod: I=${iShifted.toFixed(3)}, Hilbert(Q)=${qHilbert.toFixed(3)}, Audio=${audioSample.toFixed(3)}, Tuning=${this.tuningFreq}Hz`);
                    }
                    break;
                    
                case 'lsb':
                    // LSB: I - Hilbert(Q) - proper SSB demodulation
                    const qHilbertLsb = this.hilbertTransform(qShifted);
                    audioSample = iShifted - qHilbertLsb;
                    break;
                    
                case 'cw':
                case 'am':
                    // Envelope detection for AM/CW
                    audioSample = Math.sqrt(iShifted * iShifted + qShifted * qShifted);
                    break;
            }
            
            // Audio band filtering
            audioSample = this.audioFilter(audioSample);
            
            // AGC
            audioSample = this.automaticGainControl(audioSample);
            
            audioSamples.push(audioSample);
        }
        
        return audioSamples;
    }
    
    hilbertTransform(sample) {
        // Shift delay line
        for (let i = this.hilbertDelayLine.length - 1; i > 0; i--) {
            this.hilbertDelayLine[i] = this.hilbertDelayLine[i - 1];
        }
        this.hilbertDelayLine[0] = sample;
        
        // Convolution with Hilbert filter
        let output = 0;
        for (let i = 0; i < this.hilbertTaps.length; i++) {
            output += this.hilbertTaps[i] * this.hilbertDelayLine[i];
        }
        
        return output;
    }
    
    audioFilter(sample) {
        // Shift delay line
        for (let i = this.audioDelayLine.length - 1; i > 0; i--) {
            this.audioDelayLine[i] = this.audioDelayLine[i - 1];
        }
        this.audioDelayLine[0] = sample;
        
        // Convolution with audio filter
        let output = 0;
        for (let i = 0; i < this.audioFilterTaps.length; i++) {
            output += this.audioFilterTaps[i] * this.audioDelayLine[i];
        }
        
        return output;
    }
    
    automaticGainControl(sample) {
        const amplitude = Math.abs(sample);
        
        // Update AGC gain
        if (amplitude > this.agcTarget) {
            this.agcGain -= this.agcAttack * (amplitude - this.agcTarget);
        } else {
            this.agcGain += this.agcDecay * (this.agcTarget - amplitude);
        }
        
        // Limit gain
        this.agcGain = Math.max(0.1, Math.min(10.0, this.agcGain));
        
        return sample * this.agcGain;
    }
    
    playAudio(audioSamples) {
        if (!this.audioContext || audioSamples.length === 0) return;
        
        try {
            // Create audio buffer
            const buffer = this.audioContext.createBuffer(1, audioSamples.length, this.audioSampleRate);
            const channelData = buffer.getChannelData(0);
            
            // Copy samples to audio buffer and check audio levels
            let maxSample = 0;
            for (let i = 0; i < audioSamples.length; i++) {
                const clampedSample = Math.max(-1, Math.min(1, audioSamples[i]));
                channelData[i] = clampedSample;
                maxSample = Math.max(maxSample, Math.abs(clampedSample));
            }
            
            // Log occasionally for monitoring
            if (Math.random() < 0.001) {
                console.log(`DSP: Audio level: ${maxSample.toFixed(4)}, Tuning: ${this.tuningFreq}Hz`);
            }
            
            // Special logging for CW tuning range
            if (Math.random() < 0.01 && this.tuningFreq > 24000 && this.tuningFreq < 26000 && maxSample > 0.001) {
                console.log(`DSP CW Audio Output: Level=${maxSample.toFixed(4)}, Tuning=${this.tuningFreq}Hz, Samples=${audioSamples.length}`);
            }
            
            // Debug all audio output when tuned to any significant frequency
            if (Math.random() < 0.005 && this.tuningFreq > 20000 && this.tuningFreq < 30000) {
                console.log(`DSP Audio Check: MaxLevel=${maxSample.toFixed(4)}, Tuning=${this.tuningFreq}Hz`);
            }
            
            // Schedule audio playback for seamless output
            const source = this.audioContext.createBufferSource();
            source.buffer = buffer;
            source.connect(this.audioContext.destination);
            
            // Schedule at the next play time for seamless audio
            const currentTime = this.audioContext.currentTime;
            if (this.nextPlayTime < currentTime) {
                // First buffer or we're behind - start immediately
                this.nextPlayTime = currentTime;
            }
            
            source.start(this.nextPlayTime);
            
            // Calculate when the next buffer should start
            const bufferDuration = audioSamples.length / this.audioSampleRate;
            this.nextPlayTime += bufferDuration;
            
        } catch (error) {
            console.error('Audio playback error:', error);
        }
    }
    
    generateHilbertFilter(numTaps) {
        // Simple Hilbert transform filter (90-degree phase shift)
        const taps = new Array(numTaps).fill(0);
        const center = Math.floor(numTaps / 2);
        
        for (let i = 0; i < numTaps; i++) {
            if (i !== center) {
                const n = i - center;
                if (n % 2 !== 0) {
                    taps[i] = 2.0 / (Math.PI * n);
                }
            }
        }
        
        // Apply window function (Hamming)
        for (let i = 0; i < numTaps; i++) {
            const window = 0.54 - 0.46 * Math.cos(2 * Math.PI * i / (numTaps - 1));
            taps[i] *= window;
        }
        
        return taps;
    }
    
    generateLowPassFilter(lowFreq, highFreq, sampleRate, numTaps) {
        // Bandpass filter for audio frequencies
        const taps = new Array(numTaps).fill(0);
        const center = Math.floor(numTaps / 2);
        const nyquist = sampleRate / 2;
        
        const normalizedLow = lowFreq / nyquist;
        const normalizedHigh = highFreq / nyquist;
        
        for (let i = 0; i < numTaps; i++) {
            const n = i - center;
            if (n === 0) {
                taps[i] = normalizedHigh - normalizedLow;
            } else {
                taps[i] = (Math.sin(Math.PI * normalizedHigh * n) - 
                          Math.sin(Math.PI * normalizedLow * n)) / (Math.PI * n);
            }
            
            // Apply Hamming window
            const window = 0.54 - 0.46 * Math.cos(2 * Math.PI * i / (numTaps - 1));
            taps[i] *= window;
        }
        
        return taps;
    }
    
    setMode(mode) {
        this.mode = mode;
        if (this.workletNode) {
            this.workletNode.port.postMessage({
                type: 'setMode',
                mode: mode
            });
        }
        console.log('DSP mode set to:', mode);
    }
    
    setTuning(frequency) {
        this.tuningFreq = frequency;
        if (this.workletNode) {
            this.workletNode.port.postMessage({
                type: 'setTuning',
                frequency: frequency
            });
        }
        console.log('DSP tuning set to:', frequency, 'Hz');
    }
    
    setBandwidth(bandwidth) {
        this.bandwidth = bandwidth;
        // Regenerate audio filter with new bandwidth
        this.audioFilterTaps = this.generateLowPassFilter(200, bandwidth, this.audioSampleRate, 16);
        console.log('DSP bandwidth set to:', bandwidth, 'Hz');
    }
}