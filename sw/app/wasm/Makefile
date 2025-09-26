# WASM DSP Module Makefile
# Requires Emscripten SDK (emcc)

CC = emcc
CFLAGS = -O3 -msimd128 -ffast-math -DNDEBUG

EXPORTED_FUNCTIONS = \
	_malloc \
	_free \
	_init_hilbert_filter \
	_hilbert_transform_sample \
	_hilbert_transform_block \
	_usb_demodulate_block \
	_lsb_demodulate_block \
	_am_demodulate_block \
	_decimate_by_2 \
	_process_baseband_iq_block \
	_allocate_memory \
	_free_memory


empty :=
space := $(empty) $(empty)
comma := ,

WASM_FLAGS = \
	-s WASM=1 \
	-s ENVIRONMENT=web,worker \
	-s EXPORTED_FUNCTIONS='["$(subst $(space),"$(comma)",$(strip $(EXPORTED_FUNCTIONS)))"]' \
	-s EXPORTED_RUNTIME_METHODS='["cwrap"]' \
	-s ALLOW_MEMORY_GROWTH=1 \
	-s INITIAL_MEMORY=131072


# Source and output files
SRC = sdr_dsp.c
OUTPUT = sdr_dsp
WASM_FILE = $(OUTPUT).wasm
JS_FILE = $(OUTPUT).js

.PHONY: all clean install-emscripten

all: $(WASM_FILE)

$(WASM_FILE): $(SRC)
	@echo "Compiling WASM DSP module..."
	$(CC) $(CFLAGS) $(WASM_FLAGS) $(SRC) -o $(OUTPUT).js
	@echo "WASM module compiled successfully!"
	@echo "Generated files:"
	@echo "  - $(JS_FILE) (WASM loader)"
	@echo "  - $(WASM_FILE) (compiled WASM binary)"

clean:
	rm -f $(OUTPUT).js $(OUTPUT).wasm

# Development build with debug symbols
debug: CFLAGS = -O0 -g -DDEBUG
debug: $(WASM_FILE)

# Instructions for installing Emscripten
install-emscripten:
	@echo "To install Emscripten SDK:"
	@echo "1. git clone https://github.com/emscripten-core/emsdk.git"
	@echo "2. cd emsdk"
	@echo "3. ./emsdk install latest"
	@echo "4. ./emsdk activate latest"
	@echo "5. source ./emsdk_env.sh"
	@echo ""
	@echo "Then run: make"

help:
	@echo "Available targets:"
	@echo "  all           - Build optimized WASM module"
	@echo "  debug         - Build debug version with symbols"
	@echo "  clean         - Remove generated files"
	@echo "  install-emscripten - Show Emscripten installation instructions"
