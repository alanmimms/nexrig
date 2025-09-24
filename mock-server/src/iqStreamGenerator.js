/**
 * I/Q Stream Generator
 * Generates mock I/Q data simulating various RF signals
 */

export class IqStreamGenerator {
    constructor() {
        this.sampleRate = 96000; // 96 kS/s
        this.phase = 0;
        this.time = 0;
        
        // Signal sources for baseband simulation (±48kHz range)
        this.signals = [
            {
                frequency: 0,     // 0 Hz - USB signal at baseband center
                amplitude: 0.02,  // Much weaker to prevent splatter
                phase: 0,
                type: 'usb_two_tone',
                tone1: 700,    // 700 Hz audio tone
                tone2: 1900    // 1900 Hz audio tone
            },
            {
                frequency: 25000, // +25 kHz - CW beacon in baseband
                amplitude: 0.05,  // Clean CW carrier level
                phase: 0,
                type: 'cw',      // Changed to pure carrier for testing
                message: 'TEST TEST DE WB7NAB WB7NAB K',
                wpm: 25,
                pauseTime: 2.0
            },
            {
                frequency: 10000, // Test tone at +10 kHz
                amplitude: 0.03,  // Clean CW carrier level
                phase: 0,
                type: 'cw'        // Pure carrier for testing
            }
        ];
        
        // CW timing and state  
        this.cwBeaconState = {
            messageIndex: 0,
            elementIndex: 0,
            keyDown: false,
            elementStartTime: 0,
            pauseStartTime: 0,
            inPause: false,
            inMessagePause: false,
            ditLength: 1.2 / 25,  // WPM to dit length in seconds (PARIS standard)
            initialized: false,
            lastTime: 0
        };
        
        // Morse code table
        this.morseCode = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', ' ': ' ', '/': '-..-.'
        };
        
        // FFT debugging state
        this.lastFftTime = -1;
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
            // DEBUGGING: Generate pure zeros to isolate waterfall rendering issues
            let iSample = 0;
            let qSample = 0;

            // NOISE REMOVED: All noise should come from mock server signal generation only
            // No artificial noise floor added here

            // DEBUG: Log signal processing on first sample
            if (n === 0) {
                console.log(`DEBUG: Processing ${this.signals.length} signals, time=${this.time.toFixed(6)}`);
            }

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

                    case 'cw_beacon':
                        // CW beacon with Morse code
                        const keyDown = this.updateCwBeacon(t, signal);
                        if (keyDown) {
                            const cwI = signal.amplitude * Math.cos(omega * t + signal.phase);
                            const cwQ = signal.amplitude * Math.sin(omega * t + signal.phase);
                            iSample += cwI;
                            qSample += cwQ;

                            // Debug: Log CW contribution occasionally
                            if (n === 0 && Math.random() < 0.01) {
                                console.log(`CW: f=${signal.frequency}Hz, amp=${signal.amplitude}, I=${cwI.toFixed(4)}, Q=${cwQ.toFixed(4)}`);
                            }
                        }
                        break;

                    case 'usb_two_tone':
                        // USB two-tone signal at baseband (direct conversion receiver tuned to carrier)
                        // For USB at baseband: generate analytic signal
                        // I = cos(audio_freq*t), Q = sin(audio_freq*t)
                        const audio1_i = Math.cos(2 * Math.PI * signal.tone1 * t);
                        const audio1_q = Math.sin(2 * Math.PI * signal.tone1 * t);
                        const audio2_i = Math.cos(2 * Math.PI * signal.tone2 * t);
                        const audio2_q = Math.sin(2 * Math.PI * signal.tone2 * t);

                        // Sum the two tones to create two-tone test signal
                        iSample += signal.amplitude * 0.5 * (audio1_i + audio2_i);
                        qSample += signal.amplitude * 0.5 * (audio1_q + audio2_q);
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

                // Removed phase drift - was causing issues
                // signal.phase += 0.00001;
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
        
        return samples;
    }
    
    updateCwBeacon(t, signal) {
        // Continuous carrier - always key down for debugging
        return true;
        
        // Handle message pause (2 seconds between complete messages)
        if (state.inMessagePause) {
            if (t - state.pauseStartTime >= signal.pauseTime) {
                console.log('CW: Message pause ended, restarting');
                state.inMessagePause = false;
                state.messageIndex = 0;
                state.elementIndex = 0;
            }
            return false;
        }
        
        // Check if we've completed the message
        if (state.messageIndex >= signal.message.length) {
            if (!state.inMessagePause) {
                state.inMessagePause = true;
                state.pauseStartTime = t;
            }
            return false;
        }
        
        const currentChar = signal.message[state.messageIndex].toUpperCase();
        const morsePattern = this.morseCode[currentChar];
        
        // Handle spaces (7 dit periods)
        if (currentChar === ' ') {
            if (!state.inPause) {
                state.inPause = true;
                state.pauseStartTime = t;
            }
            if (t - state.pauseStartTime >= 7 * state.ditLength) {
                state.inPause = false;
                state.messageIndex++;
                state.elementIndex = 0;
            }
            return false;
        }
        
        // Skip unknown characters
        if (!morsePattern) {
            state.messageIndex++;
            return false;
        }
        
        // Handle inter-element pause (1 dit period between dots/dashes)
        if (state.inPause) {
            if (t - state.pauseStartTime >= state.ditLength) {
                state.inPause = false;
            }
            return false;
        }
        
        // Check if we've completed this character
        if (state.elementIndex >= morsePattern.length) {
            // Inter-character pause (3 dit periods)
            if (!state.inPause) {
                state.inPause = true;
                state.pauseStartTime = t;
            }
            if (t - state.pauseStartTime >= 3 * state.ditLength) {
                state.inPause = false;
                state.messageIndex++;
                state.elementIndex = 0;
            }
            return false;
        }
        
        const currentElement = morsePattern[state.elementIndex];
        const elementDuration = currentElement === '.' ? state.ditLength : 3 * state.ditLength; // Dah = 3 dits
        
        // Start new element
        if (!state.keyDown) {
            state.keyDown = true;
            state.elementStartTime = t;
        }
        
        // Check if element is complete
        if (t - state.elementStartTime >= elementDuration) {
            state.keyDown = false;
            state.elementIndex++;
            
            // Add inter-element pause if not at end of character
            if (state.elementIndex < morsePattern.length) {
                state.inPause = true;
                state.pauseStartTime = t;
            }
        }
        
        return state.keyDown;
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