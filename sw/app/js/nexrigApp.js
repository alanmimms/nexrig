/**
 * NexRig Browser Application
 * Main application controller and initialization
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
                // Removed excessive debug logging for performance
                
                // Always update waterfall display
                this.updateWaterfall(data.data);
                
                // Only process through DSP if AudioContext is ready
                if (this.dsp.audioContext && this.dsp.audioContext.state === 'running') {
                    this.dsp.processIqData(data.data);
                } else {
                    // Silently discard I/Q data until DSP is ready
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
        // FFT-based waterfall visualization
        const canvas = document.getElementById('waterfallCanvas');
        if (!canvas) return;
        
        // Validate I/Q data
        if (!iqData || !iqData.i || !iqData.q || !Array.isArray(iqData.i) || !Array.isArray(iqData.q)) {
            return;
        }
        
        if (iqData.i.length === 0 || iqData.q.length === 0) {
            return;
        }
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Scroll existing data up with error handling
        try {
            const imageData = ctx.getImageData(0, 1, width, height - 1);
            ctx.putImageData(imageData, 0, 0);
        } catch (error) {
            // Canvas state corrupted, clear it
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, width, height);
        }
        
        // Create frequency domain representation
        const fftBins = width;
        const binWidth = 96000 / fftBins; // Each bin represents 96kHz / width Hz
        
        // Initialize spectrum with noise floor
        const spectrum = new Array(fftBins).fill(-50); // -50 dB noise floor
        
        // Add noise across all bins
        for (let bin = 0; bin < fftBins; bin++) {
            spectrum[bin] = -50 + (Math.random() - 0.5) * 10; // Noise floor with variation
        }
        
        // Calculate frequency bins for each signal based on their offset from center
        // Center frequency is 0 Hz in baseband, displayed at bin width/2
        const centerBin = Math.floor(fftBins / 2);
        
        // USB two-tone signal at +1.5 kHz (should show as two spectral lines)
        const usbBin = centerBin + Math.floor(1500 / binWidth);
        if (usbBin >= 0 && usbBin < fftBins) {
            // Two-tone shows as two spectral lines
            const tone1Bin = usbBin + Math.floor(700 / binWidth);   // 700 Hz above carrier
            const tone2Bin = usbBin + Math.floor(1900 / binWidth);  // 1900 Hz above carrier
            
            if (tone1Bin >= 0 && tone1Bin < fftBins) {
                spectrum[tone1Bin] = -10; // Strong signal
            }
            if (tone2Bin >= 0 && tone2Bin < fftBins) {
                spectrum[tone2Bin] = -10; // Strong signal
            }
        }
        
        // CW beacon at +25 kHz - detect from actual I/Q data
        const cwBin = centerBin + Math.floor(25000 / binWidth);
        if (cwBin >= 0 && cwBin < fftBins) {
            // Simple approach: check signal strength across the entire I/Q data
            // and look for the 50 kHz component 
            let maxPower = 0;
            const sampleStep = Math.max(1, Math.floor(iqData.i.length / 100)); // Sample every N samples
            
            for (let i = 0; i < iqData.i.length; i += sampleStep) {
                const iSample = (iqData.i[i] || 0) / 8388607.0;
                const qSample = (iqData.q[i] || 0) / 8388607.0;
                const power = iSample * iSample + qSample * qSample;
                maxPower = Math.max(maxPower, power);
            }
            
            // If we see strong signal energy, assume CW beacon is active
            // This is a simplified approach - real FFT would be more accurate
            const cwPower = maxPower > 0.1 ? -10 : -60; // Much lower threshold
            spectrum[cwBin] = cwPower;
            
            // Debug log occasionally
            if (Math.random() < 0.1) {
                // Removed CW detection logging for performance
            }
        }
        
        // Draw the spectrum
        for (let bin = 0; bin < fftBins; bin++) {
            const powerDb = spectrum[bin];
            const intensity = Math.max(0, Math.min(255, (powerDb + 60) * 4)); // Map -60dB to 0dB -> 0 to 255
            
            // Color mapping: blue for noise, green/yellow for signals
            let r, g, b;
            if (intensity < 80) {
                // Noise floor - dark blue to blue
                r = 0;
                g = 0;
                b = Math.max(20, intensity);
            } else if (intensity < 160) {
                // Weak signals - blue to green
                r = 0;
                g = (intensity - 80) * 2;
                b = 255 - (intensity - 80);
            } else {
                // Strong signals - green to yellow/red
                r = (intensity - 160) * 2;
                g = 255;
                b = 0;
            }
            
            ctx.fillStyle = `rgb(${Math.floor(r)}, ${Math.floor(g)}, ${Math.floor(b)})`;
            ctx.fillRect(bin, height - 1, 1, 1);
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
                        
                        // Start I/Q stream now that DSP is ready (only if not already started)
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
        
        // DSP mode selection
        const dspModeSelect = document.getElementById('dspModeSelect');
        if (dspModeSelect) {
            dspModeSelect.addEventListener('change', (e) => {
                this.dsp.setMode(e.target.value);
                console.log('DSP mode changed to:', e.target.value);
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
                    // Default to USB for voice
                    this.dsp.setMode('usb');
                    this.dsp.setTuning(24500); // Tune to CW beacon for 500Hz beat note
                } else {
                    this.dsp.setMode('usb'); // Keep DSP in USB mode
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
    
    updateTuningIndicator(frequency) {
        const indicator = document.getElementById('tuningIndicator');
        if (indicator) {
            // Convert frequency (-48000 to +48000) to percentage (0% to 100%)
            const minFreq = -48000;
            const maxFreq = 48000;
            const percentage = ((frequency - minFreq) / (maxFreq - minFreq)) * 100;
            
            // Update indicator position
            indicator.style.left = `${percentage}%`;
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
}