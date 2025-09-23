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
                frequency: 1000,  // 1 kHz offset from center
                amplitude: 0.5,
                phase: 0,
                type: 'cw'
            },
            {
                frequency: -2500, // 2.5 kHz below center
                amplitude: 0.3,
                phase: 0,
                type: 'ssb',
                modulation: 300  // 300 Hz modulation
            },
            {
                frequency: 5000,  // 5 kHz above center
                amplitude: 0.2,
                phase: 0,
                type: 'noise'
            }
        ];
    }
    
    generateIqSamples(numSamples) {
        const samples = {
            i: new Float32Array(numSamples),
            q: new Float32Array(numSamples),
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
                        
                    case 'ssb':
                        // SSB signal with modulation
                        const modOmega = 2 * Math.PI * signal.modulation;
                        const modulation = 1 + 0.8 * Math.sin(modOmega * t);
                        iSample += signal.amplitude * modulation * Math.cos(omega * t + signal.phase);
                        qSample += signal.amplitude * modulation * Math.sin(omega * t + signal.phase);
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
            
            // Apply AGC-like scaling and clipping
            const scale = 0.8;
            samples.i[n] = Math.max(-1, Math.min(1, iSample * scale));
            samples.q[n] = Math.max(-1, Math.min(1, qSample * scale));
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