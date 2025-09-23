/**
 * I/Q Stream Generator
 * Generates mock I/Q data simulating various RF signals
 */

export class IqStreamGenerator {
    constructor() {
        this.sampleRate = 96000; // 96 kS/s
        this.phase = 0;
        this.time = 0;
        
        // Signal sources for simulation
        this.signals = [
            {
                frequency: 1500,  // 1.5 kHz USB signal
                amplitude: 0.4,
                phase: 0,
                type: 'usb_two_tone',
                tone1: 700,    // 700 Hz audio tone (standard)
                tone2: 1900    // 1900 Hz audio tone (standard)
            },
            {
                frequency: -3000, // 3 kHz LSB signal
                amplitude: 0.2,
                phase: 0,
                type: 'lsb',
                modulation: 1000  // 1 kHz audio
            },
            {
                frequency: 8000,  // 8 kHz CW signal
                amplitude: 0.3,
                phase: 0,
                type: 'cw'
            }
        ];
    }
    
    generateIqSamples(numSamples) {
        // Use regular arrays that will serialize properly
        const iArray = [];
        const qArray = [];
        const samples = {
            i: iArray,
            q: qArray,
            timestamp: Date.now()
        };
        
        const dt = 1.0 / this.sampleRate;
        
        for (let n = 0; n < numSamples; n++) {
            let iSample = 0;
            let qSample = 0;
            
            // Add noise floor
            iSample += (Math.random() - 0.5) * 0.01;
            qSample += (Math.random() - 0.5) * 0.01;
            
            // Add each signal
            for (const signal of this.signals) {
                const t = this.time + n * dt;
                const omega = 2 * Math.PI * signal.frequency;
                
                switch (signal.type) {
                    case 'cw':
                        // Pure carrier (CW signal)
                        iSample += signal.amplitude * Math.cos(omega * t + signal.phase);
                        qSample += signal.amplitude * Math.sin(omega * t + signal.phase);
                        break;
                        
                    case 'usb_two_tone':
                        // USB two-tone signal: carrier + audio tones
                        // For USB: I = cos(wc*t) * cos(wa*t), Q = sin(wc*t) * cos(wa*t)
                        const audio1 = Math.cos(2 * Math.PI * signal.tone1 * t);
                        const audio2 = Math.cos(2 * Math.PI * signal.tone2 * t);
                        const audioSum = 0.5 * (audio1 + audio2); // Two-tone test signal
                        
                        // Generate USB signal (audio shifted up by carrier frequency)
                        iSample += signal.amplitude * audioSum * Math.cos(omega * t + signal.phase);
                        qSample += signal.amplitude * audioSum * Math.sin(omega * t + signal.phase);
                        break;
                        
                    case 'lsb':
                        // LSB signal with single tone
                        const lsbAudio = Math.cos(2 * Math.PI * signal.modulation * t);
                        // For LSB: I = cos(wc*t) * cos(wa*t), Q = -sin(wc*t) * cos(wa*t)
                        iSample += signal.amplitude * lsbAudio * Math.cos(omega * t + signal.phase);
                        qSample += signal.amplitude * lsbAudio * (-Math.sin(omega * t + signal.phase));
                        break;
                        
                    case 'noise':
                        // Band-limited noise
                        const noise = (Math.random() - 0.5) * signal.amplitude;
                        iSample += noise * Math.cos(omega * t);
                        qSample += noise * Math.sin(omega * t);
                        break;
                }
                
                // Slowly drift the phase for realism
                signal.phase += 0.00001;
            }
            
            // Apply AGC-like scaling and convert to 24-bit range
            const scale = 0.8;
            const scaledI = Math.max(-1, Math.min(1, iSample * scale));
            const scaledQ = Math.max(-1, Math.min(1, qSample * scale));
            
            // Convert to 24-bit signed integer range (-8388608 to 8388607)
            iArray.push(Math.round(scaledI * 8388607));
            qArray.push(Math.round(scaledQ * 8388607));
        }
        
        this.time += numSamples * dt;
        
        // Occasionally add a strong signal (simulate QSO)
        if (Math.random() < 0.001) {
            this.addRandomSignal();
        }
        
        return samples;
    }
    
    addRandomSignal() {
        // Add a temporary strong signal to simulate activity
        const newSignal = {
            frequency: (Math.random() - 0.5) * 40000, // +/- 20 kHz
            amplitude: 0.3 + Math.random() * 0.4,
            phase: Math.random() * 2 * Math.PI,
            type: Math.random() < 0.5 ? 'cw' : 'ssb',
            modulation: 200 + Math.random() * 400,
            lifetime: 5 + Math.random() * 10  // seconds
        };
        
        this.signals.push(newSignal);
        
        // Remove after lifetime
        setTimeout(() => {
            const index = this.signals.indexOf(newSignal);
            if (index > -1) {
                this.signals.splice(index, 1);
            }
        }, newSignal.lifetime * 1000);
        
        console.log(`Added signal at ${newSignal.frequency.toFixed(0)} Hz`);
    }
    
    setNoiseLevel(level) {
        // Adjust noise floor (0-1)
        this.noiseLevel = Math.max(0, Math.min(1, level));
    }
    
    clearSignals() {
        // Keep only the first few permanent signals
        this.signals = this.signals.slice(0, 3);
    }
}