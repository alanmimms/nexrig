/**
 * NexRig Browser Application
 * Main application controller and initialization
 * Enhanced with filter envelope visualization
 */

class NexRigApplication {
  constructor() {
    this.connected = false;
    this.apiBaseUrl = window.location.origin + '/api';
    this.wsUrl = `ws://${window.location.hostname}:3001`;
    this.websocket = null;
    this.currentFreq = 14200000;
    this.currentBand = '20m';
    this.currentMode = 'rx';
    
    // DSP processor
    this.dsp = new AdvancedDsp();
    
    // Filter parameters for visualization
    this.filterParams = {
      usb: { low: 200, high: 3500, offset: 0 },
      lsb: { low: -3500, high: -200, offset: 0 },
      cw: { low: 200, high: 700, offset: 0 },  // 500Hz filter for USB-style CW
      am: { low: -4000, high: 4000, offset: 0 }
    };
  }

  async initialize() {
    console.log('Initializing NexRig Application...');
    
    try {
      // Update loading status
      this.updateLoadingStatus('Connecting to hardware...');
      
      // Test REST API connection
      const response = await fetch(`${this.apiBaseUrl}/status`);
      if (!response.ok) {
        throw new Error('Failed to connect to hardware');
      }
      
      const status = await response.json();
      console.log('Hardware status:', status);
      
      // Initialize DSP and audio
      this.updateLoadingStatus('Initializing audio system...');
      const dspInitialized = await this.dsp.initialize();
      if (!dspInitialized) {
        throw new Error('Failed to initialize audio system');
      }
      
      // Initialize WebSocket connection
      await this.initializeWebSocket();
      
      // Initialize UI components
      this.initializeUI();
      
      // Check for SIMD support
      this.checkSIMDSupport();

      // Mark as connected and show app
      this.connected = true;
      this.hideLoadingScreen();
      
      console.log('NexRig Application initialized successfully');
      
    } catch (error) {
      console.error('Failed to initialize:', error);
      this.updateLoadingStatus('Connection failed. Retrying...', error.message);
      
      // Retry after delay
      setTimeout(() => this.initialize(), 2000);
    }
  }
  
  updateLoadingStatus(message, details = '') {
    const loadingText = document.getElementById('loadingDetails');
    if (loadingText) {
      loadingText.textContent = details ? `${message} ${details}` : message;
    }
  }
  
