/**
 * High-Performance SDR DSP Module for WebAssembly with SIMD
 * Browser-side demodulation and filtering for baseband I/Q data
 * Hardware/FPGA handles frequency mixing and NCO
 */

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <wasm_simd128.h>

// Export functions for WASM
#define WASM_EXPORT __attribute__((visibility("default")))

// Constants
#define PI 3.14159265358979323846
#define TWO_PI (2.0 * PI)

// DSP state structures for filtering
typedef struct {
  float* taps;
  float* delayLine;
  int numTaps;
  int index;
} FIRFilter;

static float hilbertTaps[16] __attribute__((aligned(16)));
static float hilbertDelay[16] __attribute__((aligned(16)));
static int hilbertIndex = 0;
static int hilbertInitialized = 0;

// Initialize Hilbert transform filter
WASM_EXPORT
void init_hilbert_filter() {
  if (hilbertInitialized) return;

  int center = 8; // 16/2

  // Generate Hilbert filter coefficients
  for (int i = 0; i < 16; i++) {
    int n = i - center;
    if (n != 0 && n % 2 != 0) {
      hilbertTaps[i] = 2.0f / (PI * n);
    } else {
      hilbertTaps[i] = 0.0f;
    }

    // Apply Hamming window
    float window = 0.54f - 0.46f * cosf(TWO_PI * i / 15.0f);
    hilbertTaps[i] *= window;

    hilbertDelay[i] = 0.0f;
  }

  hilbertIndex = 0;
  hilbertInitialized = 1;
}

// SIMD-optimized Hilbert transform for single sample
WASM_EXPORT
float hilbert_transform_sample(float sample) {
  if (!hilbertInitialized) init_hilbert_filter();

  // Add sample to circular delay line
  hilbertDelay[hilbertIndex] = sample;

  // Compute convolution using SIMD (process 4 samples at a time)
  v128_t sum = wasm_f32x4_splat(0.0f);
  
  for (int i = 0; i < 16; i += 4) {
    int idx0 = (hilbertIndex - i + 16) % 16;
    int idx1 = (hilbertIndex - i - 1 + 16) % 16;
    int idx2 = (hilbertIndex - i - 2 + 16) % 16;
    int idx3 = (hilbertIndex - i - 3 + 16) % 16;
    
    // Load 4 delay samples
    v128_t delayVec = wasm_f32x4_make(
				      hilbertDelay[idx0],
				      hilbertDelay[idx1],
				      hilbertDelay[idx2],
				      hilbertDelay[idx3]
				      );
    
    // Load 4 taps
    v128_t tapsVec = wasm_v128_load(&hilbertTaps[i]);
    
    // Multiply and accumulate
    sum = wasm_f32x4_add(sum, wasm_f32x4_mul(tapsVec, delayVec));
  }
  
  // Extract and sum all lanes
  float output = wasm_f32x4_extract_lane(sum, 0) +
    wasm_f32x4_extract_lane(sum, 1) +
    wasm_f32x4_extract_lane(sum, 2) +
    wasm_f32x4_extract_lane(sum, 3);

  hilbertIndex = (hilbertIndex + 1) % 16;
  return output;
}

// SIMD-optimized block Hilbert transform
WASM_EXPORT
void hilbert_transform_block(float* input, float* output, int numSamples) {
  // Process 4 samples at a time when possible
  int simdCount = numSamples & ~3; // Round down to multiple of 4
  int i;
  
  for (i = 0; i < simdCount; i += 4) {
    // Process 4 samples using SIMD
    output[i] = hilbert_transform_sample(input[i]);
    output[i+1] = hilbert_transform_sample(input[i+1]);
    output[i+2] = hilbert_transform_sample(input[i+2]);
    output[i+3] = hilbert_transform_sample(input[i+3]);
  }
  
  // Process remaining samples
  for (; i < numSamples; i++) {
    output[i] = hilbert_transform_sample(input[i]);
  }
}

// SIMD-optimized USB demodulation: I + Hilbert(Q)
WASM_EXPORT
void usb_demodulate_block(float* iSamples, float* qSamples, float* audioOut, int numSamples) {
  // Ensure alignment for SIMD
  int simdCount = numSamples & ~3;
  int i;
  
  // Process 4 samples at a time
  for (i = 0; i < simdCount; i += 4) {
    // Load I samples
    v128_t iVec = wasm_f32x4_make(
				  iSamples[i], iSamples[i+1], iSamples[i+2], iSamples[i+3]
				  );
    
    // Compute Hilbert transform for Q samples
    float qHilbert[4] __attribute__((aligned(16)));
    qHilbert[0] = hilbert_transform_sample(qSamples[i]);
    qHilbert[1] = hilbert_transform_sample(qSamples[i+1]);
    qHilbert[2] = hilbert_transform_sample(qSamples[i+2]);
    qHilbert[3] = hilbert_transform_sample(qSamples[i+3]);
    
    v128_t qHilbertVec = wasm_v128_load(qHilbert);
    
    // USB: I + Hilbert(Q)
    v128_t result = wasm_f32x4_add(iVec, qHilbertVec);
    
    // Store result
    wasm_v128_store(&audioOut[i], result);
  }
  
  // Handle remaining samples
  for (; i < numSamples; i++) {
    float qHilbert = hilbert_transform_sample(qSamples[i]);
    audioOut[i] = iSamples[i] + qHilbert;
  }
}

