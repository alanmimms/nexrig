/**
 * @file nexrig-app.js
 * @brief Main NexRig Browser Application
 * 
 * This is the main application class for the NexRig browser interface.
 * It coordinates all UI components, manages the setbox system, and
 * communicates with the STM32 hardware through REST APIs.
 * 
 * The browser implements ALL policy decisions - the STM32 provides
 * only hardware mechanism through its REST API.
 * 
 * @copyright 2025 NexRig Project - MIT License
 */

import { HardwareAPI } from './hardware-api.js';
import { StreamManager } from './stream-manager.js';
import { SetboxManager } from './setbox-manager.js';
import { WaterfallDisplay } from './waterfall-display.js';
import { SpectrumAnalyzer } from './spectrum-analyzer.js';
import { UIController } from './ui-controller.js';
import { AdvancedDSP } from './advanced-dsp.js';

/**
 * @class NexRigApplication
 * @brief Main application coordinator
 * 
 * This class orchestrates all aspects of the NexRig user interface:
 * - Hardware communication through REST API
 * - Real-time data streaming via WebSockets
 * - Setbox management and inheritance
 * - DSP processing and visualization
 * - User interface coordination
 */
export class NexRigApplication {
  constructor() {
    // Core system components
    this.hardwareAPI = new HardwareAPI();
    this.streamManager = new StreamManager();
    this.setboxManager = new SetboxManager();
    this.waterfallDisplay = new WaterfallDisplay();
    this.spectrumAnalyzer = new SpectrumAnalyzer();
    this.uiController = new UIController();
    this.advancedDSP = new AdvancedDSP();
    
    // Application state
    this.isInitialized = false;
    this.isConnected = false;
    this.currentState = {
      frequency: 14200000,   // 20m band center
      band: '20m',
      mode: 'rx',
      power: 10.0,
      antenna: 1
    };
    
    // Performance monitoring
    this.performanceMetrics = {
      frameRate: 60,
      latency: 0,
      cpuUsage: 0,
      memoryUsage: 0
    };
    
    // Event listeners registry
    this.eventListeners = new Map();
    
    // Animation frame tracking
    this.animationFrameId = null;
    this.lastFrameTime = 0;
    
    console.log('NexRig Application initialized');
  }
  
  /**
   * @brief Initialize the complete application
   * 
   * This method coordinates the startup sequence:
   * 1. Connect to STM32 hardware
   * 2. Initialize all UI components
   * 3. Load user configurations
   * 4. Start real-time processing loops
   */
  async initialize() {
    try {
      this.updateLoadingStatus('Connecting to STM32 hardware...');
      
      // Connect to hardware API
      await this.hardwareAPI.connect();
      this.isConnected = true;
      
      this.updateLoadingStatus('Initializing data streams...');
      
      // Connect to real-time data streams
      await this.streamManager.connect();
      
      this.updateLoadingStatus('Loading user configurations...');
      
      // Load setbox configurations and user preferences
      await this.setboxManager.loadUserConfigurations();
      
      this.updateLoadingStatus('Initializing DSP engine...');
      
      // Initialize advanced DSP processing
      await this.advancedDSP.initialize();
      
      this.updateLoadingStatus('Starting user interface...');
      
      // Initialize UI components
      this.initializeUserInterface();
      
      this.updateLoadingStatus('Configuring event handlers...');
      
      // Set up event handling
      this.setupEventHandlers();
      
      this.updateLoadingStatus('Getting hardware status...');
      
      // Get initial hardware state
      await this.updateHardwareStatus();
      
      this.updateLoadingStatus('Starting real-time processing...');
      
      // Start real-time processing loops
      this.startRealTimeProcessing();
      
      // Mark as fully initialized
      this.isInitialized = true;
      
      // Hide loading screen and show main application
      this.showMainApplication();
      
      console.log('NexRig Application fully initialized and ready');
      
    } catch (error) {
      console.error('Failed to initialize NexRig application:', error);
      this.showErrorMessage('Failed to connect to NexRig hardware', error.message);
    }
  }
  
  /**
   * @brief Update loading screen status
   * @param {string} status Status message to display
   */
  updateLoadingStatus(status) {
    const loadingDetails = document.getElementById('loadingDetails');
    if (loadingDetails) {
      loadingDetails.textContent = status;
    }
    console.log(`Loading: ${status}`);
  }
  
