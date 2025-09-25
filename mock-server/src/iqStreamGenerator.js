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
        type: 'cw_beacon',
        message: 'TEST TEST DE WB7NAB WB7NAB K',
        wpm: 25,
        pauseTime: 2.0,
      },
      {
        frequency: 10000, // Test tone at +10 kHz
        amplitude: 0.03,  // Clean CW carrier level
        phase: 0,
        type: 'cw_beacon',
	message: 'CQ CQ DE TEST',
	wpm: 20,
	pauseTime: 2.0,
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
    // Convert WPM to dit duration (PARIS = 50 dits at given WPM)
    const ditDuration = 1.2 / signal.wpm;
    
    // Calculate position in the message cycle
    const messageDuration = this.calculateMessageDuration(signal.message, ditDuration);
    const totalCycleDuration = messageDuration + signal.pauseTime;
    const cyclePosition = t % totalCycleDuration;
    
    // If we're in the pause between messages, key up
    if (cyclePosition >= messageDuration) {
      return false;
    }
    
    // Find which element we're in
    let elementTime = 0;
    
    for (let charIndex = 0; charIndex < signal.message.length; charIndex++) {
      const char = signal.message[charIndex].toUpperCase();
      
      if (char === ' ') {
	duration += 9 * ditDuration;  // Was 7, now 9 for clearer word breaks
	continue;
      }

      const morse = this.morseCode[char];
      if (!morse) continue;
      
      // Process each dit/dah in the character
      for (let i = 0; i < morse.length; i++) {
	const elementDuration = morse[i] === '.' ? ditDuration : 3 * ditDuration;
	
	// Check if we're in this element
	if (cyclePosition >= elementTime && cyclePosition < elementTime + elementDuration) {
          return true; // Key down
	}
	
	elementTime += elementDuration;
	
	// Inter-element space (1 dit)
	if (i < morse.length - 1) {
          elementTime += ditDuration;
          if (cyclePosition < elementTime) return false;
	}
      }
      
      // Inter-character space (3 dits total, but we already have 1 from inter-element)
      elementTime += 2 * ditDuration;
      if (cyclePosition < elementTime) return false;
    }
    
    return false;
  }

  // Helper method to calculate total message duration
  calculateMessageDuration(message, ditDuration) {
    let duration = 0;
    
    for (let i = 0; i < message.length; i++) {
      const char = message[i].toUpperCase();
      
      if (char === ' ') {
	duration += 7 * ditDuration;
	continue;
      }
      
      const morse = this.morseCode[char];
      if (!morse) continue;
      
      for (let j = 0; j < morse.length; j++) {
	// Element duration
	duration += morse[j] === '.' ? ditDuration : 3 * ditDuration;
	// Inter-element space
	if (j < morse.length - 1) {
          duration += ditDuration;
	}
      }
      
      // Inter-character space with more natural timing
      if (i < message.length - 1) {
	if (message[i + 1] === ' ') {
	  // Already have word space coming, no extra needed
	} else {
	  duration += 4 * ditDuration;  // Was 3, now 4 for better rhythm
	}
      }
    }
    
    return duration;
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