  async initializeWebSocket() {
    return new Promise((resolve, reject) => {
      this.websocket = new WebSocket(this.wsUrl);
      
      this.websocket.onopen = () => {
        console.log('WebSocket connected');
        // I/Q stream starts automatically from server (like real radio hardware)
        resolve();
      };
      
      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(new Error('WebSocket connection failed'));
      };
      
      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };
      
      this.websocket.onclose = () => {
        console.log('WebSocket disconnected');
        this.connected = false;
        // Attempt to reconnect
        setTimeout(() => this.initializeWebSocket(), 2000);
      };
    });
  }
  
  handleWebSocketMessage(data) {
    switch (data.type) {
    case 'connected':
      console.log('Hardware capabilities:', data.capabilities);
      // I/Q stream will be started when user enables audio
      break;
      
    case 'iqData':
      // Always update waterfall display
      this.updateWaterfall(data.data);
      
      // Only process through DSP if AudioContext is ready
      if (this.dsp.audioContext && this.dsp.audioContext.state === 'running') {
        this.dsp.processIqData(data.data);
      }
      break;
      
    case 'txStreamReady':
      console.log('TX stream ready, sample rate:', data.sampleRate);
      break;
      
    default:
      console.log('Unknown WebSocket message:', data.type);
    }
  }
  
  updateWaterfall(iqData) {
    const canvas = document.getElementById('waterfallCanvas');
    if (!canvas) return;
    
    // Validate I/Q data
    if (!iqData || !iqData.i || !iqData.q || iqData.i.length === 0) return;
    
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const width = canvas.width;
    const height = canvas.height;
    
    // Scroll existing waterfall up
    try {
      const imageData = ctx.getImageData(0, 1, width, height - 1);
      ctx.putImageData(imageData, 0, 0);
    } catch (error) {
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, width, height);
    }
    
    // Use proper FFT size (power of 2)
    const fftSize = 512;
    const spectrum = new Float32Array(fftSize);
    
    // Window function for better spectral characteristics
    const window = new Float32Array(fftSize);
    for (let i = 0; i < fftSize; i++) {
      window[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / (fftSize - 1)); // Hann window
    }
    
    // Prepare I/Q data (zero-pad or truncate to FFT size)
    const iData = new Float32Array(fftSize);
    const qData = new Float32Array(fftSize);
    
    for (let i = 0; i < fftSize; i++) {
      if (i < iqData.i.length) {
        iData[i] = (iqData.i[i] / 8388607.0) * window[i];
        qData[i] = (iqData.q[i] / 8388607.0) * window[i];
      }
    }
    
    // Compute FFT using DFT (simplified for demonstration)
    for (let k = 0; k < fftSize; k++) {
      let real = 0;
      let imag = 0;
      
      for (let n = 0; n < fftSize; n++) {
        const angle = -2 * Math.PI * k * n / fftSize;
        const cos_angle = Math.cos(angle);
        const sin_angle = Math.sin(angle);
        
        // Complex multiply: (i + jq) * (cos - jsin)
        real += iData[n] * cos_angle - qData[n] * sin_angle;
        imag += iData[n] * sin_angle + qData[n] * cos_angle;
      }
      
      // Power spectrum in dB
      const power = (real * real + imag * imag) / fftSize;
      spectrum[k] = 10 * Math.log10(Math.max(1e-10, power));
    }
    
    // Rearrange spectrum for display (DC in center)
    const displaySpectrum = new Float32Array(fftSize);
    for (let i = 0; i < fftSize / 2; i++) {
      displaySpectrum[i] = spectrum[i + fftSize / 2]; // Negative frequencies
      displaySpectrum[i + fftSize / 2] = spectrum[i]; // Positive frequencies
    }
    
    // Find min/max for auto-scaling
    let minDb = Infinity;
    let maxDb = -Infinity;
    for (let i = 0; i < fftSize; i++) {
      if (displaySpectrum[i] > -100) {
        minDb = Math.min(minDb, displaySpectrum[i]);
        maxDb = Math.max(maxDb, displaySpectrum[i]);
      }
    }
    
    // Default range if no valid data
    if (minDb === Infinity) {
      minDb = -80;
      maxDb = -20;
    }
    
    // Add some headroom
    const range = maxDb - minDb;
    minDb -= range * 0.1;
    maxDb += range * 0.1;
    
    // Draw spectrum with interpolation for smooth display
    for (let x = 0; x < width; x++) {
      // Map display position to FFT bin
      const bin = (x / width) * fftSize;
      const bin1 = Math.floor(bin);
      const bin2 = Math.min(bin1 + 1, fftSize - 1);
      const frac = bin - bin1;
      
      // Interpolate between bins
      const power = displaySpectrum[bin1] * (1 - frac) + displaySpectrum[bin2] * frac;
      
      // Map power to color intensity
      const intensity = Math.max(0, Math.min(255, 
                                             ((power - minDb) / (maxDb - minDb)) * 255
                                            ));
      
      // Enhanced color mapping for better visibility
      let r, g, b;
      if (intensity < 64) {
        // Very weak - dark blue to blue
        r = 0;
        g = 0;
        b = 20 + intensity;
      } else if (intensity < 128) {
        // Weak - blue to cyan
        const t = (intensity - 64) / 64;
        r = 0;
        g = 128 * t;
        b = 255 - 128 * t;
      } else if (intensity < 192) {
        // Medium - cyan to yellow
        const t = (intensity - 128) / 64;
        r = 255 * t;
        g = 128 + 127 * t;
        b = 128 * (1 - t);
      } else {
        // Strong - yellow to red
        const t = (intensity - 192) / 63;
        r = 255;
        g = 255 * (1 - t);
        b = 0;
      }
      
      ctx.fillStyle = `rgb(${Math.floor(r)}, ${Math.floor(g)}, ${Math.floor(b)})`;
      ctx.fillRect(x, height - 1, 1, 1);
    }
    
    // Add grid lines every 10kHz if needed
    if (Math.random() < 0.01) { // Occasional grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 0.5;
      
      for (let freq = -40; freq <= 40; freq += 10) {
        const x = ((freq + 48) / 96) * width;
        ctx.beginPath();
        ctx.moveTo(x, height - 1);
        ctx.lineTo(x, height - 3);
        ctx.stroke();
      }
    }
  }
  

  updateFilterEnvelope() {
    const envelope = document.getElementById('filterEnvelope');
    const info = document.getElementById('filterInfo');
    const description = document.getElementById('filterDescription');
    const waterfall = document.getElementById('waterfallCanvas');
    const tuningSlider = document.getElementById('tuningSlider');
    
    if (!envelope || !waterfall || !tuningSlider) return;
    
    const mode = this.dsp.mode || 'usb';
    const params = this.filterParams[mode];
    
    // Use the DISPLAY width for positioning elements, not canvas internal width
    const displayWidth = waterfall.offsetWidth || waterfall.width;
    
    // Get current tuning frequency from slider
    const tuningFreq = parseInt(tuningSlider.value || 0);
    
    // Calculate pixels per Hz based on display width
    const hzPerPixel = 96000 / displayWidth;
    
    // Center of display (0 Hz position)
    const centerPixel = displayWidth / 2;
    
    // Where the tuning indicator should be displayed
    const tuningPixel = centerPixel + (tuningFreq / hzPerPixel);
    
    // Filter edges in Hz (relative to baseband after shifting)
    let filterLowHz, filterHighHz;
    
    switch (mode) {
    case 'usb':
      filterLowHz = params.low;   // 200 Hz
      filterHighHz = params.high; // 3500 Hz
      break;
      
    case 'lsb':
      filterLowHz = params.low;   // -3500 Hz
      filterHighHz = params.high; // -200 Hz
      break;
      
    case 'cw':
      filterLowHz = params.offset + params.low;   // 350 Hz
      filterHighHz = params.offset + params.high; // 850 Hz
      break;
      
    case 'am':
      filterLowHz = params.low;   // -4000 Hz
      filterHighHz = params.high; // +4000 Hz
      break;
    }
    
    // Convert filter edges to pixel positions relative to tuning
    const leftPixel = tuningPixel + (filterLowHz / hzPerPixel);
    const rightPixel = tuningPixel + (filterHighHz / hzPerPixel);
    
    // Ensure correct order
    const minPixel = Math.min(leftPixel, rightPixel);
    const maxPixel = Math.max(leftPixel, rightPixel);
    
    // Clamp to display bounds
    const clampedLeft = Math.max(0, minPixel);
    const clampedRight = Math.min(displayWidth, maxPixel);
    const width = clampedRight - clampedLeft;
    
    console.log('Filter envelope update:', {
      displayWidth: displayWidth,
      tuningFreq: tuningFreq,
      tuningPixel: tuningPixel.toFixed(1),
      filterRange: `${filterLowHz} to ${filterHighHz} Hz`,
      pixelRange: `${clampedLeft.toFixed(1)} to ${clampedRight.toFixed(1)}px`,
      width: width.toFixed(1)
    });
    
    // Update envelope position using display coordinates
    envelope.style.left = `${clampedLeft}px`;
    envelope.style.width = `${width}px`;
    
    // Update envelope class
    envelope.className = `filter-envelope filter-envelope-${mode}`;
    
    // Update info text
    const bandwidth = Math.abs(filterHighHz - filterLowHz);
    info.textContent = `${mode.toUpperCase()}: ${Math.round(bandwidth)} Hz`;
    
    // Center info text on envelope
    info.style.left = `${clampedLeft + width/2}px`;
    info.style.transform = 'translateX(-50%)';
    
    // Update description
    if (description) {
      switch (mode) {
      case 'usb':
        description.textContent = `Upper Sideband: ${params.low}-${params.high} Hz above carrier`;
        break;
      case 'lsb':
        description.textContent = `Lower Sideband: ${Math.abs(params.high)}-${Math.abs(params.low)} Hz below carrier`;
        break;
      case 'cw':
        description.textContent = `CW: ${bandwidth} Hz @ ${params.offset} Hz tone`;
        break;
      case 'am':
        description.textContent = `AM: ±${Math.abs(params.high)} Hz`;
        break;
      }
    }
  }

  updateTuningIndicator(frequency) {
    const indicator = document.getElementById('tuningIndicator');
    const waterfall = document.getElementById('waterfallCanvas');
    
    if (indicator && waterfall) {
      // Use display width, not canvas internal width
      const displayWidth = waterfall.offsetWidth || waterfall.width;
      const hzPerPixel = 96000 / displayWidth;
      const centerPixel = displayWidth / 2;
      
      // Calculate pixel position for the tuning frequency
      const tuningPixel = centerPixel + (frequency / hzPerPixel);
      
      // Set position in pixels
      indicator.style.left = `${tuningPixel}px`;
      
      console.log('Tuning indicator:', {
	frequency: frequency,
	displayWidth: displayWidth,
	tuningPixel: tuningPixel.toFixed(1)
      });
      
      // Also update the filter envelope
      this.updateFilterEnvelope();
    }
  }

  initializeUI() {
    // Initialize frequency display
    this.updateFrequencyDisplay();
    
    // Set up control handlers
    this.setupControlHandlers();
    
    // Initialize band buttons
    this.updateBandDisplay();
    
    // Initialize waterfall frequency scale
    this.updateWaterfallScale();

    // Initialize tuning indicator to 0Hz
    this.updateTuningIndicator(0);
    
    // Initialize filter envelope
    this.updateFilterEnvelope();
    
    // Start telemetry updates
    this.startTelemetryUpdates();
  }
  
  updateWaterfallScale() {
    const scaleElement = document.getElementById('frequencyScale');
    if (!scaleElement) return;
    
    // Clear existing markers
    scaleElement.innerHTML = '';
    
    // Create frequency markers for ±48 kHz span
    const spanKHz = 96; // ±48 kHz
    const numMarkers = 9; // Every 12 kHz
    
    for (let i = 0; i < numMarkers; i++) {
      const freqOffset = -48 + (i * 12); // -48, -36, -24, -12, 0, +12, +24, +36, +48
      const position = (i / (numMarkers - 1)) * 100; // 0% to 100%
      
      const marker = document.createElement('div');
      marker.className = 'freq-marker';
      marker.style.position = 'absolute';
      marker.style.left = `${position}%`;
      marker.style.transform = 'translateX(-50%)';
      marker.style.fontSize = '10px';
      marker.style.color = '#666';
      
      const sign = freqOffset > 0 ? '+' : '';
      marker.textContent = `${sign}${freqOffset}k`;
      
      scaleElement.appendChild(marker);
    }
  }
  
  setupControlHandlers() {
    // Band selection buttons
    document.querySelectorAll('.band-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const band = e.target.dataset.band;
        this.setBand(band);
      });
    });
    
    // Mode buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const mode = e.target.dataset.mode;
        this.setMode(mode);
      });
    });
    
    // Demodulation mode buttons
    document.querySelectorAll('.demod-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        // Update active button
        document.querySelectorAll('.demod-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        // Set DSP mode
        const mode = e.target.dataset.mode;
        this.dsp.setMode(mode);
        
        // Update filter envelope visualization
        this.updateFilterEnvelope();
        
        console.log(`Demodulation mode changed to: ${mode}`);
      });
    });
    
    // Power slider
    const powerSlider = document.getElementById('powerSlider');
    if (powerSlider) {
      powerSlider.addEventListener('input', (e) => {
        this.setPower(parseInt(e.target.value));
      });
    }
    
    // Antenna selection
    const antennaSelect = document.getElementById('antennaSelect');
    if (antennaSelect) {
      antennaSelect.addEventListener('change', (e) => {
        this.setAntenna(parseInt(e.target.value));
      });
    }
    
    // Audio enable button
    const audioEnableBtn = document.getElementById('audioEnableBtn');
    if (audioEnableBtn) {
      let iqStreamStarted = false;
      
      audioEnableBtn.addEventListener('click', async () => {
        try {
          // Check if already enabled
          if (audioEnableBtn.classList.contains('active')) {
            // Disable audio - switch to standby mode
            await this.setMode('standby');
            
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
              this.websocket.send(JSON.stringify({ type: 'stopIqStream' }));
              console.log('Stopped I/Q stream');
            }
            if (this.dsp.audioContext) {
              await this.dsp.audioContext.suspend();
            }
            audioEnableBtn.textContent = '🔊 Enable Audio';
            audioEnableBtn.classList.remove('active');
            iqStreamStarted = false;
            console.log('Audio disabled, switched to standby mode');
            return;
          }
          
          // Create AudioContext if not already created
          const contextCreated = await this.dsp.createAudioContext();
          if (!contextCreated) {
            console.error('Failed to create AudioContext');
            return;
          }
          
          // Resume if suspended
          if (this.dsp.audioContext.state === 'suspended') {
            await this.dsp.audioContext.resume();
          }
          
          if (this.dsp.audioContext.state === 'running') {
            // Enable audio - switch to rx mode
            await this.setMode('rx');
            
            audioEnableBtn.textContent = '🔊 Audio Enabled';
            audioEnableBtn.classList.add('active');
            console.log('Audio enabled successfully, switched to RX mode, state:', this.dsp.audioContext.state);
            
            // Start I/Q stream now that DSP is ready
            if (!iqStreamStarted && this.websocket && this.websocket.readyState === WebSocket.OPEN) {
              this.websocket.send(JSON.stringify({ type: 'startIqStream' }));
              console.log('Started I/Q stream');
              iqStreamStarted = true;
            }
          } else {
            console.warn('AudioContext not running, state:', this.dsp.audioContext.state);
          }
        } catch (error) {
          console.error('Failed to enable audio:', error);
        }
      });
    }
    
    // Tuning control
    const tuningSlider = document.getElementById('tuningSlider');
    const tuningValue = document.getElementById('tuningValue');
    if (tuningSlider && tuningValue) {
      tuningSlider.addEventListener('input', (e) => {
        const frequency = parseInt(e.target.value);
        this.dsp.setTuning(frequency);
        
        // Update display
        const sign = frequency >= 0 ? '+' : '';
        const freqKHz = (frequency / 1000).toFixed(1);
        tuningValue.textContent = `${sign}${freqKHz} kHz`;
        
        // Update waterfall tuning indicator position
        this.updateTuningIndicator(frequency);
        
        // Update filter envelope position
        this.updateFilterEnvelope();
        
        console.log('Tuning changed to:', frequency, 'Hz');
      });
    }
    
    // Emergency stop and tuning keys
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.emergencyStop();
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault(); // Prevent page scrolling
        
        const tuningSlider = document.getElementById('tuningSlider');
        const tuningValue = document.getElementById('tuningValue');
        
        if (tuningSlider && tuningValue) {
          let currentFreq = parseInt(tuningSlider.value);
          const step = parseInt(tuningSlider.step);
          
          if (e.key === 'ArrowLeft') {
            currentFreq = Math.max(parseInt(tuningSlider.min), currentFreq - step);
          } else if (e.key === 'ArrowRight') {
            currentFreq = Math.min(parseInt(tuningSlider.max), currentFreq + step);
          }
          
          // Update slider and DSP
          tuningSlider.value = currentFreq;
          this.dsp.setTuning(currentFreq);

          // Update display
          const sign = currentFreq >= 0 ? '+' : '';
          const freqKHz = (currentFreq / 1000).toFixed(1);
          tuningValue.textContent = `${sign}${freqKHz} kHz`;

          // Update waterfall tuning indicator position
          this.updateTuningIndicator(currentFreq);
          
          // Update filter envelope position
          this.updateFilterEnvelope();
        }
      }
    });
  }
  
  async setBand(band) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/rf/band`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ band })
      });
      
      if (response.ok) {
        this.currentBand = band;
        this.updateBandDisplay();
        
        // Get the new frequency for this band
        const freqResponse = await fetch(`${this.apiBaseUrl}/rf/frequency`);
        if (freqResponse.ok) {
          const freqData = await freqResponse.json();
          this.currentFreq = freqData.frequency;
          this.updateFrequencyDisplay();
        }
      }
    } catch (error) {
      console.error('Failed to set band:', error);
    }
  }
  
  async setMode(mode) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/rf/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      });
      
      if (response.ok) {
        this.currentMode = mode;
        this.updateModeDisplay();
        
        // Update DSP mode based on radio mode
        if (mode === 'rx') {
          // Keep current demodulation mode
          this.dsp.setTuning(0); // Start at baseband center frequency
        }
      }
    } catch (error) {
      console.error('Failed to set mode:', error);
    }
  }
  
  async setPower(power) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/rf/power`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ power })
      });
      
      if (response.ok) {
        document.getElementById('powerValue').textContent = `${power}W`;
      }
    } catch (error) {
      console.error('Failed to set power:', error);
    }
  }
  
  async setAntenna(antenna) {
    try {
      await fetch(`${this.apiBaseUrl}/rf/antenna`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ antenna })
      });
    } catch (error) {
      console.error('Failed to set antenna:', error);
    }
  }
  
  async emergencyStop() {
    try {
      await fetch(`${this.apiBaseUrl}/emergency-stop`, {
        method: 'POST'
      });
      console.log('Emergency stop activated');
    } catch (error) {
      console.error('Emergency stop failed:', error);
    }
  }
  
  updateFrequencyDisplay() {
    const freqDisplay = document.getElementById('frequencyDisplay');
    if (freqDisplay) {
      const freqMHz = (this.currentFreq / 1000000).toFixed(3);
      freqDisplay.querySelector('.freq-value').textContent = freqMHz;
    }
  }
  
  updateBandDisplay() {
    // Update band buttons
    document.querySelectorAll('.band-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.band === this.currentBand);
    });
    
    // Update header display
    const bandDisplay = document.getElementById('currentBand');
    if (bandDisplay) {
      bandDisplay.textContent = this.currentBand;
    }
  }
  
  updateModeDisplay() {
    // Update mode buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mode === this.currentMode);
    });
    
    // Update header display
    const modeDisplay = document.getElementById('currentMode');
    if (modeDisplay) {
      modeDisplay.textContent = this.currentMode.toUpperCase();
    }
  }
  
  startTelemetryUpdates() {
    setInterval(async () => {
      try {
        const response = await fetch(`${this.apiBaseUrl}/telemetry`);
        if (response.ok) {
          const telemetry = await response.json();
          this.updateTelemetryDisplay(telemetry);
        }
      } catch (error) {
        console.error('Telemetry update failed:', error);
      }
    }, 1000); // Update every second
  }
  
  updateTelemetryDisplay(telemetry) {
    // Update power meter
    const forwardPower = document.getElementById('forwardPowerMeter');
    const forwardValue = document.getElementById('forwardPowerValue');
    if (forwardPower && forwardValue) {
      const powerPercent = (telemetry.forwardPower / 100) * 100;
      forwardPower.style.width = `${powerPercent}%`;
      forwardValue.textContent = `${telemetry.forwardPower.toFixed(1)}W`;
    }
    
    // Update SWR meter
    const swrMeter = document.getElementById('swrMeter');
    const swrValue = document.getElementById('swrValue');
    if (swrMeter && swrValue) {
      const swrPercent = Math.min(((telemetry.swr - 1) / 2) * 100, 100);
      swrMeter.style.width = `${swrPercent}%`;
      swrValue.textContent = `${telemetry.swr.toFixed(1)}:1`;
    }
    
    // Update temperature meter
    const tempMeter = document.getElementById('tempMeter');
    const tempValue = document.getElementById('tempValue');
    if (tempMeter && tempValue) {
      const tempPercent = (telemetry.temperature / 100) * 100;
      tempMeter.style.width = `${tempPercent}%`;
      tempValue.textContent = `${telemetry.temperature.toFixed(0)}°C`;
    }
  }
  
  hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    const nexrigApp = document.getElementById('nexrigApp');
    
    if (loadingScreen) {
      loadingScreen.classList.add('hidden');
    }
    if (nexrigApp) {
      nexrigApp.classList.add('loaded');
    }
  }

  checkSIMDSupport() {
    // Chrome 91+ has SIMD enabled by default
    const chromeMatch = navigator.userAgent.match(/Chrome\/(\d+)/);
    const chromeVersion = chromeMatch ? parseInt(chromeMatch[1]) : 0;
    
    const simdSupported = chromeVersion >= 91;
    
    console.log(`Chrome version: ${chromeVersion}, SIMD supported: ${simdSupported}`);
    this.updateSIMDIndicator(simdSupported);
    
    return simdSupported;
  }

  updateSIMDIndicator(supported) {
    const indicator = document.getElementById('simdStatus');
    if (indicator) {
      const indicatorDot = indicator.querySelector('.indicator');
      if (supported) {
        indicatorDot.style.background = '#00e676';
        indicator.title = 'SIMD: Supported';
        console.log('SIMD indicator set to GREEN');
      } else {
        indicatorDot.style.background = '#666';
        indicator.title = 'SIMD: Not supported';
        console.log('SIMD indicator set to GREY');
      }
    } else {
      console.warn('SIMD indicator element not found in DOM');
    }
  }

  updateWASMIndicator(active) {
    const indicator = document.getElementById('wasmStatus');
    if (indicator) {
      const indicatorDot = indicator.querySelector('.indicator');
      if (active) {
        indicatorDot.style.background = '#00e676';
        indicator.title = 'WASM: Active';
      } else {
        indicatorDot.style.background = '#ff9800';
        indicator.title = 'WASM: Using JavaScript fallback';
      }
    }
  }
}
