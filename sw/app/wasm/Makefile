# WASM DSP Module Makefile
# Requires Emscripten SDK (emcc)

CC = emcc
CFLAGS = -O3 -ffast-math -DNDEBUG
WASM_FLAGS = -s WASM=1 -s EXPORTED_RUNTIME_METHODS='["cwrap"]' -s ALLOW_MEMORY_GROWTH=1 -s MODULARIZE=1 -s EXPORT_NAME="SdrDspModule"

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