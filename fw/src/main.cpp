/**
 * @file main.cpp
 * @brief NexRig STM32H753 Firmware Entry Point
 * 
 * This file contains the main application entry point for the NexRig
 * SDR transceiver firmware. The STM32 provides hardware abstraction
 * and REST APIs with NO UI policy decisions.
 * 
 * Architecture:
 * - HW namespace: Hardware abstraction layer
 * - RT namespace: Real-time control and DSP
 * - Coms namespace: REST API and WebSocket streaming  
 * - App namespace: Application coordination
 * 
 * @copyright 2025 NexRig Project - MIT License
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/logging/log.h>
#include <zephyr/sys/printk.h>

#include "hw/RfController.h"
#include "hw/PowerAmplifier.h"
#include "hw/FpgaInterface.h"
#include "rt/RfStateMachine.h"
#include "rt/DspProcessor.h"
#include "rt/ProtectionSystem.h"
#include "coms/HttpServer.h"
#include "coms/RestApiHandler.h"
#include "coms/WebSocketStreamer.h"
#include "app/TransceiverController.h"
#include "app/HardwareManager.h"
#include "utils/Threading.h"
#include "version.h"

LOG_MODULE_REGISTER(nexrigmain, LOG_LEVEL_INF);

// Global hardware and system objects
namespace {
  // Hardware layer
  NexRig::HW::RfController gRfController;
  NexRig::HW::PowerAmplifier gPowerAmplifier;
  NexRig::HW::FpgaInterface gFpgaInterface;
  
  // Real-time layer
  NexRig::RT::RfStateMachine gRfStateMachine;
  NexRig::RT::DspProcessor gDspProcessor;
  NexRig::RT::ProtectionSystem gProtectionSystem;
  
  // Communications layer
  NexRig::Coms::HttpServer gHttpServer;
  NexRig::Coms::RestApiHandler gRestApiHandler;
  NexRig::Coms::WebSocketStreamer gWebSocketStreamer;
  
  // Application coordination
  NexRig::App::TransceiverController gTransceiverController;
  NexRig::App::HardwareManager gHardwareManager;
  
  // System state
  std::atomic<bool> gSystemRunning{false};
  std::atomic<bool> gEmergencyShutdown{false};
}

/**
 * @brief Critical RF control thread - highest priority
 * 
 * This thread runs at 1kHz and handles all time-critical RF operations:
 * - TX/RX switching sequences
 * - Protection system monitoring
 * - Power amplifier envelope tracking
 * - FPGA coordination
 */
void RfControlThread() {
  LOG_INF("Starting RF control thread");
  
  constexpr auto LoopPeriod = std::chrono::microseconds(1000); // 1kHz
  auto NextWakeup = std::chrono::steady_clock::now();
  
  while (gSystemRunning.load()) {
    NextWakeup += LoopPeriod;
    
    // Critical RF operations - must complete within 1ms
    gRfStateMachine.RunStateMachine();
    gProtectionSystem.CheckLimits();
    gPowerAmplifier.UpdateControl();
    
    // Emergency shutdown check
    if (gEmergencyShutdown.load()) {
      LOG_ERR("Emergency shutdown triggered in RF thread");
      gRfController.SetMode(NexRig::HW::RfController::Mode::Standby);
      gPowerAmplifier.EmergencyShutdown();
      break;
    }
    
    std::this_thread::sleep_until(NextWakeup);
  }
  
  LOG_INF("RF control thread terminated");
}

/**
 * @brief High-frequency DSP processing thread
 * 
 * Handles I/Q sample processing at 96kS/s sample rate:
 * - ADC/DAC sample processing
 * - Real-time filtering
 * - Predistortion
 * - Data streaming to browser
 */
