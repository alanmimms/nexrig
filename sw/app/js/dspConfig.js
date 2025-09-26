/**
 * Shared DSP Configuration
 * Single source of truth for filter parameters and DSP settings
 */

// Filter parameters for each demodulation mode
// All frequencies in Hz, relative to baseband (after frequency shift)
const DspConfig = {
  filterParams: {
    usb: { 
      low: 200,    // Lower edge of passband
      high: 3500,  // Upper edge of passband
      description: 'Upper Sideband: 200-3500 Hz above carrier'
    },
    lsb: { 
      low: -3500,  // Lower edge (negative for LSB)
      high: -200,  // Upper edge (negative for LSB)
      description: 'Lower Sideband: 200-3500 Hz below carrier'
    },
    cw: { 
      low: 200,    // Narrow filter for CW (will be mirrored for LSB-style CW)
      high: 700,   // 500 Hz bandwidth
      description: 'CW: 500 Hz narrow filter'
    },
    am: { 
      low: -4000,  // Symmetric around carrier
      high: 4000,
      description: 'AM: ±4000 Hz'
    }
  },

  // Sample rates
  sampleRates: {
    iq: 96000,      // I/Q input sample rate
    audio: 48000,   // Audio output sample rate
    decimation: 2   // Decimation ratio
  },

  // Waterfall display parameters
  waterfall: {
    spanHz: 96000,  // Total frequency span (±48 kHz)
    minFreq: -48000,
    maxFreq: 48000
  },

  // AGC parameters
  agc: {
    initialGain: 3.0,
    target: 0.3,
    attackRate: 0.0001,
    decayRate: 0.00005,
    minGain: 1.0,
    maxGain: 3.0
  },

  // Filter design parameters
  filter: {
    order: 64,      // Filter taps
    window: 'blackman'  // Window function type
  },

  // Get bandwidth for a given mode
  getBandwidth(mode) {
    const params = this.filterParams[mode];
    if (!params) return 0;
    return Math.abs(params.high - params.low);
  },

  // Get filter description for UI
  getDescription(mode) {
    const params = this.filterParams[mode];
    if (!params) return '';
    
    switch (mode) {
    case 'usb':
      return `Upper Sideband: ${params.low}-${params.high} Hz above carrier`;
    case 'lsb':
      return `Lower Sideband: ${Math.abs(params.high)}-${Math.abs(params.low)} Hz below carrier`;
    case 'cw':
      return `CW: ${this.getBandwidth(mode)} Hz narrow filter`;
    case 'am':
      return `AM: ±${params.high} Hz`;
    default:
      return params.description || '';
    }
  },

  // Get CW filter params based on SSB mode preference
  getCwFilterParams(ssbMode = 'usb') {
    const cwParams = this.filterParams.cw;
    if (ssbMode === 'lsb') {
      // Mirror the filter for LSB-style CW
      return {
        low: -cwParams.high,
        high: -cwParams.low
      };
    }
    return cwParams;
  }
};

DspConfig.getSerializable = function() {
  return {
    filterParams: this.filterParams,
    sampleRates: this.sampleRates,
    agc: this.agc,
    filter: this.filter,
    waterfall: this.waterfall
  };
};


// Export for use in both browser and AudioWorklet contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DspConfig;
} else if (typeof self !== 'undefined') {
  // AudioWorklet global scope
  self.DspConfig = DspConfig;
} else if (typeof window !== 'undefined') {
  // Browser global scope
  window.DspConfig = DspConfig;
}