  /**
   * @brief Initialize all user interface components
   */
  initializeUserInterface() {
    // Initialize waterfall display
    this.waterfallDisplay.initialize(document.getElementById('waterfallCanvas'));
    
    // Initialize spectrum analyzer
    this.spectrumAnalyzer.initialize(document.getElementById('spectrumCanvas'));
    
    // Initialize UI controller with all interactive elements
    this.uiController.initialize({
      frequencyDisplay: document.getElementById('frequencyDisplay'),
      bandButtons: document.querySelectorAll('.band-btn'),
      modeButtons: document.querySelectorAll('.mode-btn'),
      powerSlider: document.getElementById('powerSlider'),
      antennaSelect: document.getElementById('antennaSelect'),
      meters: {
        forwardPower: document.getElementById('forwardPowerMeter'),
        swr: document.getElementById('swrMeter'),
        temperature: document.getElementById('tempMeter')
      }
    });
    
    // Initialize setbox UI components
    this.setboxManager.initializeUI({
      activeSetboxName: document.getElementById('activeSetboxName'),
      setboxInheritance: document.getElementById('setboxInheritance'),
      setboxList: document.getElementById('setboxList'),
      newSetboxBtn: document.getElementById('newSetboxBtn'),
      saveSetboxBtn: document.getElementById('saveSetboxBtn'),
      deleteSetboxBtn: document.getElementById('deleteSetboxBtn')
    });
  }
  
