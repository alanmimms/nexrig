/**
 * Mock RF Controller
 * Simulates the STM32's RF control functionality
 */

export class RfController {
    constructor() {
        this.frequency = 14200000; // 14.2 MHz (20m band)
        this.band = '20m';
        this.mode = 'rx'; // rx, tx, standby
        this.power = 10; // watts
        this.antenna = 1;
        
        this.bandLimits = {
            '160m': { min: 1800000, max: 2000000, default: 1900000 },
            '80m':  { min: 3500000, max: 4000000, default: 3750000 },
            '40m':  { min: 7000000, max: 7300000, default: 7150000 },
            '30m':  { min: 10100000, max: 10150000, default: 10110000 },
            '20m':  { min: 14000000, max: 14350000, default: 14200000 },
            '17m':  { min: 18068000, max: 18168000, default: 18118000 },
            '15m':  { min: 21000000, max: 21450000, default: 21225000 },
            '12m':  { min: 24890000, max: 24990000, default: 24940000 },
            '10m':  { min: 28000000, max: 29700000, default: 28500000 }
        };
    }
    
    getFrequency() {
        return this.frequency;
    }
    
    setFrequency(freq) {
        // Validate frequency is within amateur bands
        for (const [band, limits] of Object.entries(this.bandLimits)) {
            if (freq >= limits.min && freq <= limits.max) {
                this.frequency = freq;
                this.band = band;
                return true;
            }
        }
        return false;
    }
    
    getBand() {
        return this.band;
    }
    
    setBand(band) {
        if (this.bandLimits[band]) {
            this.band = band;
            this.frequency = this.bandLimits[band].default;
            return true;
        }
        return false;
    }
    
    getMode() {
        return this.mode;
    }
    
    setMode(mode) {
        if (['rx', 'tx', 'standby'].includes(mode)) {
            this.mode = mode;
            console.log(`RF mode changed to: ${mode}`);
            return true;
        }
        return false;
    }
    
    getPower() {
        return this.power;
    }
    
    setPower(power) {
        if (power >= 1 && power <= 100) {
            this.power = power;
            return true;
        }
        return false;
    }
    
    getAntenna() {
        return this.antenna;
    }
    
    setAntenna(antenna) {
        if (antenna >= 1 && antenna <= 4) {
            this.antenna = antenna;
            return true;
        }
        return false;
    }
    
    emergencyStop() {
        this.mode = 'standby';
        this.power = 0;
        console.log('EMERGENCY STOP ACTIVATED');
        return true;
    }
}
