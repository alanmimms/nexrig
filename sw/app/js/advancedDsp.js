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
	
	// First, load the AudioWorklet module
	try {
          // Use the correct absolute path
          const workletUrl = '/app/js/sdr-processor.js?v=' + Date.now();
          console.log('Loading AudioWorklet from:', workletUrl);
          
          await this.audioContext.audioWorklet.addModule(workletUrl);
          console.log('AudioWorklet module loaded successfully');
	} catch (workletError) {
          console.error('Failed to load AudioWorklet module:', workletError);
          // Try without cache busting
          await this.audioContext.audioWorklet.addModule('/app/js/sdr-processor.js');
	}
	
	// Now create the worklet node
	this.workletNode = new AudioWorkletNode(this.audioContext, 'sdr-processor', {
          numberOfInputs: 0,
          numberOfOutputs: 1,
          outputChannelCount: [1]
	});
	
	// Try to load WASM, but don't fail if it's missing
	try {
          const wasmResponse = await fetch('/app/wasm/sdr_dsp.wasm');
          if (wasmResponse.ok) {
            const wasmBytes = await wasmResponse.arrayBuffer();
            
            // Send WASM bytes to worklet
            this.workletNode.port.postMessage({
              type: 'initWasm',
              wasmBytes: wasmBytes
            });
            console.log('WASM module sent to AudioWorklet');
          } else {
            console.warn('WASM not found, using JavaScript DSP fallback');
          }
	} catch (wasmError) {
          console.warn('WASM loading failed, using JavaScript DSP fallback:', wasmError);
	}
	
	this.workletNode.connect(this.audioContext.destination);
	console.log('AudioWorkletNode created and connected');
	
	// Listen for messages from AudioWorklet
	this.workletNode.port.onmessage = (event) => {
          if (event.data.type === 'debug') {
            if (event.data.message) {
              console.log(`AudioWorklet: ${event.data.message}`);
            }
            
            // Update WASM indicator based on messages
            if (event.data.message && event.data.message.includes('WASM DSP initialized successfully')) {
              if (window.nexrigApp) {
		window.nexrigApp.updateWASMIndicator(true);
              }
            } else if (event.data.message && event.data.message.includes('WASM init failed')) {
              if (window.nexrigApp) {
		window.nexrigApp.updateWASMIndicator(false);
              }
            }
          } else if (event.data.type === 'dspStatus') {
            // Handle status updates
            if (window.nexrigApp) {
              window.nexrigApp.updateWASMIndicator(event.data.useWasm);
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
	
	// Ensure AudioContext is running
	if (this.audioContext.state === 'suspended') {
          console.log('AudioContext suspended, resuming...');
          await this.audioContext.resume();
	}
	
	console.log('AudioContext and SDR Worklet created, final state:', this.audioContext.state);
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
      // Log why we're not processing
      if (!this.audioContext) {
        console.warn('DSP: No AudioContext - audio not initialized');
      } else if (this.audioContext.state !== 'running') {
        console.warn(`DSP: AudioContext not running, state: ${this.audioContext.state}`);
      } else if (!this.workletNode) {
        console.warn('DSP: No workletNode - AudioWorklet not loaded');
      }
      return;
    }
    
    // Check if we're getting valid data
    if (!iqData || !iqData.i || !iqData.q || iqData.i.length === 0) {
      console.warn('DSP: Invalid or empty I/Q data received');
      return;
    }
    
    // Debug: Log occasionally to confirm we're sending data
    if (!this.iqSendCount) this.iqSendCount = 0;
    this.iqSendCount++;
    if (this.iqSendCount <= 5 || this.iqSendCount % 100 === 0) {
      console.log(`DSP: Sending I/Q data #${this.iqSendCount} to worklet: ${iqData.i.length} samples`);
    }
    
    // Send I/Q data to AudioWorklet processor
    this.workletNode.port.postMessage({
      type: 'iqData',
      samples: {
        i: iqData.i,
        q: iqData.q
      }
    });
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