  /**
   * @brief Set up all event handlers for user interaction
   */
  setupEventHandlers() {
    // Frequency control via waterfall display
    this.waterfallDisplay.onFrequencyChange = (frequencyHz) => {
      this.setFrequency(frequencyHz);
    };
    
    // Band selection buttons
    document.querySelectorAll('.band-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const band = e.target.dataset.band;
        this.setBand(band);
      });
    });
    
    // Mode control buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const mode = e.target.dataset.mode;
        this.setMode(mode);
      });
    });
    
    // Power control slider
    const powerSlider = document.getElementById('powerSlider');
    powerSlider.addEventListener('input', (e) => {
      const power = parseFloat(e.target.value);
      this.setPower(power);
    });
    
    // Antenna selection
    const antennaSelect = document.getElementById('antennaSelect');
    antennaSelect.addEventListener('change', (e) => {
      const antenna = parseInt(e.target.value);
      this.setAntenna(antenna);
    });
    
    // Waterfall controls
    document.getElementById('waterfallZoomIn').addEventListener('click', () => {
      this.waterfallDisplay.zoomIn();
    });
    
    document.getElementById('waterfallZoomOut').addEventListener('click', () => {
      this.waterfallDisplay.zoomOut();
    });
    
    document.getElementById('waterfallPause').addEventListener('click', () => {
      this.waterfallDisplay.togglePause();
    });
    
    // Setbox management
    this.setboxManager.onSetboxChanged = (setboxName) => {
      this.activateSetbox(setboxName);
    };
    
    this.setboxManager.onSetboxSaved = (setboxName, configuration) => {
      console.log(`Setbox '${setboxName}' saved with configuration:`, configuration);
    };
    
    // Emergency stop handler
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && e.ctrlKey) {
        this.emergencyStop();
      }
    });
    
    // Window visibility for performance optimization
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pauseRealTimeProcessing();
      } else {
        this.resumeRealTimeProcessing();
      }
    });
    
    // Data stream handlers
    this.streamManager.onIQData = (iqData) => {
      this.handleIQData(iqData);
    };
    
    this.streamManager.onSpectrumData = (spectrumData) => {
      this.handleSpectrumData(spectrumData);
    };
    
    this.streamManager.onHardwareEvent = (event) => {
      this.handleHardwareEvent(event);
    };
  }
  
  /**
   * @brief Start real-time processing loops
   */
  startRealTimeProcessing() {
    // Main animation loop for UI updates
    const processFrame = (timestamp) => {
      if (!this.isInitialized) return;
      
      const deltaTime = timestamp - this.lastFrameTime;
      this.lastFrameTime = timestamp;
      
      // Update performance metrics
      this.updatePerformanceMetrics(deltaTime);
      
      // Process any pending DSP operations
      this.advancedDSP.processFrame();
      
      // Update waterfall display
      this.waterfallDisplay.render();
      
      // Update spectrum analyzer
      this.spectrumAnalyzer.render();
      
      // Update UI meters and indicators
      this.uiController.updateDisplays();
      
      // Schedule next frame
      this.animationFrameId = requestAnimationFrame(processFrame);
    };
    
    this.animationFrameId = requestAnimationFrame(processFrame);
    
    console.log('Real-time processing loops started');
  }
  
  /**
   * @brief Pause real-time processing (when window hidden)
   */
  pauseRealTimeProcessing() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }
  
  /**
   * @brief Resume real-time processing
   */
  resumeRealTimeProcessing() {
    if (!this.animationFrameId && this.isInitialized) {
      this.startRealTimeProcessing();
    }
  }
  
  /**
   * @brief Handle incoming I/Q data from hardware
   * @param {Object} iqData I/Q sample data
   */
  handleIQData(iqData) {
    // Send to advanced DSP for processing
    const processedData = this.advancedDSP.processIQSamples(iqData);
    
    // Update waterfall display
    this.waterfallDisplay.addIQData(processedData);
    
    // Update spectrum analyzer
    this.spectrumAnalyzer.addIQData(processedData);
  }
  
  /**
   * @brief Handle spectrum data from hardware
   * @param {Object} spectrumData FFT spectrum data
   */
  handleSpectrumData(spectrumData) {
    this.spectrumAnalyzer.updateSpectrum(spectrumData);
  }
  
  /**
   * @brief Handle hardware events from STM32
   * @param {Object} event Hardware event notification
   */
  handleHardwareEvent(event) {
    switch (event.type) {
      case 'protection_triggered':
        this.handleProtectionEvent(event);
        break;
        
      case 'rf_state_change':
        this.handleRFStateChange(event);
        break;
        
      case 'hardware_error':
        this.handleHardwareError(event);
        break;
        
      default:
        console.log('Unknown hardware event:', event);
    }
  }
  
  /**
   * @brief Set operating frequency
   * @param {number} frequencyHz Frequency in Hz
   */
  async setFrequency(frequencyHz) {
    try {
      const response = await this.hardwareAPI.setFrequency(frequencyHz);
      
      if (response.success) {
        this.currentState.frequency = frequencyHz;
        this.uiController.updateFrequencyDisplay(frequencyHz);
        
        // Update active setbox if needed
        this.setboxManager.updateCurrentParameter('frequency', frequencyHz);
      }
      
    } catch (error) {
      console.error('Failed to set frequency:', error);
      this.showErrorMessage('Frequency Error', error.message);
    }
  }
  
  /**
   * @brief Set amateur radio band
   * @param {string} band Band designation (e.g., "20m")
   */
  async setBand(band) {
    try {
      const response = await this.hardwareAPI.setBand(band);
      
      if (response.success) {
        this.currentState.band = band;
        this.uiController.updateBandDisplay(band);
        
        // Band changes often require frequency adjustment
        const bandFreq = this.getBandCenterFrequency(band);
        if (bandFreq) {
          await this.setFrequency(bandFreq);
        }
        
        // Update active setbox
        this.setboxManager.updateCurrentParameter('band', band);
      }
      
    } catch (error) {
      console.error('Failed to set band:', error);
      this.showErrorMessage('Band Error', error.message);
    }
  }
  
  /**
   * @brief Set operating mode
   * @param {string} mode Operating mode ("rx", "tx", "standby")
   */
  async setMode(mode) {
    try {
      const response = await this.hardwareAPI.setMode(mode);
      
      if (response.success) {
        this.currentState.mode = mode;
        this.uiController.updateModeDisplay(mode);
        
        // Update active setbox
        this.setboxManager.updateCurrentParameter('mode', mode);
      }
      
    } catch (error) {
      console.error('Failed to set mode:', error);
      this.showErrorMessage('Mode Error', error.message);
    }
  }
  
  /**
   * @brief Set transmit power
   * @param {number} powerWatts Power in watts
   */
  async setPower(powerWatts) {
    try {
      const response = await this.hardwareAPI.setPower(powerWatts);
      
      if (response.success) {
        this.currentState.power = powerWatts;
        this.uiController.updatePowerDisplay(powerWatts);
        
        // Update active setbox
        this.setboxManager.updateCurrentParameter('power', powerWatts);
      }
      
    } catch (error) {
      console.error('Failed to set power:', error);
      this.showErrorMessage('Power Error', error.message);
    }
  }
  
  /**
   * @brief Set antenna selection
   * @param {number} antenna Antenna number (1-4)
   */
  async setAntenna(antenna) {
    try {
      const response = await this.hardwareAPI.setAntenna(antenna);
      
      if (response.success) {
        this.currentState.antenna = antenna;
        this.uiController.updateAntennaDisplay(antenna);
        
        // Update active setbox
        this.setboxManager.updateCurrentParameter('antenna', antenna);
      }
      
    } catch (error) {
      console.error('Failed to set antenna:', error);
      this.showErrorMessage('Antenna Error', error.message);
    }
  }
  
  /**
   * @brief Activate a setbox configuration
   * @param {string} setboxName Name of setbox to activate
   */
  async activateSetbox(setboxName) {
    try {
      const configuration = this.setboxManager.resolveSetboxConfiguration(setboxName);
      
      // Apply all configuration parameters to hardware
      if (configuration.frequency) {
        await this.setFrequency(configuration.frequency);
      }
      
      if (configuration.band) {
        await this.setBand(configuration.band);
      }
      
      if (configuration.mode) {
        await this.setMode(configuration.mode);
      }
      
      if (configuration.power) {
        await this.setPower(configuration.power);
      }
      
      if (configuration.antenna) {
        await this.setAntenna(configuration.antenna);
      }
      
      // Update UI to show active setbox
      this.setboxManager.setActiveSetbox(setboxName);
      
      console.log(`Activated setbox: ${setboxName}`, configuration);
      
    } catch (error) {
      console.error('Failed to activate setbox:', error);
      this.showErrorMessage('Setbox Error', error.message);
    }
  }
  
  /**
   * @brief Get hardware status from STM32
   */
  async updateHardwareStatus() {
    try {
      const rfStatus = await this.hardwareAPI.getRFStatus();
      const paStatus = await this.hardwareAPI.getPowerAmplifierStatus();
      const protectionStatus = await this.hardwareAPI.getProtectionStatus();
      
      // Update current state from hardware
      this.currentState.frequency = rfStatus.frequency_hz;
      this.currentState.band = rfStatus.band;
      this.currentState.mode = rfStatus.mode;
      this.currentState.power = paStatus.target_power_watts;
      this.currentState.antenna = rfStatus.antenna;
      
      // Update UI displays
      this.uiController.updateAllDisplays(this.currentState);
      
      // Update status indicators
      this.updateStatusIndicators(rfStatus, paStatus, protectionStatus);
      
    } catch (error) {
      console.error('Failed to get hardware status:', error);
      this.updateConnectionStatus(false);
    }
  }
  
  /**
   * @brief Update system status indicators
   */
  updateStatusIndicators(rfStatus, paStatus, protectionStatus) {
    const indicators = {
      rf: rfStatus.pll_locked && rfStatus.mode !== 'error',
      pa: paStatus.operational && !paStatus.protection_active,
      fpga: rfStatus.fpga_responsive,
      connection: this.isConnected
    };
    
    this.uiController.updateStatusIndicators(indicators);
  }
  
  /**
   * @brief Emergency stop - immediate safe state
   */
  async emergencyStop() {
    try {
      await this.hardwareAPI.emergencyStop();
      
      // Show emergency overlay
      const overlay = document.getElementById('emergencyOverlay');
      overlay.classList.remove('hidden');
      
      // Disable all controls
      this.uiController.disableAllControls();
      
      console.log('EMERGENCY STOP ACTIVATED');
      
    } catch (error) {
      console.error('Emergency stop failed:', error);
    }
  }
  
  /**
   * @brief Show main application interface
   */
  showMainApplication() {
    const loadingScreen = document.getElementById('loadingScreen');
    const nexrigApp = document.getElementById('nexrigApp');
    
    loadingScreen.classList.add('hidden');
    nexrigApp.classList.add('loaded');
  }
  
  /**
   * @brief Show error message to user
   * @param {string} title Error title
   * @param {string} message Error details
   */
  showErrorMessage(title, message) {
    // Create error dialog or notification
    console.error(`${title}: ${message}`);
    
    // Update loading screen with error
    const loadingText = document.querySelector('.loading-text');
    const loadingDetails = document.getElementById('loadingDetails');
    
    if (loadingText) loadingText.textContent = `❌ ${title}`;
    if (loadingDetails) loadingDetails.textContent = message;
  }
  
  /**
   * @brief Get center frequency for a band
   * @param {string} band Band designation
   * @returns {number|null} Center frequency in Hz
   */
  getBandCenterFrequency(band) {
    const frequencies = {
      '160m': 1900000,
      '80m': 3750000,
      '40m': 7150000,
      '20m': 14200000,
      '17m': 18118000,
      '15m': 21225000,
      '12m': 24940000,
      '10m': 28850000,
      '6m': 52000000,
      '2m': 146000000
    };
    
    return frequencies[band] || null;
  }
  
  /**
   * @brief Update performance metrics
   * @param {number} deltaTime Time since last frame in ms
   */
  updatePerformanceMetrics(deltaTime) {
    // Calculate frame rate
    this.performanceMetrics.frameRate = 1000 / deltaTime;
    
    // Update performance display if visible
    if (this.performanceMetrics.frameRate < 30) {
      console.warn(`Low frame rate: ${this.performanceMetrics.frameRate.toFixed(1)} fps`);
    }
  }
  
  /**
   * @brief Cleanup and shutdown
   */
  destroy() {
    // Cancel animation frame
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    
    // Disconnect from hardware
    this.streamManager.disconnect();
    this.hardwareAPI.disconnect();
    
    // Cleanup UI components
    this.waterfallDisplay.destroy();
    this.spectrumAnalyzer.destroy();
    
    console.log('NexRig Application destroyed');
  }
}