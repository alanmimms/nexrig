/**
 * Mock STM32 Server for NexRig Development
 * 
 * Simulates the STM32H753's REST API and WebSocket streaming
 * for development without hardware.
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

import { RfController } from './rfController.js';
import { IqStreamGenerator } from './iqStreamGenerator.js';
import { SystemStatus } from './systemStatus.js';

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
  
  let streamState = {
    active: false,
    samplesPerPacket: 960,  // 10ms of samples at 96kHz (larger chunks for less jitter)
    targetInterval: 10,      // Send every 10ms
    nextSendTime: 0,
    packetCount: 0,
    startTime: Date.now()
  };
  
  // High-precision streaming function
  const streamIqData = () => {
    if (!streamState.active) return;
    
    const now = Date.now();
    
    // Generate and send I/Q data
    const iqData = iqGenerator.generateIqSamples(streamState.samplesPerPacket);
    
    try {
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify({
          type: 'iqData',
          data: iqData,
          packetNumber: streamState.packetCount++,
          serverTime: now
        }));
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
    
    // Debug timing occasionally
    if (streamState.packetCount % 100 === 0) {
      const elapsed = (now - streamState.startTime) / 1000;
      const effectiveSampleRate = (streamState.packetCount * streamState.samplesPerPacket) / elapsed;
      console.log(`Stream: ${effectiveSampleRate.toFixed(0)} S/s effective, packet #${streamState.packetCount}`);
    }
  };
  
  // Auto-start streaming (like real hardware)
  streamState.active = true;
  streamState.nextSendTime = Date.now();
  console.log('Starting I/Q stream automatically');
  streamIqData();
  
  ws.on('message', (message) => {
    try {
      const msg = JSON.parse(message);
      
      switch (msg.type) {
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
          
        case 'ping':
          // Latency measurement
          ws.send(JSON.stringify({
            type: 'pong',
            timestamp: msg.timestamp,
            serverTime: Date.now()
          }));
          break;
          
        default:
          console.log('Unknown message type:', msg.type);
      }
    } catch (e) {
      console.error('WebSocket message error:', e);
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket client disconnected');
    streamState.active = false;
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    streamState.active = false;
  });
  
  // Send initial status
  ws.send(JSON.stringify({
    type: 'connected',
    version: '1.0.0-mock',
    capabilities: {
      iqStreaming: true,
      txStreaming: true,
      maxSampleRate: 96000,
      bitsPerSample: 24,
      bands: Object.keys(rfController.bandLimits)
    }
  }));
});

console.log(`WebSocket server running on ws://localhost:${WS_PORT}`);

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down mock server...');
  wss.clients.forEach((client) => {
    client.close();
  });
  process.exit(0);
});
