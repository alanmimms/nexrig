/**
 * TX UI Integration for NexRig Application
 * Extends the existing nexrigApp.js with transmit functionality
 * Add this to your nexrigApp.js or include as a separate module
 */

class TxInterface {
  constructor(nexrigApp) {
    this.app = nexrigApp;
    this.txProcessor = null;
    this.audioContext = null;
    this.micStream = null;
    this.txActive = false;
    this.pttLocked = false;
    
    // TX audio buffer for streaming
    this.txBuffer = [];
    this.txBufferSize = 480; // 10ms at 48kHz
    
    // Monitoring
    this.alcMeter = null;
    this.modMeter = null;
    this.micLevel = null;
    
    // Test modes
    this.testMode = 'none'; // 'none', 'twoTone', 'whistle'
  }
  
  async initialize() {
    // Create TX processor
    const TxProcessor = window.TxProcessor;
    if (TxProcessor) {
      this.txProcessor = new TxProcessor();
      console.log('TX Processor initialized');
    } else {
      console.error('TX Processor not loaded');
      return false;
    }
    
    // Add TX UI elements to existing interface
    this.injectTxControls();
    
    // Set up event handlers
    this.setupEventHandlers();
    
    return true;
  }
  
  injectTxControls() {
    // Find the mode buttons container
    const modeButtons = document.querySelector('.mode-buttons');
    
    // Add PTT button after mode buttons
    if (modeButtons) {
      const pttGroup = document.createElement('div');
      pttGroup.className = 'control-group';
      pttGroup.innerHTML = `
        <label>Transmit Control</label>
        <div class="ptt-controls">
          <button class="ptt-btn" id="pttButton">
            <span class="ptt-icon">🎤</span>
            <span class="ptt-text">PTT</span>
          </button>
          <button class="ptt-lock-btn" id="pttLockButton" title="PTT Lock">
            <span class="lock-icon">🔓</span>
          </button>
        </div>
        <div class="tx-test-controls" style="margin-top: 8px;">
          <select id="txTestMode" style="width: 100%;">
            <option value="none">Normal TX</option>
            <option value="twoTone">Two-Tone Test</option>
            <option value="whistle">Whistle Test</option>
            <option value="cw">CW Test</option>
          </select>
        </div>
      `;
      modeButtons.parentNode.insertBefore(pttGroup, modeButtons.nextSibling);
    }
    
    // Add TX meters to the meters panel
    const metersContent = document.querySelector('.meters-content');
    if (metersContent) {
      const txMeters = document.createElement('div');
      txMeters.className = 'tx-meters';
      txMeters.innerHTML = `
        <div class="meter">
          <label>Mic Level</label>
          <div class="meter-bar">
            <div class="meter-fill mic-level" id="micLevelMeter" style="width: 0%;"></div>
          </div>
          <span class="meter-value" id="micLevelValue">-∞ dB</span>
        </div>
        <div class="meter">
          <label>ALC</label>
          <div class="meter-bar">
            <div class="meter-fill alc-meter" id="alcMeter" style="width: 0%;"></div>
          </div>
          <span class="meter-value" id="alcValue">1.0x</span>
        </div>
        <div class="meter">
          <label>Modulation</label>
          <div class="meter-bar">
            <div class="meter-fill mod-meter" id="modMeter" style="width: 0%;"></div>
          </div>
          <span class="meter-value" id="modValue">0%</span>
        </div>
      `;
      metersContent.appendChild(txMeters);
    }
    
    // Add mic selection to audio controls
    const audioControls = document.querySelector('.audio-controls');
    if (audioControls) {
      const micSelect = document.createElement('select');
      micSelect.id = 'micSelect';
      micSelect.style.marginTop = '5px';
      micSelect.innerHTML = '<option value="">Select Microphone...</option>';
      audioControls.appendChild(micSelect);
      
      // Populate microphone list
      this.updateMicrophoneList();
    }
    
    // Add CSS for TX controls
    const style = document.createElement('style');
    style.textContent = `
      .ptt-controls {
        display: flex;
        gap: 5px;
      }
      
      .ptt-btn {
        flex: 1;
        background: #2a2a2a;
        border: none;
        color: white;
        padding: 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      
      .ptt-btn:hover {
        background: #3a3a3a;
      }
      
      .ptt-btn.transmitting {
        background: #f44336;
        animation: pulse 1s infinite;
      }
      
      @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
      }
      
      .ptt-lock-btn {
        width: 40px;
        background: #2a2a2a;
        border: none;
        color: white;
        padding: 8px;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
      }
      
      .ptt-lock-btn.locked {
        background: #ff9800;
      }
      
      .mic-level { background: #4caf50; }
      .alc-meter { background: #2196f3; }
      .mod-meter { background: #ff9800; }
      
      .tx-meters {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #3a3a3a;
      }
    `;
    document.head.appendChild(style);
  }
  
