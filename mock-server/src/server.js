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
    if (['rx', 'tx', 'standby'].includes(mode)) {
        rfController.setMode(mode);
        res.json({ success: true, mode: rfController.getMode() });
    } else {
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
    
    let iqStreamInterval = null;
    let txStreamInterval = null;
    
    ws.on('message', (message) => {
        try {
            const msg = JSON.parse(message);
            
            switch (msg.type) {
                case 'startIqStream':
                    // Start sending I/Q data at 96 kS/s (simulated at lower rate)
                    if (!iqStreamInterval) {
                        iqStreamInterval = setInterval(() => {
                            const iqData = iqGenerator.generateIqSamples(1024);
                            ws.send(JSON.stringify({
                                type: 'iqData',
                                data: iqData
                            }));
                        }, 10); // Send 1024 samples every 10ms (~100kS/s)
                    }
                    break;
                    
                case 'stopIqStream':
                    if (iqStreamInterval) {
                        clearInterval(iqStreamInterval);
                        iqStreamInterval = null;
                    }
                    break;
                    
                case 'startTxStream':
                    // Accept transmit amplitude/phase data
                    ws.send(JSON.stringify({
                        type: 'txStreamReady',
                        sampleRate: 48000
                    }));
                    break;
                    
                case 'txData':
                    // Process transmit data (amplitude and phase)
                    // In real hardware, this would go to the FPGA and PA
                    console.log(`TX data received: ${msg.data.length} samples`);
                    break;
                    
                case 'stopTxStream':
                    ws.send(JSON.stringify({
                        type: 'txStreamStopped'
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
        if (iqStreamInterval) clearInterval(iqStreamInterval);
        if (txStreamInterval) clearInterval(txStreamInterval);
    });
    
    // Send initial status
    ws.send(JSON.stringify({
        type: 'connected',
        version: '1.0.0-mock',
        capabilities: {
            iqStreaming: true,
            txStreaming: true,
            maxSampleRate: 96000,
            bands: ['160m', '80m', '40m', '20m', '17m', '15m', '12m', '10m', '6m', '2m']
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