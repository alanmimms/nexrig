/**
 * SDR AudioWorklet Processor
 */

class SdrProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    // Default config - will be updated via message from main thread
    this.config = {
      filterParams: {
        usb: { low: 200, high: 3500 },
        lsb: { low: -3500, high: -200 },
        cw: { low: 200, high: 700 },
        am: { low: -4000, high: 4000 }
      },
      sampleRates: {
        iq: 96000,
        audio: 48000,
        decimation: 2
      },
      agc: {
        initialGain: 3.0,
        target: 0.3,
        attackRate: 0.0001,
        minGain: 1.0,
        maxGain: 3.0
      },
      filter: {
        order: 64,
        window: 'blackman'
      }
    };
    
    // DSP parameters
    this.sampleRate = this.config.sampleRates.audio;
    this.iqSampleRate = this.config.sampleRates.iq;
    this.decimationRatio = this.config.sampleRates.decimation;
    
    this.tuningFreq = 0;
    this.mode = 'usb';
    this.cwMode = 'usb';

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
    
    // Don't update filter yet - wait for config
    this.filterReady = false;

    // AGC
    this.agcGain = this.config.agc.initialGain;
    this.agcTarget = this.config.agc.target;

    // Listen for messages
    this.port.onmessage = (event) => {
      this.handleMessage(event.data);
    };

    // Request config from main thread
    this.port.postMessage({
      type: 'requestConfig'
    });

    // Debug counters
    this.processCallCount = 0;
    this.iqDataCount = 0;
    this.underrunCount = 0;
  }

  handleMessage(data) {
    switch (data.type) {
      case 'config':
        // Receive config from main thread
        this.config = data.config;
        this.sampleRate = this.config.sampleRates.audio;
        this.iqSampleRate = this.config.sampleRates.iq;
        this.decimationRatio = this.config.sampleRates.decimation;
        this.agcTarget = this.config.agc.target;
        
        // Now we can initialize the filter
        this.updateBandpassFilter();
        this.filterReady = true;
        
        this.port.postMessage({
          type: 'debug',
          message: 'Config received and filter initialized'
        });
        break;

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
        if (this.filterReady) {
          this.updateBandpassFilter();
        }
        this.port.postMessage({
          type: 'debug',
          message: `Mode: ${this.mode}`
        });
        break;

      case 'setCwMode':
        this.cwMode = data.cwMode || 'usb';
        if (this.mode === 'cw' && this.filterReady) {
          this.updateBandpassFilter();
        }
        break;
    }
  }

  updateBandpassFilter() {
    let lowFreq, highFreq;
    
    if (this.mode === 'cw') {
      // CW filter based on SSB mode
      const cwParams = this.config.filterParams.cw;
      if (this.cwMode === 'lsb') {
        lowFreq = -cwParams.high;
        highFreq = -cwParams.low;
      } else {
        lowFreq = cwParams.low;
        highFreq = cwParams.high;
      }
    } else {
      const params = this.config.filterParams[this.mode];
      lowFreq = params.low;
      highFreq = params.high;
    }
    
    const filterOrder = this.config.filter.order;
    this.bandpassTaps = this.generateBandpassFilter(
      lowFreq,
      highFreq,
      this.sampleRate,
      filterOrder
    );
    
    this.bandpassDelayI = new Float32Array(filterOrder);
    this.bandpassDelayQ = new Float32Array(filterOrder);
    
    this.port.postMessage({
      type: 'debug',
      message: `Filter: ${lowFreq}Hz to ${highFreq}Hz`
    });
  }

  generateBandpassFilter(lowFreq, highFreq, sampleRate, numTaps) {
    const taps = new Float32Array(numTaps);
    const center = Math.floor(numTaps / 2);
    
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
      
      // Window function
      let window = 1.0;
      if (this.config.filter.window === 'blackman') {
        const a0 = 0.42;
        const a1 = 0.5;
        const a2 = 0.08;
        window = a0 - a1 * Math.cos(2 * Math.PI * i / (numTaps - 1)) 
                    + a2 * Math.cos(4 * Math.PI * i / (numTaps - 1));
      } else {
        // Hamming
        window = 0.54 - 0.46 * Math.cos(2 * Math.PI * i / (numTaps - 1));
      }
      taps[i] *= window;
    }
    
    // Normalize
    let sum = 0;
    for (let i = 0; i < numTaps; i++) {
      sum += taps[i];
    }
    
    if (Math.abs(sum) > 0.001) {
      for (let i = 0; i < numTaps; i++) {
        taps[i] /= sum;
      }
    }
    
    return taps;
  }

  applyComplexBandpassFilter(iSample, qSample) {
    // Shift samples into delay lines
    for (let i = this.bandpassDelayI.length - 1; i > 0; i--) {
      this.bandpassDelayI[i] = this.bandpassDelayI[i - 1];
      this.bandpassDelayQ[i] = this.bandpassDelayQ[i - 1];
    }
    this.bandpassDelayI[0] = iSample;
    this.bandpassDelayQ[0] = qSample;
    
    // Apply filter
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

    if (this.processCallCount <= 5 || this.processCallCount % 200 === 0) {
      this.port.postMessage({
        type: 'debug',
        message: `Buffer: ${this.iqBuffer.length}, Mode: ${this.mode}, Filter: ${this.filterReady ? 'ready' : 'waiting'}`
      });
    }

    // Only process if filter is ready
    if (this.filterReady) {
      this.processAudio(outputChannel, blockSize);
    } else {
      outputChannel.fill(0);
    }

    // Manage buffer
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

    // Debug: log filter output occasionally
    if (this.processCallCount % 100 === 0 && i === 0) {
      this.port.postMessage({
	type: 'debug',
	message: `Mode: ${this.mode}, Filtered I: ${filtered.i.toFixed(6)}, Q: ${filtered.q.toFixed(6)}`
      });
    }

    for (let i = 0; i < blockSize; i++) {
      let audioSample = 0;
      const iqIndex = i * this.decimationRatio;

      if (this.iqBuffer.length > iqIndex + 1) {
        // Decimate
        const iq1 = this.iqBuffer[iqIndex];
        const iq2 = this.iqBuffer[iqIndex + 1];
        
        let iSample = (iq1.i + iq2.i) / 2;
        let qSample = (iq1.q + iq2.q) / 2;

        // Frequency shift
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

        // Bandpass filter
        const filtered = this.applyComplexBandpassFilter(iSample, qSample);

        // Demodulation
        switch (this.mode) {
          case 'usb':
            audioSample = filtered.i + this.hilbertTransform(filtered.q);
            break;

          case 'lsb':
            audioSample = filtered.i - this.hilbertTransform(filtered.q);
            break;

          case 'cw':
            if (this.cwMode === 'lsb') {
              audioSample = filtered.i - this.hilbertTransform(filtered.q);
            } else {
              audioSample = filtered.i + this.hilbertTransform(filtered.q);
            }
            audioSample *= 2;
            break;

          case 'am':
            audioSample = Math.sqrt(filtered.i * filtered.i + filtered.q * filtered.q);
            break;

          default:
            audioSample = filtered.i;
        }

        // AGC
        audioSample = this.applyAgc(audioSample);

      } else {
        if (i > 0) {
          audioSample = outputChannel[i - 1] * 0.95;
        }
      }

      outputChannel[i] = Math.tanh(audioSample * 0.5);
    }

    // Remove consumed samples
    const samplesConsumed = Math.min(blockSize * this.decimationRatio, this.iqBuffer.length);
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
    const alpha = this.config.agc.attackRate;

    if (envelope > 0.001) {
      if (envelope > this.agcTarget) {
        this.agcGain *= (1 - alpha);
      } else {
        this.agcGain *= (1 + alpha * 0.5);
      }
    }

    this.agcGain = Math.max(this.config.agc.minGain, 
                            Math.min(this.config.agc.maxGain, this.agcGain));
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

    for (let i = 0; i < numTaps; i++) {
      const window = 0.54 - 0.46 * Math.cos(2 * Math.PI * i / (numTaps - 1));
      taps[i] *= window;
    }

    return taps;
  }
}

registerProcessor('sdr-processor', SdrProcessor);
