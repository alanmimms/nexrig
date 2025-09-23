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
                // Debug: Check what we're actually receiving
                console.log('Received I/Q data structure:', data);
                console.log('data.data:', data.data);
                console.log('data.data.i:', data.data?.i);
                console.log('Is data.data.i an array?', Array.isArray(data.data?.i));
                console.log('data.data.i length:', data.data?.i?.length);
                
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
        // Simple waterfall visualization
        const canvas = document.getElementById('waterfallCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Scroll existing data up
        const imageData = ctx.getImageData(0, 1, width, height - 1);
        ctx.putImageData(imageData, 0, 0);
        
        // Draw new line at bottom
        const fftSize = Math.min(iqData.i.length, width);
        for (let i = 0; i < fftSize; i++) {
            const power = Math.sqrt(iqData.i[i] * iqData.i[i] + iqData.q[i] * iqData.q[i]);
            const intensity = Math.min(255, power * 500); // Scale for visibility
            
            ctx.fillStyle = `rgb(${intensity}, ${intensity/2}, ${255-intensity})`;
            ctx.fillRect(i, height - 1, 1, 1);
        }
    }
    
    initializeUI() {
        // Initialize frequency display
        this.updateFrequencyDisplay();
        
        // Set up control handlers
        this.setupControlHandlers();
        
        // Initialize band buttons
        this.updateBandDisplay();
        
        // Start telemetry updates
        this.startTelemetryUpdates();
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
                        // Disable audio
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
                        audioEnableBtn.textContent = '🔊 Audio Enabled';
                        audioEnableBtn.classList.add('active');
                        console.log('Audio enabled successfully, state:', this.dsp.audioContext.state);
                        
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
        
        // Emergency stop
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.emergencyStop();
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
                    this.dsp.setTuning(1500); // Tune to the USB signal
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