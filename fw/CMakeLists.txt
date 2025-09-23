# NexRig STM32 Firmware - Zephyr RTOS Build Configuration
# Target: STM32H753 at 480MHz with 1MB Flash/1MB RAM

cmake_minimum_required(VERSION 3.20.0)

# Zephyr boilerplate
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(nexrig_firmware VERSION 1.0.0 LANGUAGES CXX C)

# Project configuration
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler flags for high-performance real-time operation
target_compile_options(app PRIVATE
  # C++20 features and optimization
  -std=c++20
  -O3
  -ffast-math
  -funroll-loops
  
  # Real-time performance
  -fno-exceptions
  -fno-rtti
  -ffunction-sections
  -fdata-sections
  
  # ARM Cortex-M7 specific optimizations
  -mcpu=cortex-m7
  -mfpu=fpv5-d16
  -mfloat-abi=hard
  -mthumb
  
  # Warnings
  -Wall
  -Wextra
  -Werror
  -Wno-unused-parameter
)

# Linker flags
target_link_options(app PRIVATE
  -Wl,--gc-sections
  -Wl,--print-memory-usage
)

# Include directories
target_include_directories(app PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/hw
  ${CMAKE_CURRENT_SOURCE_DIR}/src/rt
  ${CMAKE_CURRENT_SOURCE_DIR}/src/coms
  ${CMAKE_CURRENT_SOURCE_DIR}/src/app
  ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Source files organized by namespace
target_sources(app PRIVATE
  # Main application entry
  src/main.cpp
  
  # Hardware abstraction layer (HW namespace)
  src/hw/RFController.cpp
  src/hw/PowerAmplifier.cpp
  src/hw/AdcDacInterface.cpp
  src/hw/PinDiodeMatrix.cpp
  src/hw/FPGAInterface.cpp
  
  # Real-time control layer (RT namespace)
  src/rt/RFStateMachine.cpp
  src/rt/DSPProcessor.cpp
  src/rt/PredistortionEngine.cpp
  src/rt/ProtectionSystem.cpp
  
  # Communications layer (Coms namespace)
  src/coms/UsbEthernetGadget.cpp
  src/coms/HTTPServer.cpp
  src/coms/RESTAPIHandler.cpp
  src/coms/WebSocketStreamer.cpp
  
  # Application coordination layer (App namespace)
  src/app/TransceiverController.cpp
  src/app/HardwareManager.cpp
  src/app/DiagnosticsEngine.cpp
  
  # Utility and support code
  src/utils/Memory.cpp
  src/utils/Threading.cpp
  src/utils/Diagnostics.cpp
)

# External libraries
find_package(PkgConfig REQUIRED)

# JSON library for REST API
target_sources(app PRIVATE
  lib/nlohmann_json/single_include/nlohmann/json.hpp
)

# WebSocket++ library for streaming
target_include_directories(app PRIVATE
  lib/websocketpp
)

# Lock-free data structures
target_include_directories(app PRIVATE
  lib/lockfree/include
)

# Zephyr device tree configuration
set(DTC_OVERLAY_FILE ${CMAKE_CURRENT_SOURCE_DIR}/boards/nexrig_stm32h753.overlay)

# Board-specific configuration
if(BOARD STREQUAL "nexrig_stm32h753")
  target_sources(app PRIVATE
    src/board/nexrig_board_init.cpp
    src/board/nexrig_pinmux.cpp
  )
endif()

# Debug configuration
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  target_compile_definitions(app PRIVATE
    NEXRIG_DEBUG=1
    NEXRIG_VERBOSE_LOGGING=1
  )
  
  target_compile_options(app PRIVATE
    -Og
    -g3
    -DDEBUG
  )
else()
  target_compile_definitions(app PRIVATE
    NEXRIG_DEBUG=0
    NDEBUG
  )
endif()

# Version information
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/include/version.h.in
  ${CMAKE_CURRENT_BINARY_DIR}/include/version.h
  @ONLY
)
target_include_directories(app PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include)

# Custom targets for development
add_custom_target(flash
  COMMAND west flash
  DEPENDS app
  COMMENT "Flashing firmware to NexRig hardware"
)

add_custom_target(monitor
  COMMAND west espresso monitor
  COMMENT "Starting serial monitor"
)

add_custom_target(clean-build
  COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}
  COMMENT "Clean build directory"
)

# Documentation generation (if Doxygen available)
find_package(Doxygen)
if(DOXYGEN_FOUND)
  configure_file(${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in 
                 ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile @ONLY)
  
  add_custom_target(docs
    ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Generating API documentation with Doxygen"
    VERBATIM
  )
endif()

# Testing configuration
enable_testing()

# Unit tests (if in development environment)
if(DEFINED ENV{NEXRIG_ENABLE_TESTS})
  add_subdirectory(tests)
endif()

# Static analysis integration
find_program(CLANG_TIDY clang-tidy)
if(CLANG_TIDY)
  set_target_properties(app PROPERTIES
    CXX_CLANG_TIDY "${CLANG_TIDY};-checks=*,-fuchsia-default-arguments"
  )
endif()

# Memory usage reporting
add_custom_command(TARGET app POST_BUILD
  COMMAND ${CMAKE_SIZE} $<TARGET_FILE:app>
  COMMENT "Memory usage:"
)

# Generate compile_commands.json for IDE integration
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)