# NexRig Mock Server

This Node.js server mocks the STM32H753 firmware REST API and WebSocket streaming for development without hardware.

## Features

- REST API endpoints for RF control (frequency, band, power, antenna)
- WebSocket server for I/Q data streaming (simulated signals)
- Mock telemetry data (SWR, temperature, voltage, current)
- Serves the browser application from `/app/`
- Simulates various RF signals (CW, SSB, noise)

## Quick Start

```bash
# Install dependencies
npm install

# Start the server
npm start

# Or run in development mode with auto-reload
npm run dev
```

## Access Points

- Browser App: http://localhost:3000/app/
- REST API: http://localhost:3000/api/
- WebSocket: ws://localhost:3001/

## API Endpoints

### System
- `GET /api/status` - Get system status
- `GET /api/telemetry` - Get telemetry data

### RF Control
- `GET/POST /api/rf/frequency` - Get/Set frequency (Hz)
- `GET/POST /api/rf/band` - Get/Set band
- `GET/POST /api/rf/mode` - Get/Set mode (rx/tx/standby)
- `GET/POST /api/rf/power` - Get/Set power (1-100W)
- `GET/POST /api/rf/antenna` - Get/Set antenna (1-4)

### Emergency
- `POST /api/emergency-stop` - Activate emergency stop

## WebSocket Protocol

Connect to `ws://localhost:3001/` and send JSON messages:

### Start I/Q Stream
```json
{ "type": "startIqStream" }
```

### Stop I/Q Stream
```json
{ "type": "stopIqStream" }
```

### Transmit Data
```json
{ 
  "type": "txData",
  "data": {
    "amplitude": [...],
    "phase": [...]
  }
}
```

## Development

The mock server generates realistic I/Q data with:
- Multiple simulated signals (CW, SSB)
- Noise floor
- Random signal appearances
- Realistic telemetry variations