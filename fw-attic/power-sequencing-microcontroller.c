#include "stm32f0xx.h"
#include <stdint.h>

// --- Hardware Pin and Channel Mapping ---
// Change these defines to match your schematic

// FPGA Power Rails
#define FPGA_CORE_EN_PORT       GPIOA
#define FPGA_CORE_EN_PIN        0
#define FPGA_CORE_ADC_CHAN      1 // ADC_IN1 on PA1

#define FPGA_SPI_EN_PORT        GPIOA
#define FPGA_SPI_EN_PIN         2
#define FPGA_SPI_ADC_CHAN       3 // ADC_IN3 on PA3

#define FPGA_VPP_EN_PORT        GPIOA
#define FPGA_VPP_EN_PIN         4
#define FPGA_VPP_ADC_CHAN       6 // ADC_IN6 on PA6

// Codec Power Rails
#define CODEC_AVDD_EN_PORT      GPIOB
#define CODEC_AVDD_EN_PIN       0
#define CODEC_AVDD_ADC_CHAN     7 // ADC_IN7 on PA7

#define CODEC_DVDD_EN_PORT      GPIOB
#define CODEC_DVDD_EN_PIN       1
#define CODEC_DVDD_ADC_CHAN     8 // ADC_IN8 on PC0 (Example, map to available pin)

// Status LED
#define LED_PORT                GPIOA
#define LED_PIN                 5

// --- Voltage Thresholds (12-bit ADC, 3.3V VREF) ---
// Formula: ADC_VALUE = (TARGET_VOLTAGE * 0.9 / 3.3V) * 4095
#define V_FPGA_CORE_THRESH      1340 // 1.2V * 0.9 = 1.08V
#define V_FPGA_SPI_THRESH       3685 // 3.3V * 0.9 = 2.97V
#define V_FPGA_VPP_THRESH       2790 // 2.5V * 0.9 = 2.25V
#define V_CODEC_AVDD_THRESH     3685 // 3.3V * 0.9 = 2.97V
#define V_CODEC_DVDD_THRESH     2015 // 1.8V * 0.9 = 1.62V


// --- State Machine Definition ---
typedef enum {
    POWER_STATE_OFF,
    POWER_STATE_ENABLE_FPGA_CORE,
    POWER_STATE_WAIT_FPGA_CORE,
    POWER_STATE_ENABLE_FPGA_SPI_VPP,
    POWER_STATE_WAIT_FPGA_SPI_VPP,
    POWER_STATE_ENABLE_CODEC_AVDD,
    POWER_STATE_WAIT_CODEC_AVDD,
    POWER_STATE_ENABLE_CODEC_DVDD,
    POWER_STATE_WAIT_CODEC_DVDD,
    POWER_STATE_OK,
    POWER_STATE_FAULT
} power_state_t;


// --- Helper Functions ---

// Simple blocking delay. Not precise, but sufficient for this task.
void delay_ms(volatile uint32_t ms) {
    // 8MHz HSI clock, simple loop is roughly 1ms per 1000 iterations
    for (ms = ms * 1000; ms > 0; ms--);
}

void gpio_init(void) {
    // Enable clocks for GPIOA and GPIOB
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOBEN;

    // Configure LDO enable pins as outputs
    FPGA_CORE_EN_PORT->MODER |= (1 << (FPGA_CORE_EN_PIN * 2));
    FPGA_SPI_EN_PORT->MODER  |= (1 << (FPGA_SPI_EN_PIN * 2));
    FPGA_VPP_EN_PORT->MODER  |= (1 << (FPGA_VPP_EN_PIN * 2));
    CODEC_AVDD_EN_PORT->MODER|= (1 << (CODEC_AVDD_EN_PIN * 2));
    CODEC_DVDD_EN_PORT->MODER|= (1 << (CODEC_DVDD_EN_PIN * 2));
    LED_PORT->MODER          |= (1 << (LED_PIN * 2));
    
    // Configure ADC monitor pins as analog inputs
    // This is the default reset state for many, but explicit configuration is best.
    GPIOA->MODER |= (3 << (1 * 2)); // PA1
    GPIOA->MODER |= (3 << (3 * 2)); // PA3
    GPIOA->MODER |= (3 << (6 * 2)); // PA6
    GPIOA->MODER |= (3 << (7 * 2)); // PA7
    // Assuming PC0 is used for ADC_IN8 for Codec DVDD
    RCC->AHBENR |= RCC_AHBENR_GPIOCEN;
    GPIOC->MODER |= (3 << (0 * 2)); // PC0
}

void adc_init(void) {
    // Enable ADC clock
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    // Calibrate the ADC
    ADC1->CR |= ADC_CR_ADCAL;
    while (ADC1->CR & ADC_CR_ADCAL); // Wait for calibration to complete

    // Enable the ADC
    ADC1->CR |= ADC_CR_ADEN;
    while (!(ADC1->ISR & ADC_ISR_ADRDY)); // Wait for ADC to be ready
}

