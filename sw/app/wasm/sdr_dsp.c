/**
 * High-Performance SDR DSP Module for WebAssembly
 * Browser-side demodulation and filtering for baseband I/Q data
 * Hardware/FPGA handles frequency mixing and NCO
 */

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// Export functions for WASM
#define WASM_EXPORT __attribute__((visibility("default")))

// Constants
#define PI 3.14159265358979323846
#define TWO_PI (2.0 * PI)

// DSP state structures for filtering
typedef struct {
    float *taps;
    float *delay_line;
    int num_taps;
    int index;
} FIRFilter;
static float hilbert_taps[16];
static float hilbert_delay[16];
static int hilbert_index = 0;
static int hilbert_initialized = 0;

// Initialize Hilbert transform filter
WASM_EXPORT
void init_hilbert_filter() {
    if (hilbert_initialized) return;

    int center = 8; // 16/2

    // Generate Hilbert filter coefficients
    for (int i = 0; i < 16; i++) {
        int n = i - center;
        if (n != 0 && n % 2 != 0) {
            hilbert_taps[i] = 2.0f / (PI * n);
        } else {
            hilbert_taps[i] = 0.0f;
        }

        // Apply Hamming window
        float window = 0.54f - 0.46f * cosf(TWO_PI * i / 15.0f);
        hilbert_taps[i] *= window;

        hilbert_delay[i] = 0.0f;
    }

    hilbert_index = 0;
    hilbert_initialized = 1;
}

// Note: Frequency mixing/NCO is handled by hardware/FPGA
// Browser receives pre-tuned baseband I/Q data

// High-performance Hilbert transform for SSB demodulation
WASM_EXPORT
float hilbert_transform_sample(float sample) {
    if (!hilbert_initialized) init_hilbert_filter();

    // Add sample to circular delay line
    hilbert_delay[hilbert_index] = sample;

    // Compute convolution
    float output = 0.0f;
    for (int i = 0; i < 16; i++) {
        int delay_idx = (hilbert_index - i + 16) % 16;
        output += hilbert_taps[i] * hilbert_delay[delay_idx];
    }

    hilbert_index = (hilbert_index + 1) % 16;
    return output;
}

// Process block of samples for Hilbert transform
WASM_EXPORT
void hilbert_transform_block(float *input, float *output, int num_samples) {
    for (int i = 0; i < num_samples; i++) {
        output[i] = hilbert_transform_sample(input[i]);
    }
}

// USB demodulation: I + Hilbert(Q)
WASM_EXPORT
void usb_demodulate_block(float *i_samples, float *q_samples, float *audio_out, int num_samples) {
    for (int i = 0; i < num_samples; i++) {
        float q_hilbert = hilbert_transform_sample(q_samples[i]);
        audio_out[i] = i_samples[i] + q_hilbert;
    }
}

// LSB demodulation: I - Hilbert(Q)
WASM_EXPORT
void lsb_demodulate_block(float *i_samples, float *q_samples, float *audio_out, int num_samples) {
    for (int i = 0; i < num_samples; i++) {
        float q_hilbert = hilbert_transform_sample(q_samples[i]);
        audio_out[i] = i_samples[i] - q_hilbert;
    }
}

// AM demodulation: magnitude
WASM_EXPORT
void am_demodulate_block(float *i_samples, float *q_samples, float *audio_out, int num_samples) {
    for (int i = 0; i < num_samples; i++) {
        audio_out[i] = sqrtf(i_samples[i] * i_samples[i] + q_samples[i] * q_samples[i]);
    }
}

// Decimate by 2 with simple averaging
WASM_EXPORT
int decimate_by_2(float *input, float *output, int input_length) {
    int output_length = input_length / 2;
    for (int i = 0; i < output_length; i++) {
        // Simple averaging decimation
        output[i] = (input[i * 2] + input[i * 2 + 1]) * 0.5f;
    }
    return output_length;
}

// High-performance combined processing function
// Performs decimation + demodulation in one pass for baseband I/Q data
WASM_EXPORT
int process_baseband_iq_block(float *i_in, float *q_in, int input_samples,
                              float *audio_out, int demod_mode) {
    // Step 1: Decimation by 2 with demodulation
    int output_samples = input_samples / 2;

    for (int i = 0; i < output_samples; i++) {
        int src_idx = i * 2;
        float i_sample = (i_in[src_idx] + i_in[src_idx + 1]) * 0.5f;
        float q_sample = (q_in[src_idx] + q_in[src_idx + 1]) * 0.5f;

        // Step 2: Demodulation based on mode
        switch (demod_mode) {
            case 0: // USB
                {
                    float q_hilbert = hilbert_transform_sample(q_sample);
                    audio_out[i] = i_sample + q_hilbert;
                }
                break;
            case 1: // LSB
                {
                    float q_hilbert = hilbert_transform_sample(q_sample);
                    audio_out[i] = i_sample - q_hilbert;
                }
                break;
            case 2: // AM
                audio_out[i] = sqrtf(i_sample * i_sample + q_sample * q_sample);
                break;
            case 3: // CW (same as AM for now)
                audio_out[i] = sqrtf(i_sample * i_sample + q_sample * q_sample);
                break;
            default:
                audio_out[i] = i_sample; // Direct I channel
                break;
        }
    }

    return output_samples;
}

// Memory allocation functions for WASM
WASM_EXPORT
void* allocate_memory(int size) {
    return malloc(size);
}

WASM_EXPORT
void free_memory(void* ptr) {
    free(ptr);
}