void DSPThread() {
  LOG_INF("Starting DSP processing thread");
  
  while (gSystemRunning.load()) {
    // Process incoming RX samples
    auto RXSamples = gDSPProcessor.GetNewRXSamples();
    if (!RXSamples.empty()) {
      gDSPProcessor.ProcessRXSamples(RXSamples);
      gWebSocketStreamer.StreamIQData(RXSamples);
    }
    
    // Process outgoing TX samples
    auto TXSamples = gDSPProcessor.GetNewTXSamples();
    if (!TXSamples.empty()) {
      gDSPProcessor.ProcessTXSamples(TXSamples);
      
      // Send phase commands to FPGA
      auto PhaseCommands = gDSPProcessor.GeneratePhaseCommands(TXSamples);
      gFPGAInterface.UpdatePhaseStream(PhaseCommands);
    }
    
    // Yield to other high-priority tasks
    k_yield();
  }
  
  LOG_INF("DSP processing thread terminated");
}

/**
 * @brief Communication server thread
 * 
 * Handles HTTP REST API and WebSocket connections:
 * - REST API endpoints for hardware control
 * - WebSocket streaming for real-time data
 * - Browser application serving
 */
void CommunicationThread() {
  LOG_INF("Starting communication thread");
  
  // Initialize HTTP server with REST API handlers
  gHTTPServer.Initialize();
  gRESTAPIHandler.RegisterRoutes(&gHTTPServer);
  
  // Start WebSocket streaming server
  gWebSocketStreamer.Initialize();
  
  // Serve browser application files
  gHTTPServer.ServeStaticFiles("/app", "Browser application files");
  
  // Start listening on USB ethernet interface
  gHTTPServer.StartListening("192.168.7.1", 8080);
  
  LOG_INF("HTTP server started on 192.168.7.1:8080");
  LOG_INF("WebSocket streaming available on /stream");
  LOG_INF("REST API available at /api/v1/");
  LOG_INF("Browser app available at /app/");
  
  // Communication event loop
  while (gSystemRunning.load()) {
    gHTTPServer.ProcessRequests();
    gWebSocketStreamer.ProcessConnections();
    
    k_msleep(10); // 100Hz update rate for communications
  }
  
  LOG_INF("Communication thread terminated");
}

/**
 * @brief System monitoring and diagnostics thread
 * 
 * Lower priority thread for:
 * - Temperature monitoring
 * - Performance metrics
 * - Hardware diagnostics
 * - Logging and telemetry
 */
void DiagnosticsThread() {
  LOG_INF("Starting diagnostics thread");
  
  while (gSystemRunning.load()) {
    // Update system diagnostics
    gHardwareManager.UpdateDiagnostics();
    
    // Check for thermal issues
    auto Temperatures = gHardwareManager.GetTemperatures();
    for (const auto& [Sensor, TempC] : Temperatures) {
      if (TempC > 85.0f) { // Example thermal limit
        LOG_WRN("High temperature on %s: %.1f°C", Sensor.c_str(), TempC);
      }
    }
    
    // Performance monitoring
    auto CPUUsage = gHardwareManager.GetCPUUsage();
    auto MemoryUsage = gHardwareManager.GetMemoryUsage();
    
    // Log periodic status (every 10 seconds)
    static uint32_t StatusCounter = 0;
    if (++StatusCounter >= 100) { // 10Hz * 10 seconds
      LOG_INF("System status: CPU=%.1f%% Memory=%.1f%% Temp=%.1f°C", 
              CPUUsage, MemoryUsage.UsagePercent, Temperatures["PA"]);
      StatusCounter = 0;
    }
    
    k_msleep(100); // 10Hz update rate for diagnostics
  }
  
  LOG_INF("Diagnostics thread terminated");
}

/**
 * @brief Initialize all hardware subsystems
 * 
 * @return true if initialization successful, false on error
 */
bool InitializeHardware() {
  LOG_INF("Initializing NexRig hardware subsystems");
  
  // Initialize hardware abstraction layer
  if (!gRFController.Initialize()) {
    LOG_ERR("Failed to initialize RF controller");
    return false;
  }
  
  if (!gPowerAmplifier.Initialize()) {
    LOG_ERR("Failed to initialize power amplifier");
    return false;
  }
  
  if (!gFPGAInterface.Initialize()) {
    LOG_ERR("Failed to initialize FPGA interface");
    return false;
  }
  
  // Initialize real-time control systems
  gRFStateMachine.Initialize(&gRFController, &gPowerAmplifier);
  gDSPProcessor.Initialize();
  gProtectionSystem.Initialize(&gPowerAmplifier, &gRFController);
  
  // Initialize application coordination
  gTransceiverController.Initialize(&gRFController, &gPowerAmplifier, &gDSPProcessor);
  gHardwareManager.Initialize();
  
  // Set safe initial state
  gRFController.SetMode(NexRig::HW::RFController::Mode::Standby);
  gRFController.SetFrequency(14200000); // 20m band center
  gPowerAmplifier.SetTargetPower(10.0f); // 10W default
  
  LOG_INF("Hardware initialization complete");
  return true;
}

