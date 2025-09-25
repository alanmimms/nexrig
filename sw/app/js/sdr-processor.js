/**
 * SDR AudioWorklet Processor
 * High-performance DSP running on dedicated audio thread
 */

class SdrProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    // DSP parameters
    this.sampleRate = 48000;
    this.iqSampleRate = 96000;
    this.decimationRatio = 2; // 96kHz -> 48kHz
    this.tuningFreq = 0; // Hz
    this.mode = 'usb';

    // I/Q buffer from WebSocket
    this.iqBuffer = [];
    this.sampleCounter = 0;  // Count processed samples for phase calculation

    // JavaScript DSP implementation
    this.hilbertTaps = this.generateHilbertFilter(16);
    this.hilbertDelay = new Float32Array(16);
    this.hilbertIndex = 0;

    // AGC with gentle response
    this.agcGain = 3.0;
    this.agcTarget = 0.3;

    // Listen for messages from main thread
    this.port.onmessage = (event) => {
      this.handleMessage(event.data);
    };

    // Debug counters
    this.processCallCount = 0;
    this.iqDataCount = 0;
    this.underrunCount = 0;
    this.lastDebugTime = 0;
  }

  handleMessage(data) {
    switch (data.type) {
      case 'test':
        this.port.postMessage({
          type: 'testResponse',
          message: 'AudioWorklet received test message: ' + data.message
        });
        break;

      case 'iqData':
        // Add I/Q samples to buffer
        const samples = data.samples;
        if (samples && samples.i && samples.q) {
          for (let i = 0; i < samples.i.length; i++) {
            this.iqBuffer.push({
              i: samples.i[i] / 8388607.0, // 24-bit to float
              q: samples.q[i] / 8388607.0
            });
          }
          this.iqDataCount++;

          // Debug: Log when we receive I/Q data
          if (this.iqDataCount <= 5 || this.iqDataCount % 100 === 0) {
            this.port.postMessage({
              type: 'debug',
              message: `Received I/Q data #${this.iqDataCount}: ${samples.i.length} samples, buffer now has ${this.iqBuffer.length}`
            });
          }
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
        break;
    }
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];
    const outputChannel = output[0];
    const blockSize = outputChannel.length; // 128 samples

    this.processCallCount++;

    // Debug on first few calls
    if (this.processCallCount <= 5) {
      this.port.postMessage({
        type: 'debug',
        processCount: this.processCallCount,
        bufferSize: this.iqBuffer.length,
        message: 'AudioWorklet process() is running!'
      });
    }

    // Periodic status update
    if (this.processCallCount % 200 === 0) {
      this.port.postMessage({
        type: 'debug',
        processCount: this.processCallCount,
        bufferSize: this.iqBuffer.length,
        message: `Buffer: ${this.iqBuffer.length} samples, underruns: ${this.underrunCount}, AGC: ${this.agcGain.toFixed(2)}`
      });
    }

    // Process with JavaScript DSP
    this.processWithJavaScript(outputChannel, blockSize);

    // Keep buffer size reasonable
    const maxBufferSize = 48000; // 0.5 seconds at 96kHz
    if (this.iqBuffer.length > maxBufferSize) {
      const toRemove = this.iqBuffer.length - maxBufferSize;
      this.iqBuffer.splice(0, toRemove);
      this.sampleCounter += toRemove;

      if (this.processCallCount % 100 === 0) {
        this.port.postMessage({
          type: 'debug',
          message: `Trimmed ${toRemove} excess samples from buffer`
        });
      }
    }

    return true; // Keep processor alive
  }

  processWithJavaScript(outputChannel, blockSize) {
    // Require more buffer to prevent starvation
    const minBufferSize = 2048; // ~21ms at 96kHz

    // If buffer is too low, output silence and wait for more data
    if (this.iqBuffer.length < minBufferSize) {
      outputChannel.fill(0);
      this.underrunCount++;
      
      if (this.processCallCount % 50 === 0) {
        this.port.postMessage({
          type: 'debug',
          message: `Buffer underrun: need ${minBufferSize}, have ${this.iqBuffer.length}`
        });
      }
      return;
    }

    // Process audio samples
    for (let i = 0; i < blockSize; i++) {
      let audioSample = 0;
      const iqIndex = i * 2; // 2:1 decimation

      // Check if we have enough I/Q samples
      if (this.iqBuffer.length > iqIndex + 1) {
        // Average two I/Q samples for decimation
        const iq1 = this.iqBuffer[iqIndex];
        const iq2 = this.iqBuffer[iqIndex + 1];
        
        const iSample = (iq1.i + iq2.i) / 2;
        const qSample = (iq1.q + iq2.q) / 2;

        // Apply frequency shift for tuning
        let iShifted = iSample;
        let qShifted = qSample;

        if (this.tuningFreq !== 0) {
	  const sampleTime = (this.sampleCounter + iqIndex) / this.iqSampleRate;
	  const phase = (2 * Math.PI * this.tuningFreq * sampleTime) % (2 * Math.PI);
          const cosPhase = Math.cos(-phase);
          const sinPhase = Math.sin(-phase);

          // Complex multiplication for frequency shift
          iShifted = iSample * cosPhase - qSample * sinPhase;
          qShifted = iSample * sinPhase + qSample * cosPhase;
        }

        // Demodulation based on mode
        switch (this.mode) {
          case 'usb':
            // USB: I + Hilbert(Q)
            const qHilbert = this.hilbertTransform(qShifted);
            audioSample = iShifted + qHilbert;
            break;

          case 'lsb':
            // LSB: I - Hilbert(Q)
            const qHilbertLsb = this.hilbertTransform(qShifted);
            audioSample = iShifted - qHilbertLsb;
            break;

          case 'am':
          case 'cw':
            // Envelope detection
            audioSample = Math.sqrt(iShifted * iShifted + qShifted * qShifted);
            
            // Add CW tone at 600Hz if in CW mode
            if (this.mode === 'cw' && audioSample > 0.01) {
              const cwTime = this.sampleCounter / this.sampleRate;
              audioSample *= Math.sin(2 * Math.PI * 600 * cwTime);
            }
            break;

          default:
            audioSample = iShifted;
        }

        // Apply gentle AGC
        audioSample = this.applyAgc(audioSample);

      } else {
        // Not enough samples - use last sample with decay to avoid click
        if (i > 0) {
          audioSample = outputChannel[i - 1] * 0.95;
        }
      }

      // Soft clipping for output
      outputChannel[i] = Math.tanh(audioSample * 0.3);
    }

    // Remove consumed samples
    const samplesConsumed = Math.min(blockSize * 2, this.iqBuffer.length);
    if (samplesConsumed > 0) {
      this.iqBuffer.splice(0, samplesConsumed);
      this.sampleCounter += samplesConsumed;
    }
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

  applyAgc(sample) {
    const envelope = Math.abs(sample);
    const alpha = 0.0001; // Very slow time constant

    // Only adjust gain if there's significant signal
    if (envelope > 0.001) {
      if (envelope > this.agcTarget) {
        // Reduce gain slowly
        this.agcGain *= (1 - alpha);
      } else {
        // Increase gain slowly
        this.agcGain *= (1 + alpha * 0.5);
      }
    }

    // Limit gain range
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