uint16_t adc_read(uint8_t channel) {
    // Select the channel to read
    ADC1->CHSELR = (1 << channel);
    
    // Start the conversion
    ADC1->CR |= ADC_CR_ADSTART;

    // Wait for the conversion to complete
    while (!(ADC1->ISR & ADC_ISR_EOC));

    // Return the 12-bit result
    return (uint16_t)(ADC1->DR);
}


int main(void) {
    // --- Initialization ---
    gpio_init();
    adc_init();

    power_state_t current_state = POWER_STATE_ENABLE_FPGA_CORE;

    // --- Main Loop ---
    while(1) {
        switch(current_state) {
            case POWER_STATE_ENABLE_FPGA_CORE:
                FPGA_CORE_EN_PORT->BSRR = (1 << FPGA_CORE_EN_PIN); // Set pin high
                delay_ms(10); // Allow time for LDO to start ramping
                current_state = POWER_STATE_WAIT_FPGA_CORE;
                break;

            case POWER_STATE_WAIT_FPGA_CORE:
                if (adc_read(FPGA_CORE_ADC_CHAN) > V_FPGA_CORE_THRESH) {
                    current_state = POWER_STATE_ENABLE_FPGA_SPI_VPP;
                }
                // Optional: Add a timeout here to go to FAULT state
                break;

            case POWER_STATE_ENABLE_FPGA_SPI_VPP:
                FPGA_SPI_EN_PORT->BSRR = (1 << FPGA_SPI_EN_PIN);
                FPGA_VPP_EN_PORT->BSRR = (1 << FPGA_VPP_EN_PIN);
                delay_ms(10);
                current_state = POWER_STATE_WAIT_FPGA_SPI_VPP;
                break;
            
            case POWER_STATE_WAIT_FPGA_SPI_VPP:
                // Check that both rails are up before proceeding
                if ((adc_read(FPGA_SPI_ADC_CHAN) > V_FPGA_SPI_THRESH) && 
                    (adc_read(FPGA_VPP_ADC_CHAN) > V_FPGA_VPP_THRESH)) {
                    current_state = POWER_STATE_ENABLE_CODEC_AVDD;
                }
                break;

            case POWER_STATE_ENABLE_CODEC_AVDD:
                CODEC_AVDD_EN_PORT->BSRR = (1 << CODEC_AVDD_EN_PIN);
                delay_ms(10);
                current_state = POWER_STATE_WAIT_CODEC_AVDD;
                break;

            case POWER_STATE_WAIT_CODEC_AVDD:
                if (adc_read(CODEC_AVDD_ADC_CHAN) > V_CODEC_AVDD_THRESH) {
                    current_state = POWER_STATE_ENABLE_CODEC_DVDD;
                }
                break;

            case POWER_STATE_ENABLE_CODEC_DVDD:
                CODEC_DVDD_EN_PORT->BSRR = (1 << CODEC_DVDD_EN_PIN);
                delay_ms(10);
                current_state = POWER_STATE_WAIT_CODEC_DVDD;
                break;

            case POWER_STATE_WAIT_CODEC_DVDD:
                if (adc_read(CODEC_DVDD_ADC_CHAN) > V_CODEC_DVDD_THRESH) {
                    current_state = POWER_STATE_OK;
                }
                break;

            case POWER_STATE_OK:
                // All rails are stable. Turn on solid status LED.
                LED_PORT->BSRR = (1 << LED_PIN);
                // In a real application, you would continue to monitor all rails here.
                // If any rail drops below its threshold, transition to FAULT.
                // For this example, we will just stay here.
                break;

            case POWER_STATE_FAULT:
                // Something went wrong. Turn off all LDOs.
                FPGA_CORE_EN_PORT->BRR = (1 << FPGA_CORE_EN_PIN);
                FPGA_SPI_EN_PORT->BRR  = (1 << FPGA_SPI_EN_PIN);
                FPGA_VPP_EN_PORT->BRR  = (1 << FPGA_VPP_EN_PIN);
                CODEC_AVDD_EN_PORT->BRR= (1 << CODEC_AVDD_EN_PIN);
                CODEC_DVDD_EN_PORT->BRR= (1 << CODEC_DVDD_EN_PIN);

                // Blink LED fast to indicate fault
                while(1) {
                    LED_PORT->BSRR = (1 << LED_PIN);
                    delay_ms(100);
                    LED_PORT->BRR = (1 << LED_PIN);
                    delay_ms(100);
                }
                break;

            default:
                current_state = POWER_STATE_FAULT;
                break;
        }
    }
}