/**
 * @brief Emergency shutdown handler
 * 
 * Called on critical errors or external shutdown signals
 */
void EmergencyShutdown() {
  LOG_ERR("EMERGENCY SHUTDOWN INITIATED");
  
  // Signal all threads to stop
  gEmergencyShutdown.store(true);
  gSystemRunning.store(false);
  
  // Immediate hardware safety actions
  gRFController.SetMode(NexRig::HW::RFController::Mode::Standby);
  gPowerAmplifier.EmergencyShutdown();
  gProtectionSystem.TriggerEmergencyProtection();
  
  // Disable all RF outputs
  gFPGAInterface.SetFastTRSwitch(false);
  gFPGAInterface.TriggerFastProtection();
  
  LOG_ERR("Emergency shutdown complete - system safe");
}

/**
 * @brief Main application entry point
 * 
 * Initializes all subsystems and starts the main control threads.
 * The STM32 provides hardware mechanism only - all UI policy is in the browser.
 */
int main() {
  // Print startup banner
  printk("\n\n");
  printk("========================================\n");
  printk("NexRig SDR Transceiver Firmware v%s\n", NEXRIG_VERSION_STRING);
  printk("STM32H753 @ 480MHz - Built %s %s\n", __DATE__, __TIME__);
  printk("Hardware Abstraction & REST API Only\n");
  printk("UI Policy Implemented in Browser\n"); 
  printk("========================================\n\n");
  
  LOG_INF("Starting NexRig firmware initialization");
  
  // Initialize hardware subsystems
  if (!InitializeHardware()) {
    LOG_ERR("Hardware initialization failed - cannot continue");
    EmergencyShutdown();
    return -1;
  }
  
  // System is ready to run
  gSystemRunning.store(true);
  
  // Create and start real-time threads
  LOG_INF("Starting real-time control threads");
  
  NexRig::Utils::Threading::CreateThread<NexRig::Utils::Threading::Priority::Critical>(
    "RF_Control", RFControlThread, 8192);
    
  NexRig::Utils::Threading::CreateThread<NexRig::Utils::Threading::Priority::High>(
    "DSP_Processing", DSPThread, 16384);
    
  NexRig::Utils::Threading::CreateThread<NexRig::Utils::Threading::Priority::Normal>(
    "Communication", CommunicationThread, 32768);
    
  NexRig::Utils::Threading::CreateThread<NexRig::Utils::Threading::Priority::Low>(
    "Diagnostics", DiagnosticsThread, 8192);
  
  LOG_INF("All threads started - system operational");
  
  // Main thread becomes the watchdog and error handler
  while (gSystemRunning.load()) {
    // Check for system health issues
    if (!gProtectionSystem.IsSystemHealthy()) {
      LOG_ERR("Protection system detected unhealthy condition");
      EmergencyShutdown();
      break;
    }
    
    // Check FPGA responsiveness
    if (!gFPGAInterface.IsFPGAResponsive()) {
      LOG_ERR("FPGA not responding - emergency shutdown");
      EmergencyShutdown();
      break;
    }
    
    // Watchdog timer reset (if available)
    // wdt_feed(watchdogdevice, watchdogchannel);
    
    k_msleep(1000); // 1Hz watchdog rate
  }
  
  LOG_INF("Main thread exiting - system shutdown");
  
  // Clean shutdown if we get here
  gSystemRunning.store(false);
  
  // Wait for threads to terminate gracefully
  k_msleep(2000);
  
  // Final hardware shutdown
  gRFController.Shutdown();
  gPowerAmplifier.Shutdown();
  gFPGAInterface.Shutdown();
  
  LOG_INF("NexRig firmware shutdown complete");
  
  return 0;
}