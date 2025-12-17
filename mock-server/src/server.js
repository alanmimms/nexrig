/**
 * Mock STM32 Server for NexRig Development
 * 
 * Simulates the STM32H753's REST API and WebSocket streaming
 * for development without hardware.
 * Includes CBOR protocol support and TX loopback
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { encode, decode } from 'cbor-x';

import { RfController } from './rfController.js';
import { IqStreamGenerator } from './iqStreamGenerator.js';
import { SystemStatus } from './systemStatus.js';
import { CborHandler } from './cborHandler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3000;
const WS_PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Serve the browser app
app.use('/app', express.static(path.join(__dirname, '../../sw/app')));

// Mock hardware instances
const rfController = new RfController();
const iqGenerator = new IqStreamGenerator();
const systemStatus = new SystemStatus();

// Radio mode state: 'standby', 'rx', 'tx'
let radioMode = 'standby';

// TX recording storage
const txRecordings = [];

// Root redirect to app
app.get('/', (req, res) => {
  res.redirect('/app/');
});

// REST API Routes

// System status
app.get('/api/status', (req, res) => {
  res.json(systemStatus.getStatus());
});

// RF Control
app.get('/api/rf/frequency', (req, res) => {
  res.json({ frequency: rfController.getFrequency() });
});

app.post('/api/rf/frequency', (req, res) => {
  const { frequency } = req.body;
  if (frequency && frequency >= 1800000 && frequency <= 54000000) {
    rfController.setFrequency(frequency);
    res.json({ success: true, frequency: rfController.getFrequency() });
  } else {
    res.status(400).json({ error: 'Invalid frequency' });
  }
});

// Band selection
app.get('/api/rf/band', (req, res) => {
  res.json({ band: rfController.getBand() });
});

app.post('/api/rf/band', (req, res) => {
  const { band } = req.body;
  if (rfController.setBand(band)) {
    res.json({ success: true, band: rfController.getBand() });
  } else {
    res.status(400).json({ error: 'Invalid band' });
  }
});

// Mode control
app.get('/api/rf/mode', (req, res) => {
  res.json({ mode: rfController.getMode() });
});

app.post('/api/rf/mode', (req, res) => {
  const { mode } = req.body;
  console.log('Mode API called with:', mode, 'Type:', typeof mode);
  if (['rx', 'tx', 'standby'].includes(mode)) {
    // Update both rfController and global radioMode state
    rfController.setMode(mode);
    radioMode = mode;
    
    // Update system status for TX
    systemStatus.setTxActive(mode === 'tx');
    
    console.log(`Radio mode changed to: ${radioMode}`);
    res.json({ success: true, mode: rfController.getMode() });
  } else {
    console.log('Invalid mode rejected:', mode);
    res.status(400).json({ error: 'Invalid mode' });
  }
});

// Power control
app.get('/api/rf/power', (req, res) => {
  res.json({ power: rfController.getPower() });
});

app.post('/api/rf/power', (req, res) => {
  const { power } = req.body;
  if (power >= 1 && power <= 100) {
    rfController.setPower(power);
    res.json({ success: true, power: rfController.getPower() });
  } else {
    res.status(400).json({ error: 'Invalid power level' });
  }
});

// Antenna selection
app.get('/api/rf/antenna', (req, res) => {
  res.json({ antenna: rfController.getAntenna() });
});

app.post('/api/rf/antenna', (req, res) => {
  const { antenna } = req.body;
  if (antenna >= 1 && antenna <= 4) {
    rfController.setAntenna(antenna);
    res.json({ success: true, antenna: rfController.getAntenna() });
  } else {
    res.status(400).json({ error: 'Invalid antenna selection' });
  }
});

// System telemetry
app.get('/api/telemetry', (req, res) => {
  res.json({
    forwardPower: systemStatus.getForwardPower(),
    reflectedPower: systemStatus.getReflectedPower(),
    swr: systemStatus.getSwr(),
    temperature: systemStatus.getTemperature(),
    voltage: systemStatus.getVoltage(),
    current: systemStatus.getCurrent()
  });
});

// Emergency stop
app.post('/api/emergency-stop', (req, res) => {
  rfController.emergencyStop();
  systemStatus.setTxActive(false);
  radioMode = 'standby';
  res.json({ success: true, message: 'Emergency stop activated' });
});

// Start Express server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Mock STM32 REST API server running at http://localhost:${PORT}`);
  console.log(`Browser app available at http://localhost:${PORT}/app/`);
});

// WebSocket Server for I/Q streaming
const wss = new WebSocketServer({ port: WS_PORT, host: '0.0.0.0' });

wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  
  // Create CBOR handler for this connection
  const cborHandler = new CborHandler();
  
  let streamState = {
    active: false,
    samplesPerPacket: 960,  // 10ms of samples at 96kHz
    targetInterval: 10,      // Send every 10ms
    nextSendTime: 0,
    packetCount: 0,
    startTime: Date.now(),
    
    // TX state
    txActive: false,
    txStartTime: 0,
    txSampleCount: 0,
    loopbackEnabled: true,  // Enable loopback by default for testing
    recording: false,
    
    // Protocol state
    useCbor: false,  // Will be set to true after handshake
    protocolVersion: null
  };
  
  // High-precision streaming function
  const streamIqData = () => {
    if (!streamState.active) return;
    
    const now = Date.now();
    
    // Generate and send I/Q data
    const iqData = iqGenerator.generateIqSamples(streamState.samplesPerPacket);
    
    try {
      if (ws.readyState === ws.OPEN) {
        if (streamState.useCbor) {
          // Send as CBOR
          const message = cborHandler.createIqDataMessage(iqData, streamState.packetCount++);
          ws.send(cborHandler.encode(message));
        } else {
          // Send as JSON (legacy)
          ws.send(JSON.stringify({
            type: 'iqData',
            data: iqData,
            packetNumber: streamState.packetCount++,
            serverTime: now
          }));
        }
      }
    } catch (error) {
      console.error('WebSocket send error:', error);
      streamState.active = false;
      return;
    }
    
    // Calculate next send time for consistent rate
    if (streamState.nextSendTime === 0) {
      streamState.nextSendTime = now + streamState.targetInterval;
    } else {
      streamState.nextSendTime += streamState.targetInterval;
    }
    
    // Calculate actual delay to next transmission
    const delay = Math.max(1, streamState.nextSendTime - Date.now());
    
    // Schedule next transmission
    setTimeout(streamIqData, delay);
  };
  
  // Auto-start streaming (like real hardware)
  streamState.active = true;
  streamState.nextSendTime = Date.now();
  console.log('Starting I/Q stream automatically');
  streamIqData();
  
  ws.on('message', async (message) => {
    try {
      // Decode using CBOR handler (handles both CBOR and JSON)
      const msg = cborHandler.decode(message);
      
      // Handle based on type field (CBOR) or legacy type field
      const messageType = msg.t !== undefined ? msg.t : msg.type;
      
      switch (messageType) {
        case cborHandler.messageTypes.HANDSHAKE:
        case 'handshake':
          console.log('Handshake received, capabilities:', msg.cap);
          streamState.useCbor = msg.cap && msg.cap.includes('cbor');
          streamState.protocolVersion = msg.v || 1;
          
          // Send handshake response
          const response = cborHandler.createHandshakeResponse();
          if (streamState.useCbor) {
            ws.send(cborHandler.encode(response));
          } else {
            ws.send(JSON.stringify(response));
          }
          console.log('Protocol mode:', streamState.useCbor ? 'CBOR' : 'JSON');
          break;
          
        case 'stopIqStream':
          streamState.active = false;
          console.log('I/Q stream stopped');
          break;
          
        case 'startIqStream':
          if (!streamState.active) {
            streamState.active = true;
            streamState.nextSendTime = Date.now();
            streamState.packetCount = 0;
            streamState.startTime = Date.now();
            streamIqData();
            console.log('I/Q stream restarted');
          }
          break;
          
        case cborHandler.messageTypes.TX_CONTROL:
        case 'startTxStream':
          streamState.txActive = true;
          streamState.txStartTime = Date.now();
          streamState.txSampleCount = 0;
          
          // Simulate PIN diode switching delay
          setTimeout(() => {
            const txReady = {
              type: 'txReady',
              switchingTime: 5 // ms
            };
            ws.send(streamState.useCbor ? 
              cborHandler.encode(txReady) : 
              JSON.stringify(txReady));
          }, 5);
          
          console.log('TX stream started');
          break;
          
        case 'stopTxStream':
          streamState.txActive = false;
          
          // Simulate PA shutdown sequence
          setTimeout(() => {
            const txStopped = {
              type: 'txStopped',
              totalSamples: streamState.txSampleCount,
              duration: Date.now() - streamState.txStartTime
            };
            ws.send(streamState.useCbor ? 
              cborHandler.encode(txStopped) : 
              JSON.stringify(txStopped));
          }, 10);
          
          console.log('TX stream stopped');
          break;
          
        case cborHandler.messageTypes.TX_MODULATION:
        case 'txModulation':
          // Extract fields from CBOR or JSON format
          const amplitude = msg.a || msg.amplitude || msg.data?.amplitude;
          const phase = msg.p || msg.phase || msg.data?.phase;
          const frequency = msg.f || msg.frequency || msg.data?.frequency;
          const mode = msg.m || msg.mode || msg.data?.mode;
          const sampleRate = msg.sr || msg.sampleRate || msg.data?.sampleRate || 48000;
          
          console.log(`TX modulation received: mode ${mode} at ${frequency} Hz, ${amplitude.length} samples`);
          
          streamState.txSampleCount += amplitude.length;
          
          // Store for recording/playback if enabled
          if (streamState.recording) {
            recordTxModulation({
              timestamp: Date.now(),
              frequency,
              mode,
              amplitude,
              phase,
              sampleRate
            });
          }
          
          // Loopback test - inject TX into RX stream
          if (streamState.loopbackEnabled && radioMode === 'tx') {
            // Calculate frequency offset from current RX frequency
            const rxFreq = rfController.getFrequency();
            const frequencyOffset = 0; // TX at same frequency as RX for testing
            
            // Inject into I/Q generator for immediate playback
            iqGenerator.injectTxSignal({
              amplitude: amplitude,
              phase: phase,
              sampleRate: sampleRate
            }, frequencyOffset);
            
            console.log('TX signal injected into RX stream for loopback');
          }
          
          // Send ACK with simulated hardware status
          const forwardPower = calculatePowerFromAmplitude(amplitude);
          const ack = {
            type: 'txModulationAck',
            vswr: 1.2 + Math.random() * 0.3,
            forwardPower: forwardPower,
            temperature: 35 + Math.random() * 5
          };
          
          ws.send(streamState.useCbor ? 
            cborHandler.encode(ack) : 
            JSON.stringify(ack));
          break;
          
        case 'enableLoopback':
          streamState.loopbackEnabled = true;
          console.log('TX loopback enabled - TX will be heard in RX');
          ws.send(JSON.stringify({
            type: 'loopbackStatus',
            enabled: true
          }));
          break;
          
        case 'disableLoopback':
          streamState.loopbackEnabled = false;
          console.log('TX loopback disabled');
          ws.send(JSON.stringify({
            type: 'loopbackStatus',
            enabled: false
          }));
          break;
          
        case 'startRecording':
          streamState.recording = true;
          console.log('TX recording started');
          break;
          
        case 'stopRecording':
          streamState.recording = false;
          console.log('TX recording stopped');
          break;
          
        case 'playbackRecording':
          const recordingId = msg.recordingId || msg.data?.recordingId;
          playbackTxRecording(recordingId);
          break;
          
        case 'setTxTestMode':
          const testMode = msg.testMode || msg.data?.testMode;
          const parameters = msg.parameters || msg.data?.parameters;
          
          if (testMode === 'twoTone') {
            streamState.twoToneTest = {
              enabled: true,
              freq1: parameters?.freq1 || 700,
              freq2: parameters?.freq2 || 1900,
              amplitude: parameters?.amplitude || 0.5
            };
          } else if (testMode === 'sweep') {
            streamState.sweepTest = {
              enabled: true,
              startFreq: parameters?.startFreq || 100,
              stopFreq: parameters?.stopFreq || 3000,
              duration: parameters?.duration || 5
            };
          }
          break;
          
        case 'ping':
          // Latency measurement
          const pong = {
            type: 'pong',
            timestamp: msg.timestamp,
            serverTime: Date.now()
          };
          ws.send(streamState.useCbor ? 
            cborHandler.encode(pong) : 
            JSON.stringify(pong));
          break;
          
        default:
          console.log('Unknown message type:', messageType);
          // Send warning back to client
          if (streamState.useCbor) {
            const warning = cborHandler.createWarningMessage(
              `Unknown message type: ${messageType}`
            );
            ws.send(cborHandler.encode(warning));
          }
          break;
      }
    } catch (e) {
      console.error('WebSocket message error:', e);
      // Send error back
      if (streamState.useCbor) {
        const error = cborHandler.createErrorMessage(400, e.message);
        ws.send(cborHandler.encode(error));
      }
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket client disconnected');
    streamState.active = false;
    streamState.txActive = false;
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    streamState.active = false;
    streamState.txActive = false;
  });
  
  // Send initial connection status (legacy JSON for compatibility)
  ws.send(JSON.stringify({
    type: 'connected',
    version: '1.0.0-mock',
    capabilities: {
      iqStreaming: true,
      txStreaming: true,
      loopback: true,
      cbor: true,
      maxSampleRate: 96000,
      bitsPerSample: 24,
      bands: Object.keys(rfController.bandLimits)
    }
  }));
});

// Helper functions

/**
 * Calculate forward power from amplitude samples
 */
