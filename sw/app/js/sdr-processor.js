class SdrProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    // DSP parameters
    this.sampleRate = 48000;
    this.iqSampleRate = 96000;
    this.decimationRatio = 2;
    this.tuningFreq = 0; // Hz
    this.mode = 'usb';
    this.cwMode = 'usb'; // Which SSB mode to use for CW

    // Filter parameters for each mode
    this.filterParams = {
      usb: { low: 200, high: 3500 },
      lsb: { low: -3500, high: -200 },
      cw: { low: 200, high: 700 },  // 500Hz filter for CW in USB mode (200-700 Hz)
      am: { low: -4000, high: 4000 }
    };

    // I/Q buffer
    this.iqBuffer = [];
    this.sampleCounter = 0;

    // Hilbert transform for SSB demodulation
    this.hilbertTaps = this.generateHilbertFilter(16);
    this.hilbertDelay = new Float32Array(16);
    this.hilbertIndex = 0;

    // Complex bandpass filter state
    this.bandpassTaps = null;
    this.bandpassDelayI = null;
    this.bandpassDelayQ = null;
    this.updateBandpassFilter();

    // AGC
    this.agcGain = 3.0;
    this.agcTarget = 0.3;

    // Listen for messages
    this.port.onmessage = (event) => {
      this.handleMessage(event.data);
    };

    // Debug counters
    this.processCallCount = 0;
    this.iqDataCount = 0;
    this.underrunCount = 0;
  }

  handleMessage(data) {
    switch (data.type) {
      case 'iqData':
        const samples = data.samples;
        if (samples && samples.i && samples.q) {
          for (let i = 0; i < samples.i.length; i++) {
            this.iqBuffer.push({
              i: samples.i[i] / 8388607.0,
              q: samples.q[i] / 8388607.0
            });
          }
          this.iqDataCount++;
        }
        break;

      case 'setTuning':
        this.tuningFreq = data.frequency;
        this.port.postMessage({
          type: 'debug',
          message: `Tuning changed to: ${this.tuningFreq}Hz`
        });
        break;

      case 'setMode':
        this.mode = data.mode;
        this.updateBandpassFilter();
        this.port.postMessage({
          type: 'debug',
          message: `Mode changed to: ${this.mode}, filter reconfigured`
        });
        break;

      case 'setCwMode':
        // Allow setting whether CW uses USB or LSB demodulation
        this.cwMode = data.cwMode || 'usb';
        if (this.mode === 'cw') {
          this.updateBandpassFilter();
        }
        break;
    }
  }

  updateBandpassFilter() {
    let lowFreq, highFreq;
    
    if (this.mode === 'cw') {
      // CW uses narrow filter with USB or LSB demodulation
      if (this.cwMode === 'lsb') {
        // For LSB CW, mirror the filter
        lowFreq = -700;
        highFreq = -200;
      } else {
        // Default USB CW
        lowFreq = 200;
        highFreq = 700;
      }
    } else {
      // Normal mode filters
      const params = this.filterParams[this.mode];
      lowFreq = params.low;
      highFreq = params.high;
    }
    
    // Generate complex bandpass filter
    const filterOrder = 64;
    this.bandpassTaps = this.generateBandpassFilter(
      lowFreq,
      highFreq,
      this.sampleRate,
      filterOrder
    );
    
    // Separate delay lines for I and Q
    this.bandpassDelayI = new Float32Array(filterOrder);
    this.bandpassDelayQ = new Float32Array(filterOrder);
    
    this.port.postMessage({
      type: 'debug',
      message: `${this.mode.toUpperCase()} filter: ${lowFreq}Hz to ${highFreq}Hz`
    });
  }

  generateBandpassFilter(lowFreq, highFreq, sampleRate, numTaps) {
    const taps = new Float32Array(numTaps);
    const center = Math.floor(numTaps / 2);
    
    // Normalize frequencies
    const wl = (2 * Math.PI * lowFreq) / sampleRate;
    const wh = (2 * Math.PI * highFreq) / sampleRate;
    
    for (let i = 0; i < numTaps; i++) {
      const n = i - center;
      
      if (n === 0) {
        taps[i] = (wh - wl) / Math.PI;
      } else {
        const highpass = Math.sin(wh * n) / (Math.PI * n);
        const lowpass = Math.sin(wl * n) / (Math.PI * n);
        taps[i] = highpass - lowpass;
      }
      
      // Apply Blackman window for better stopband
      const a0 = 0.42;
      const a1 = 0.5;
      const a2 = 0.08;
      const window = a0 - a1 * Math.cos(2 * Math.PI * i / (numTaps - 1)) 
                        + a2 * Math.cos(4 * Math.PI * i / (numTaps - 1));
      taps[i] *= window;
    }
    
    // Normalize filter response
    let sum = 0;
    for (let i = 0; i < numTaps; i++) {
      sum += taps[i];
    }
    
    // Only normalize if sum is significant
    if (Math.abs(sum) > 0.001) {
      for (let i = 0; i < numTaps; i++) {
        taps[i] /= sum;
      }
    }
    
    return taps;
  }

  applyComplexBandpassFilter(iSample, qSample) {
    // Shift new samples into delay lines
    for (let i = this.bandpassDelayI.length - 1; i > 0; i--) {
      this.bandpassDelayI[i] = this.bandpassDelayI[i - 1];
      this.bandpassDelayQ[i] = this.bandpassDelayQ[i - 1];
    }
    this.bandpassDelayI[0] = iSample;
    this.bandpassDelayQ[0] = qSample;
    
    // Apply filter to both I and Q
    let iOut = 0;
    let qOut = 0;
    for (let i = 0; i < this.bandpassTaps.length; i++) {
      iOut += this.bandpassTaps[i] * this.bandpassDelayI[i];
      qOut += this.bandpassTaps[i] * this.bandpassDelayQ[i];
    }
    
    return { i: iOut, q: qOut };
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];
    const outputChannel = output[0];
    const blockSize = outputChannel.length;

    this.processCallCount++;

    // Debug logging
    if (this.processCallCount <= 5 || this.processCallCount % 200 === 0) {
      this.port.postMessage({
        type: 'debug',
        processCount: this.processCallCount,
        bufferSize: this.iqBuffer.length,
        message: `Mode: ${this.mode}, Tuning: ${this.tuningFreq}Hz, Buffer: ${this.iqBuffer.length}`
      });
    }

    this.processAudio(outputChannel, blockSize);

    // Manage buffer size
    const maxBufferSize = 48000;
    if (this.iqBuffer.length > maxBufferSize) {
      const toRemove = this.iqBuffer.length - maxBufferSize;
      this.iqBuffer.splice(0, toRemove);
      this.sampleCounter += toRemove;
    }

    return true;
  }

  processAudio(outputChannel, blockSize) {
    const minBufferSize = 2048;

    if (this.iqBuffer.length < minBufferSize) {
      outputChannel.fill(0);
      this.underrunCount++;
      return;
    }

    for (let i = 0; i < blockSize; i++) {
      let audioSample = 0;
      const iqIndex = i * 2;

      if (this.iqBuffer.length > iqIndex + 1) {
        // Decimate by averaging
        const iq1 = this.iqBuffer[iqIndex];
        const iq2 = this.iqBuffer[iqIndex + 1];
        
        let iSample = (iq1.i + iq2.i) / 2;
        let qSample = (iq1.q + iq2.q) / 2;

        // STEP 1: Frequency shift to baseband
        if (this.tuningFreq !== 0) {
          const sampleTime = (this.sampleCounter + iqIndex) / this.iqSampleRate;
          const phase = 2 * Math.PI * this.tuningFreq * sampleTime;
          const cosPhase = Math.cos(-phase);
          const sinPhase = Math.sin(-phase);

          const iShifted = iSample * cosPhase - qSample * sinPhase;
          const qShifted = iSample * sinPhase + qSample * cosPhase;
          
          iSample = iShifted;
          qSample = qShifted;
        }

        // STEP 2: Complex bandpass filter (filters both I and Q)
        const filtered = this.applyComplexBandpassFilter(iSample, qSample);

        // STEP 3: Demodulation
        switch (this.mode) {
          case 'usb':
            // USB: I + Hilbert(Q)
            audioSample = filtered.i + this.hilbertTransform(filtered.q);
            break;

          case 'lsb':
            // LSB: I - Hilbert(Q)
            audioSample = filtered.i - this.hilbertTransform(filtered.q);
            break;

          case 'cw':
            // CW uses SSB demodulation with narrow filter
            if (this.cwMode === 'lsb') {
              audioSample = filtered.i - this.hilbertTransform(filtered.q);
            } else {
              audioSample = filtered.i + this.hilbertTransform(filtered.q);
            }
            audioSample *= 2; // Boost CW signals
            break;

          case 'am':
            // AM: envelope detection
            audioSample = Math.sqrt(filtered.i * filtered.i + filtered.q * filtered.q);
            break;

          default:
            audioSample = filtered.i;
        }

        // STEP 4: AGC
        audioSample = this.applyAgc(audioSample);

      } else {
        // Fade out if buffer underrun
        if (i > 0) {
          audioSample = outputChannel[i - 1] * 0.95;
        }
      }

      // Output with soft clipping
      outputChannel[i] = Math.tanh(audioSample * 0.5);
    }

    // Remove consumed samples
    const samplesConsumed = Math.min(blockSize * 2, this.iqBuffer.length);
    if (samplesConsumed > 0) {
      this.iqBuffer.splice(0, samplesConsumed);
      this.sampleCounter += samplesConsumed;
    }
  }

  hilbertTransform(sample) {
    this.hilbertDelay[this.hilbertIndex] = sample;

    let output = 0;
    for (let i = 0; i < this.hilbertTaps.length; i++) {
      const delayIndex = (this.hilbertIndex - i + this.hilbertTaps.length) % this.hilbertTaps.length;
      output += this.hilbertTaps[i] * this.hilbertDelay[delayIndex];
    }

    this.hilbertIndex = (this.hilbertIndex + 1) % this.hilbertTaps.length;
    return output;
  }

  applyAgc(sample) {
    const envelope = Math.abs(sample);
    const alpha = 0.0001;

    if (envelope > 0.001) {
      if (envelope > this.agcTarget) {
        this.agcGain *= (1 - alpha);
      } else {
        this.agcGain *= (1 + alpha * 0.5);
      }
    }

    this.agcGain = Math.max(1.0, Math.min(3.0, this.agcGain));
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
}

registerProcessor('sdr-processor', SdrProcessor);
