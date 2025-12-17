import {encode, decode} from 'cbor-x';

export class CborHandler {

  constructor() {
    this.messageTypes = {
      HANDSHAKE: 0x01,
      CAPABILITY: 0x02,
      ERROR: 0x03,
      WARNING: 0x04,
      ACK: 0x05,
      IQ_DATA: 0x10,
      IQ_CONTROL: 0x11,
      TX_MODULATION: 0x20,
      TX_CONTROL: 0x21,
      TELEMETRY: 0x40,
      STATUS: 0x41,
      EXTENDED: 0xFF
    };
    
    this.capabilities = [
      'iq_streaming',
      'tx_modulation', 
      'loopback',
      'recording',
      'cbor'
    ];
  }
  
  async decode(data) {

    try {
      
      // Try CBOR-X first
      return decode(data);
    } catch (e) {
      // Fall back to JSON
      try {
        return JSON.parse(data.toString());
      } catch (jsonError) {
        throw new Error('Invalid message format');
      }
    }
  }
  
  encode(message) {
    // Add timestamp
    if (!message.ts) {
      message.ts = Date.now();
    }
    return encode(message);
  }
  
  createHandshakeResponse() {
    return {
      t: this.messageTypes.HANDSHAKE,
      v: 1,
      id: 'nexrig-mock',
      cap: this.capabilities,
      info: {
        device: 'STM32H753 Mock',
        version: '1.0.0-mock',
        timestamp: Date.now()
      }
    };
  }
  
  createIqDataMessage(iqData, packetNumber) {
    return {
      t: this.messageTypes.IQ_DATA,
      i: iqData.i,
      q: iqData.q,
      seq: packetNumber,
      ts: Date.now()
    };
  }
  
  createErrorMessage(code, message) {
    return {
      t: this.messageTypes.ERROR,
      code: code,
      msg: message,
      ts: Date.now()
    };
  }
}