function calculatePowerFromAmplitude(amplitude) {
  if (!amplitude || amplitude.length === 0) return 0;
  
  let sumSquared = 0;
  const numSamples = amplitude.length;
  
  for (let i = 0; i < numSamples; i++) {
    const normalized = amplitude[i] / 4095.0; // From 12-bit range
    sumSquared += normalized * normalized;
  }
  
  // RMS power in watts (assuming 50 ohm load)
  const rms = Math.sqrt(sumSquared / numSamples);
  const powerWatts = (rms * rms * 50) * rfController.getPower(); // Scale by power setting
  
  return Math.min(powerWatts, rfController.getPower()); // Cap at set power
}

/**
 * Record TX modulation for later playback
 */
function recordTxModulation(data) {
  const recording = {
    ...data,
    id: Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  };
  
  txRecordings.push(recording);
  
  // Keep only last 10 recordings
  if (txRecordings.length > 10) {
    txRecordings.shift();
  }
  
  console.log(`Recorded TX modulation: ${data.mode} at ${data.frequency} Hz`);
  return recording.id;
}

/**
 * Playback recorded TX modulation through RX
 */
function playbackTxRecording(recordingId) {
  const recording = txRecordings.find(r => r.id === recordingId);
  
  if (recording) {
    console.log(`Playing back TX recording: ${recordingId}`);
    
    // Inject into I/Q generator
    iqGenerator.injectTxSignal({
      amplitude: recording.amplitude,
      phase: recording.phase,
      sampleRate: recording.sampleRate
    }, 0); // Play at center frequency
    
    return true;
  }
  
  console.log(`Recording not found: ${recordingId}`);
  return false;
}

console.log(`WebSocket server running on ws://localhost:${WS_PORT}`);
console.log('TX loopback enabled by default - transmitted signals will appear in RX waterfall');
console.log('Protocol: CBOR support enabled, JSON fallback available');

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down mock server...');
  wss.clients.forEach((client) => {
    client.close();
  });
  process.exit(0);
});