  setupEventHandlers() {
    // PTT button - mouse/touch events for momentary PTT
    const pttButton = document.getElementById('pttButton');
    if (pttButton) {
      // Mouse events
      pttButton.addEventListener('mousedown', () => this.startTransmit());
      pttButton.addEventListener('mouseup', () => this.stopTransmit());
      pttButton.addEventListener('mouseleave', () => this.stopTransmit());
      
      // Touch events for mobile
      pttButton.addEventListener('touchstart', (e) => {
        e.preventDefault();
        this.startTransmit();
      });
      pttButton.addEventListener('touchend', (e) => {
        e.preventDefault();
        this.stopTransmit();
      });
    }
    
    // PTT lock button
    const pttLockButton = document.getElementById('pttLockButton');
    if (pttLockButton) {
      pttLockButton.addEventListener('click', () => this.togglePttLock());
    }
    
    // Test mode selector
    const testModeSelect = document.getElementById('txTestMode');
    if (testModeSelect) {
      testModeSelect.addEventListener('change', (e) => {
        this.testMode = e.target.value;
        console.log('TX test mode:', this.testMode);
      });
    }
    
    // Keyboard PTT (spacebar)
    document.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && !e.repeat && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        this.startTransmit();
      }
    });
    
    document.addEventListener('keyup', (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        if (!this.pttLocked) {
          this.stopTransmit();
        }
      }
    });
    
    // Microphone selection
    const micSelect = document.getElementById('micSelect');
    if (micSelect) {
      micSelect.addEventListener('change', (e) => {
        this.selectMicrophone(e.target.value);
      });
    }
  }
  
  async updateMicrophoneList() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const micSelect = document.getElementById('micSelect');
      
      if (micSelect) {
        // Clear existing options except first
        micSelect.innerHTML = '<option value="">Select Microphone...</option>';
        
        devices
          .filter(device => device.kind === 'audioinput')
          .forEach(device => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label || `Microphone ${device.deviceId.substr(0, 8)}`;
            micSelect.appendChild(option);
          });
      }
    } catch (error) {
      console.error('Failed to enumerate audio devices:', error);
    }
  }
  
  async selectMicrophone(deviceId) {
    if (!deviceId) return;
    
    try {
      // Stop existing stream
      if (this.micStream) {
        this.micStream.getTracks().forEach(track => track.stop());
      }
      
      // Get new stream with selected device
      this.micStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: { exact: deviceId },
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false, // We have our own ALC
          sampleRate: 48000
        }
      });
      
      console.log('Microphone selected:', deviceId);
      
      // Set up audio processing if needed
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: 48000
        });
      }
      
    } catch (error) {
      console.error('Failed to access microphone:', error);
      alert('Failed to access microphone. Please check permissions.');
    }
  }
  
  async startTransmit() {
    if (this.txActive) return;
    
    console.log('Starting transmit...');
    
    // Check if we have STM32 connection
    if (!this.app.connected) {
      console.error('Not connected to hardware');
      return;
    }
    
    // Switch to TX mode via REST API
    try {
      const response = await fetch(`${this.app.apiBaseUrl}/rf/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'tx' })
      });
      
      if (!response.ok) {
        throw new Error('Failed to switch to TX mode');
      }
    } catch (error) {
      console.error('TX mode switch failed:', error);
      return;
    }
    
    this.txActive = true;
    
    // Update UI
    const pttButton = document.getElementById('pttButton');
    if (pttButton) {
      pttButton.classList.add('transmitting');
    }
    
    // Start TX streaming
    this.startTxStream();
  }
  
  async stopTransmit() {
    if (!this.txActive || this.pttLocked) return;
    
    console.log('Stopping transmit...');
    
    this.txActive = false;
    
    // Stop TX streaming
    this.stopTxStream();
    
    // Switch back to RX mode
    try {
      await fetch(`${this.app.apiBaseUrl}/rf/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'rx' })
      });
    } catch (error) {
      console.error('RX mode switch failed:', error);
    }
    
    // Update UI
    const pttButton = document.getElementById('pttButton');
    if (pttButton) {
      pttButton.classList.remove('transmitting');
    }
  }
  
  togglePttLock() {
    this.pttLocked = !this.pttLocked;
    
    const lockButton = document.getElementById('pttLockButton');
    if (lockButton) {
      lockButton.classList.toggle('locked', this.pttLocked);
      lockButton.querySelector('.lock-icon').textContent = this.pttLocked ? '🔒' : '🔓';
    }
    
    if (this.pttLocked && this.txActive) {
      console.log('PTT locked in TX');
    } else if (!this.pttLocked && this.txActive) {
      this.stopTransmit();
    }
  }
  
  startTxStream() {
    if (!this.app.websocket || this.app.websocket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }
    
    // Notify server we're starting TX
    this.app.websocket.send(JSON.stringify({
      type: 'startTxStream',
      sampleRate: 48000,
      mode: this.app.dsp.mode || 'usb'
    }));
    
    // Start generating modulation data
    this.txStreamInterval = setInterval(() => {
      this.processTxAudio();
    }, 10); // 10ms intervals = 480 samples at 48kHz
  }
  
  stopTxStream() {
    if (this.txStreamInterval) {
      clearInterval(this.txStreamInterval);
      this.txStreamInterval = null;
    }
    
    // Notify server
    if (this.app.websocket && this.app.websocket.readyState === WebSocket.OPEN) {
      this.app.websocket.send(JSON.stringify({
        type: 'stopTxStream'
      }));
    }
  }
  
  processTxAudio() {
    if (!this.txProcessor) return;
    
    let audioSamples;
    
    // Generate or capture audio based on mode
    if (this.testMode === 'twoTone') {
      // Generate two-tone test signal
      audioSamples = this.txProcessor.generateTwoTone(this.txBufferSize);
    } else if (this.testMode === 'whistle') {
      // Generate whistle test (swept sine)
      audioSamples = this.generateWhistle(this.txBufferSize);
    } else if (this.testMode === 'cw') {
      // Generate CW test
      const keyDown = Math.sin(Date.now() * 0.003) > 0; // Simple keying pattern
      const result = this.txProcessor.processCw(keyDown, this.txBufferSize);
      this.sendModulationData(result.amplitude, result.phase);
      this.updateTxMeters(result.amplitude);
      return;
    } else {
      // Use microphone input or silence
      audioSamples = this.getMicrophoneAudio(this.txBufferSize);
    }
    
    // Process audio through TX DSP chain
    const mode = this.app.dsp.mode || 'usb';
    let result;
    
    if (mode === 'am') {
      result = this.txProcessor.processAmAudio(audioSamples, 0.9);
    } else {
      // SSB (USB/LSB)
      result = this.txProcessor.processSsbAudio(audioSamples, mode);
    }
    
    // Quantize for hardware
    const quantized = this.txProcessor.quantizeForHardware(result.amplitude, result.phase);
    
    // Send to server
    this.sendModulationData(quantized.amplitude, quantized.phase);
    
    // Update meters
    this.updateTxMeters(result.amplitude);
  }
  
  getMicrophoneAudio(numSamples) {
    // For now, return silence if no mic
    // In real implementation, this would read from Web Audio API input
    const samples = new Float32Array(numSamples);
    
    if (this.micStream && this.audioContext) {
      // TODO: Connect mic stream to ScriptProcessor or AudioWorklet
      // to get actual audio samples
    }
    
    return samples;
  }
  
  generateWhistle(numSamples) {
    const samples = new Float32Array(numSamples);
    const startFreq = 500;
    const endFreq = 2500;
    const sweepRate = (endFreq - startFreq) / (this.txProcessor.sampleRate * 2); // 2 second sweep
    
    for (let i = 0; i < numSamples; i++) {
      const t = (Date.now() % 2000) / 1000; // 0-2 seconds
      const freq = startFreq + (endFreq - startFreq) * t / 2;
      samples[i] = 0.5 * Math.sin(2 * Math.PI * freq * i / this.txProcessor.sampleRate);
    }
    
    return samples;
  }
  
  sendModulationData(amplitude, phase) {
    if (!this.app.websocket || this.app.websocket.readyState !== WebSocket.OPEN) {
      return;
    }
    
    // Use CBOR protocol to send
    window.cborProtocol.sendTxModulation(
      amplitude, 
      phase, 
      this.app.currentFreq,
      this.app.dsp.mode === 'usb' ? 0 : 
	this.app.dsp.mode === 'lsb' ? 1 :
	this.app.dsp.mode === 'am' ? 2 : 3
    );
  }

  updateTxMeters(amplitude) {
    // Calculate RMS for modulation meter
    let sum = 0;
    for (let i = 0; i < amplitude.length; i++) {
      sum += amplitude[i] * amplitude[i];
    }
    const rms = Math.sqrt(sum / amplitude.length);
    const modPercent = Math.min(100, rms * 100);
    
    // Update modulation meter
    const modMeter = document.getElementById('modMeter');
    const modValue = document.getElementById('modValue');
    if (modMeter && modValue) {
      modMeter.style.width = `${modPercent}%`;
      modValue.textContent = `${modPercent.toFixed(0)}%`;
    }
    
    // Update ALC meter
    const alcGain = this.txProcessor.getAlcGain();
    const alcPercent = (alcGain / this.txProcessor.alcMaxGain) * 100;
    
    const alcMeter = document.getElementById('alcMeter');
    const alcValue = document.getElementById('alcValue');
    if (alcMeter && alcValue) {
      alcMeter.style.width = `${alcPercent}%`;
      alcValue.textContent = `${alcGain.toFixed(1)}x`;
    }
  }
}

// Extend the NexRigApplication class
if (window.NexRigApplication) {
  const originalInitialize = NexRigApplication.prototype.initialize;
  
  NexRigApplication.prototype.initialize = async function() {
    // Call original initialize
    await originalInitialize.call(this);
    
    // Initialize TX interface
    this.txInterface = new TxInterface(this);
    await this.txInterface.initialize();
    
    console.log('TX interface initialized');
  };
}