// SIMD-optimized LSB demodulation: I - Hilbert(Q)
WASM_EXPORT
void lsb_demodulate_block(float* iSamples, float* qSamples, float* audioOut, int numSamples) {
  int simdCount = numSamples & ~3;
  int i;
  
  for (i = 0; i < simdCount; i += 4) {
    // Load I samples
    v128_t iVec = wasm_f32x4_make(
				  iSamples[i], iSamples[i+1], iSamples[i+2], iSamples[i+3]
				  );
    
    // Compute Hilbert transform for Q samples
    float qHilbert[4] __attribute__((aligned(16)));
    qHilbert[0] = hilbert_transform_sample(qSamples[i]);
    qHilbert[1] = hilbert_transform_sample(qSamples[i+1]);
    qHilbert[2] = hilbert_transform_sample(qSamples[i+2]);
    qHilbert[3] = hilbert_transform_sample(qSamples[i+3]);
    
    v128_t qHilbertVec = wasm_v128_load(qHilbert);
    
    // LSB: I - Hilbert(Q)
    v128_t result = wasm_f32x4_sub(iVec, qHilbertVec);
    
    // Store result
    wasm_v128_store(&audioOut[i], result);
  }
  
  // Handle remaining samples
  for (; i < numSamples; i++) {
    float qHilbert = hilbert_transform_sample(qSamples[i]);
    audioOut[i] = iSamples[i] - qHilbert;
  }
}

// SIMD-optimized AM demodulation: magnitude
WASM_EXPORT
void am_demodulate_block(float* iSamples, float* qSamples, float* audioOut, int numSamples) {
  int simdCount = numSamples & ~3;
  int i;
  
  for (i = 0; i < simdCount; i += 4) {
    // Load I and Q samples
    v128_t iVec = wasm_f32x4_make(
				  iSamples[i], iSamples[i+1], iSamples[i+2], iSamples[i+3]
				  );
    v128_t qVec = wasm_f32x4_make(
				  qSamples[i], qSamples[i+1], qSamples[i+2], qSamples[i+3]
				  );
    
    // Compute I^2 + Q^2
    v128_t iSquared = wasm_f32x4_mul(iVec, iVec);
    v128_t qSquared = wasm_f32x4_mul(qVec, qVec);
    v128_t magSquared = wasm_f32x4_add(iSquared, qSquared);
    
    // sqrt() for magnitude - WASM SIMD doesn't have sqrt, so extract and compute
    audioOut[i] = sqrtf(wasm_f32x4_extract_lane(magSquared, 0));
    audioOut[i+1] = sqrtf(wasm_f32x4_extract_lane(magSquared, 1));
    audioOut[i+2] = sqrtf(wasm_f32x4_extract_lane(magSquared, 2));
    audioOut[i+3] = sqrtf(wasm_f32x4_extract_lane(magSquared, 3));
  }
  
  // Handle remaining samples
  for (; i < numSamples; i++) {
    audioOut[i] = sqrtf(iSamples[i] * iSamples[i] + qSamples[i] * qSamples[i]);
  }
}

// SIMD-optimized decimation by 2 with averaging
WASM_EXPORT
int decimate_by_2(float* input, float* output, int inputLength) {
  int outputLength = inputLength / 2;
  int simdCount = outputLength & ~3;
  int i;
  
  for (i = 0; i < simdCount; i += 4) {
    // Load 8 input samples to produce 4 output samples
    v128_t in0 = wasm_f32x4_make(
				 input[i*2], input[i*2+2], input[i*2+4], input[i*2+6]
				 );
    v128_t in1 = wasm_f32x4_make(
				 input[i*2+1], input[i*2+3], input[i*2+5], input[i*2+7]
				 );
    
    // Average pairs
    v128_t sum = wasm_f32x4_add(in0, in1);
    v128_t result = wasm_f32x4_mul(sum, wasm_f32x4_splat(0.5f));
    
    // Store decimated result
    wasm_v128_store(&output[i], result);
  }
  
  // Handle remaining samples
  for (; i < outputLength; i++) {
    output[i] = (input[i * 2] + input[i * 2 + 1]) * 0.5f;
  }
  
  return outputLength;
}

// SIMD-optimized combined processing function
// Performs decimation + demodulation in one pass for baseband I/Q data
WASM_EXPORT
int process_baseband_iq_block(float* iIn, float* qIn, int inputSamples,
                              float* audioOut, int demodMode) {
  // Step 1: Decimation by 2 with SIMD
  int outputSamples = inputSamples / 2;
  float* iDecimated = (float*)malloc(outputSamples * sizeof(float));
  float* qDecimated = (float*)malloc(outputSamples * sizeof(float));
  
  if (!iDecimated || !qDecimated) {
    if (iDecimated) free(iDecimated);
    if (qDecimated) free(qDecimated);
    return 0;
  }
  
  // SIMD decimation
  decimate_by_2(iIn, iDecimated, inputSamples);
  decimate_by_2(qIn, qDecimated, inputSamples);
  
  // Step 2: Demodulation based on mode (all SIMD-optimized)
  switch (demodMode) {
  case 0: // USB
    usb_demodulate_block(iDecimated, qDecimated, audioOut, outputSamples);
    break;
  case 1: // LSB
    lsb_demodulate_block(iDecimated, qDecimated, audioOut, outputSamples);
    break;
  case 2: // AM
  case 3: // CW (same as AM)
    am_demodulate_block(iDecimated, qDecimated, audioOut, outputSamples);
    break;
  default:
    // Direct I channel copy with SIMD
    memcpy(audioOut, iDecimated, outputSamples * sizeof(float));
    break;
  }
  
  free(iDecimated);
  free(qDecimated);
  
  return outputSamples;
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
