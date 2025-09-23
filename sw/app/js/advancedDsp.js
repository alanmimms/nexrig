/**
 * Advanced DSP Module for NexRig
 * Handles SSB demodulation, filtering, and audio processing
 */

class AdvancedDsp {
    constructor() {
        this.audioContext = null;
        this.sampleRate = 96000; // I/Q sample rate
        this.audioSampleRate = 48000; // Audio output rate
        this.bufferSize = 1024;
        
        // DSP state
        this.iqBuffer = [];
        this.audioBuffer = [];
        this.decimationRatio = this.sampleRate / this.audioSampleRate; // 2:1
        this.sampleIndex = 0; // Track absolute sample position for phase continuity
        this.nextPlayTime = 0; // Track when to schedule next audio buffer
        
        // Demodulation parameters
        this.mode = 'usb'; // usb, lsb, cw, am
        this.tuningFreq = 1500; // Hz offset from center
        this.bandwidth = 2400; // Hz
        
        // Filter coefficients (simple Hilbert transform approximation)
        this.hilbertTaps = this.generateHilbertFilter(64);
        this.hilbertDelayLine = new Array(this.hilbertTaps.length).fill(0);
        
        // Audio filter (low-pass for audio band)
        this.audioFilterTaps = this.generateLowPassFilter(200, 3000, this.audioSampleRate, 64);
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
                console.log('AudioContext created, state:', this.audioContext.state);
                return true;
            } catch (error) {
                console.error('Failed to create AudioContext:', error);
                return false;
            }
        }
        return true;
    }
    
    processIqData(iqData) {
        if (!this.audioContext || this.audioContext.state !== 'running') {
            // Silently return if AudioContext not ready
            return;
        }
        
        // Check if we're getting valid data
        if (!iqData || !iqData.i || !iqData.q || iqData.i.length === 0) {
            console.warn('DSP: Invalid or empty I/Q data received');
            return;
        }
        
        // Add new I/Q samples to buffer (convert from 24-bit integers to floats)
        for (let i = 0; i < iqData.i.length; i++) {
            this.iqBuffer.push({
                i: iqData.i[i] / 8388607.0,  // Convert 24-bit to -1.0 to +1.0 range
                q: iqData.q[i] / 8388607.0
            });
        }
        
        console.log(`DSP: Received ${iqData.i.length} I/Q samples, buffer size: ${this.iqBuffer.length}, need: ${this.bufferSize * this.decimationRatio}`);
        
        // Process when we have enough samples
        let blocksProcessed = 0;
        while (this.iqBuffer.length >= this.bufferSize * this.decimationRatio) {
            const audioSamples = this.demodulateBlock();
            if (audioSamples.length > 0) {
                this.playAudio(audioSamples);
                blocksProcessed++;
            }
        }
        
        if (blocksProcessed > 0) {
            console.log(`DSP: Processed ${blocksProcessed} audio blocks`);
        }
    }
    
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
            
            // SSB demodulation
            let audioSample = 0;
            
            switch (this.mode) {
                case 'usb':
                    // USB: I + j*Hilbert(Q)
                    const qHilbert = this.hilbertTransform(qShifted);
                    audioSample = iShifted + qHilbert;
                    break;
                    
                case 'lsb':
                    // LSB: I - j*Hilbert(Q)
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
            
            // Always log for debugging
            console.log(`DSP: Playing ${audioSamples.length} samples, max amplitude: ${maxSample.toFixed(4)}`);
            
            // Check if audio is too quiet
            if (maxSample < 0.001) {
                console.warn('DSP: Audio amplitude very low, may not be audible');
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
        console.log('DSP mode set to:', mode);
    }
    
    setTuning(frequency) {
        this.tuningFreq = frequency;
        console.log('DSP tuning set to:', frequency, 'Hz');
    }
    
    setBandwidth(bandwidth) {
        this.bandwidth = bandwidth;
        // Regenerate audio filter with new bandwidth
        this.audioFilterTaps = this.generateLowPassFilter(200, bandwidth, this.audioSampleRate, 64);
        console.log('DSP bandwidth set to:', bandwidth, 'Hz');
    }
}