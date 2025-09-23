/**
 * System Status Simulator
 * Provides mock telemetry and status information
 */

export class SystemStatus {
    constructor() {
        this.startTime = Date.now();
        this.txActive = false;
        this.temperature = 35; // Celsius
        this.voltage = 13.8; // Volts
    }
    
    getStatus() {
        return {
            version: '1.0.0-mock',
            uptime: Math.floor((Date.now() - this.startTime) / 1000),
            rf: {
                enabled: true,
                locked: true,
                synthesizer: 'OK'
            },
            pa: {
                enabled: !this.txActive,
                temperature: this.temperature,
                protection: 'OK'
            },
            fpga: {
                initialized: true,
                version: '0.1.0',
                utilization: 45
            },
            stm32: {
                cpuLoad: 15 + Math.random() * 10,
                memoryUsed: 256000 + Math.floor(Math.random() * 50000),
                memoryTotal: 1048576
            }
        };
    }
    
    getForwardPower() {
        if (!this.txActive) return 0;
        // Simulate forward power with some variation
        return 10 + Math.random() * 2;
    }
    
    getReflectedPower() {
        if (!this.txActive) return 0;
        // Simulate low reflected power (good SWR)
        return 0.5 + Math.random() * 0.2;
    }
    
    getSwr() {
        const forward = this.getForwardPower();
        const reflected = this.getReflectedPower();
        
        if (forward === 0) return 1.0;
        
        const rho = Math.sqrt(reflected / forward);
        return (1 + rho) / (1 - rho);
    }
    
    getTemperature() {
        // Simulate temperature rise during TX
        if (this.txActive) {
            this.temperature += 0.1;
            if (this.temperature > 60) this.temperature = 60;
        } else {
            this.temperature -= 0.05;
            if (this.temperature < 35) this.temperature = 35;
        }
        return this.temperature;
    }
    
    getVoltage() {
        // Simulate voltage sag during TX
        if (this.txActive) {
            return this.voltage - 0.3 - Math.random() * 0.2;
        }
        return this.voltage + (Math.random() - 0.5) * 0.1;
    }
    
    getCurrent() {
        // Simulate current draw
        if (this.txActive) {
            return 8.5 + Math.random() * 1.5; // 8.5-10A during TX
        }
        return 0.8 + Math.random() * 0.2; // 0.8-1A during RX
    }
    
    setTxActive(active) {
        this.txActive = active;
        console.log(`TX ${active ? 'ACTIVE' : 'INACTIVE'}`);
    }
}