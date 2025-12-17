class TxProcessor {

  constructor(sampleRate = 48000) {
    this.sampleRate = sampleRate;
    this.modRate = 4000; // Max modulation bandwidth
    
    // For SSB generation
    this.hilbertLength = 129; // FIR filter taps
    this.hilbertFilter = this.designHilbert(this.hilbertLength);
    
    // CW shaping
    this.cwRiseTime = 0.005; // 5ms default
    this.cwSpeed = 25; // WPM
    
    // Audio processing
    this.compressor = new AudioCompressor();
    this.alc = new AutoLevelControl();
  }
  
  processSsbAudio(audioSamples, mode = 'usb') {
    // Generate I/Q from audio using Hilbert transform
    const I = audioSamples;
    const Q = this.hilbertTransform(audioSamples);
    
    // For LSB, negate Q
    if (mode === 'lsb') {
      Q = Q.map(v => -v);
    }
    
    // Convert I/Q to amplitude/phase
    return this.iqToPolar(I, Q);
  }
  
  processAmAudio(audioSamples, modDepth = 0.9) {
    // AM: amplitude varies with audio, phase is constant
    const amplitude = audioSamples.map(sample => {
      return (1 + modDepth * sample); // Carrier + modulation
    });
    
    const phase = new Float32Array(audioSamples.length); // Zero phase
    
    return { amplitude, phase };
  }
  
  processCw(keyingState, sampleCount) {
    // CW: constant amplitude when keyed, shaped envelope
    const amplitude = new Float32Array(sampleCount);
    const phase = new Float32Array(sampleCount); // Zero phase
    
    // Apply rise/fall shaping to prevent key clicks
    for (let i = 0; i < sampleCount; i++) {
      amplitude[i] = this.shapeCwEnvelope(keyingState, i);
    }
    
    return { amplitude, phase };
  }
  
  iqToPolar(I, Q) {
    const amplitude = new Float32Array(I.length);
    const phase = new Float32Array(I.length);
    
    for (let i = 0; i < I.length; i++) {
      amplitude[i] = Math.sqrt(I[i] * I[i] + Q[i] * Q[i]);
      phase[i] = Math.atan2(Q[i], I[i]);
    }
    
    return { amplitude, phase };
  }
  
  // Quantize for hardware transmission
  quantizeForHardware(amplitude, phase) {
    // Amplitude: 12-bit DAC for Vdd control (0-4095)
    const ampQuantized = amplitude.map(a => {
      const scaled = Math.max(0, Math.min(1, a));
      return Math.round(scaled * 4095);
    });
    
    // Phase: 16-bit for NCO (0-65535 = 0-2π)
    const phaseQuantized = phase.map(p => {
      // Normalize phase to [0, 2π]
      let normalized = p;
      while (normalized < 0) normalized += 2 * Math.PI;
      while (normalized >= 2 * Math.PI) normalized -= 2 * Math.PI;
      
      return Math.round((normalized / (2 * Math.PI)) * 65535);
    });
    
    return { amplitude: ampQuantized, phase: phaseQuantized };
  }
}
