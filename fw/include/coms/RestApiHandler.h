/**
 * @file RESTAPIHandler.h
 * @brief REST API Handler for NexRig Hardware Control
 * 
 * Provides pure hardware mechanism through REST endpoints.
 * NO UI policy decisions - just hardware abstraction for the browser.
 * All user interface logic and setbox management happens in JavaScript.
 * 
 * @copyright 2025 NexRig Project - MIT License
 */

#pragma once

#include <string>
#include <functional>
#include <unordered_map>
#include <nlohmann/json.hpp>
#include "hw/RFController.h"
#include "hw/PowerAmplifier.h"
#include "rt/ProtectionSystem.h"

namespace NexRig::Coms {

/**
 * @brief REST API handler for hardware control
 * 
 * Exposes hardware capabilities through standard REST endpoints.
 * The STM32 provides mechanism only - policy is implemented in browser.
 */
class RESTAPIHandler {
public:
  /**
   * @brief API response structure
   */
  struct APIResponse {
    enum class Status {
      Success,        ///< Operation completed successfully
      Error,          ///< Generic error occurred
      InvalidParam,   ///< Invalid parameter provided
      HardwareError,  ///< Hardware operation failed
      NotFound,       ///< Endpoint not found
      MethodNotAllowed ///< HTTP method not supported
    };
    
    Status StatusCode;           ///< Response status
    std::string Message;         ///< Human-readable status message
    nlohmann::json Data;         ///< Response data payload
    uint32_t TimestampMs;        ///< Response timestamp
    
    /**
     * @brief Convert to JSON for HTTP response
     */
    [[nodiscard]] nlohmann::json ToJSON() const;
    
    /**
     * @brief Create success response
     */
    static APIResponse Success(const nlohmann::json& Data = {}, 
                              const std::string& Message = "OK");
    
    /**
     * @brief Create error response
     */
    static APIResponse Error(Status Code, const std::string& Message);
  };
  
  /**
   * @brief HTTP method enumeration
   */
  enum class HTTPMethod {
    GET,
    POST,
    PUT,
    DELETE,
    OPTIONS
  };
  
  /**
   * @brief Request handler function type
   */
  using RequestHandler = std::function<APIResponse(const nlohmann::json& Params, 
                                                   const nlohmann::json& Body)>;
  
  /**
   * @brief Constructor
   */
  explicit RESTAPIHandler(HW::RFController* RFController,
                         HW::PowerAmplifier* PowerAmp,
                         RT::ProtectionSystem* Protection);
  
  /**
   * @brief Initialize API handler and register routes
   */
  void Initialize();
  
  /**
   * @brief Register API routes with HTTP server
   */
  void RegisterRoutes(class HTTPServer* Server);
  
  /**
   * @brief Handle incoming REST API request
   * @param Method HTTP method
   * @param Path Request path
   * @param Params Query parameters
   * @param Body Request body
   * @return API response
   */
  APIResponse HandleRequest(HTTPMethod Method,
                           const std::string& Path,
                           const nlohmann::json& Params,
                           const nlohmann::json& Body);

private:
  // Hardware interfaces
  HW::RFController* RFController_;
  HW::PowerAmplifier* PowerAmp_;
  RT::ProtectionSystem* Protection_;
  
  // Route registration
  struct RouteInfo {
    HTTPMethod Method;
    std::string Path;
    RequestHandler Handler;
    std::string Description;
  };
  
  std::vector<RouteInfo> Routes_;
  
  /**
   * @brief Register a route handler
   */
  void RegisterRoute(HTTPMethod Method, 
                    const std::string& Path,
                    RequestHandler Handler,
                    const std::string& Description);
  
  // ============================================================================
  // RF CONTROL API ENDPOINTS - Pure hardware mechanism
  // ============================================================================
  
  /**
   * @brief GET /api/v1/rf/status
   * @brief Get current RF hardware status
   */
  APIResponse GetRFStatus(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/rf/frequency
   * @brief Set operating frequency
   * Body: { "frequency_hz": 14200000 }
   */
  APIResponse SetFrequency(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/rf/band  
   * @brief Set amateur radio band
   * Body: { "band": "20m" } or { "band": 3 }
   */
  APIResponse SetBand(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/rf/mode
   * @brief Set operating mode (RX/TX/Standby)
   * Body: { "mode": "rx" }
   */
  APIResponse SetMode(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/rf/antenna
   * @brief Set antenna selection
   * Body: { "antenna": 1 }
   */
  APIResponse SetAntenna(const nlohmann::json& Params, const nlohmann::json& Body);
  
  // ============================================================================
  // POWER AMPLIFIER API ENDPOINTS
  // ============================================================================
  
  /**
   * @brief GET /api/v1/pa/status
   * @brief Get power amplifier status
   */
  APIResponse GetPowerAmplifierStatus(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/pa/power
   * @brief Set target output power
   * Body: { "power_watts": 50.0 }
   */
  APIResponse SetPower(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief GET /api/v1/pa/efficiency
   * @brief Get current PA efficiency metrics
   */
  APIResponse GetPowerEfficiency(const nlohmann::json& Params, const nlohmann::json& Body);
  
  // ============================================================================
  // PROTECTION SYSTEM API ENDPOINTS  
  // ============================================================================
  
  /**
   * @brief GET /api/v1/protection/status
   * @brief Get protection system status
   */
  APIResponse GetProtectionStatus(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief POST /api/v1/protection/reset
   * @brief Reset protection system after fault
   */
  APIResponse ResetProtection(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/protection/limits
   * @brief Set protection limits
   * Body: { "max_power_watts": 100.0, "max_temp_c": 85.0 }
   */
  APIResponse SetProtectionLimits(const nlohmann::json& Params, const nlohmann::json& Body);
  
  // ============================================================================
  // HARDWARE STATE MANAGEMENT API ENDPOINTS
  // ============================================================================
  
  /**
   * @brief POST /api/v1/state/save
   * @brief Save current hardware state
   * Body: { "state_name": "my_config", "description": "Contest setup" }
   */
  APIResponse SaveHardwareState(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/state/restore
   * @brief Restore saved hardware state
   * Body: { "state_name": "my_config" }
   */
  APIResponse RestoreHardwareState(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief GET /api/v1/state/list
   * @brief List all saved hardware states
   */
  APIResponse ListSavedStates(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief DELETE /api/v1/state/{state_name}
   * @brief Delete a saved hardware state
   */
  APIResponse DeleteSavedState(const nlohmann::json& Params, const nlohmann::json& Body);
  
  // ============================================================================
  // CALIBRATION AND TEST API ENDPOINTS
  // ============================================================================
  
  /**
   * @brief POST /api/v1/calibration/start
   * @brief Enter calibration mode
   * Body: { "calibration_type": "power" | "frequency" | "phase" }
   */
  APIResponse StartCalibration(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief POST /api/v1/calibration/stop
   * @brief Exit calibration mode
   */
  APIResponse StopCalibration(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief PUT /api/v1/test/signal
   * @brief Generate test signal
   * Body: { "frequency_hz": 14200000, "amplitude_db": -10.0, "modulation": "cw" }
   */
  APIResponse SetTestSignal(const nlohmann::json& Params, const nlohmann::json& Body);
  
  // ============================================================================
  // DIAGNOSTICS AND MONITORING API ENDPOINTS
  // ============================================================================
  
  /**
   * @brief GET /api/v1/diagnostics/hardware
   * @brief Get comprehensive hardware diagnostics
   */
  APIResponse GetHardwareDiagnostics(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief GET /api/v1/diagnostics/temperatures
   * @brief Get all temperature sensor readings
   */
  APIResponse GetTemperatures(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief GET /api/v1/diagnostics/performance
   * @brief Get system performance metrics
   */
  APIResponse GetPerformanceMetrics(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief GET /api/v1/diagnostics/fpga
   * @brief Get FPGA status and version information
   */
  APIResponse GetFPGADiagnostics(const nlohmann::json& Params, const nlohmann::json& Body);
  
  // ============================================================================
  // SYSTEM CONTROL API ENDPOINTS
  // ============================================================================
  
  /**
   * @brief POST /api/v1/system/emergency_stop
   * @brief Trigger emergency shutdown
   */
  APIResponse EmergencyStop(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief GET /api/v1/system/version
   * @brief Get firmware version and build information
   */
  APIResponse GetSystemVersion(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief GET /api/v1/system/capabilities
   * @brief Get hardware capabilities and supported features
   */
  APIResponse GetSystemCapabilities(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief POST /api/v1/system/restart
   * @brief Restart system (graceful reboot)
   */
  APIResponse RestartSystem(const nlohmann::json& Params, const nlohmann::json& Body);
  
  // ============================================================================
  // HELPER METHODS
  // ============================================================================
  
  /**
   * @brief Convert band string to enum
   * @param BandStr Band string ("20m", "40m", etc.)
   * @return Band enum value or nullopt if invalid
   */
  [[nodiscard]] std::optional<HW::RFController::Band> ParseBandString(const std::string& BandStr) const;
  
  /**
   * @brief Convert band enum to string
   * @param Band Band enum value
   * @return String representation
   */
  [[nodiscard]] std::string BandToString(HW::RFController::Band Band) const;
  
  /**
   * @brief Convert mode string to enum
   * @param ModeStr Mode string ("rx", "tx", "standby")
   * @return Mode enum value or nullopt if invalid
   */
  [[nodiscard]] std::optional<HW::RFController::Mode> ParseModeString(const std::string& ModeStr) const;
  
  /**
   * @brief Convert mode enum to string
   * @param Mode Mode enum value
   * @return String representation
   */
  [[nodiscard]] std::string ModeToString(HW::RFController::Mode Mode) const;
  
  /**
   * @brief Validate frequency parameter
   * @param FreqHz Frequency in Hz
   * @return true if frequency is valid for amateur radio use
   */
  [[nodiscard]] bool ValidateFrequency(uint32_t FreqHz) const;
  
  /**
   * @brief Validate power parameter
   * @param PowerWatts Power in watts
   * @return true if power level is safe and achievable
   */
  [[nodiscard]] bool ValidatePower(float PowerWatts) const;
  
  /**
   * @brief Get current timestamp in milliseconds
   * @return Timestamp since system boot
   */
  [[nodiscard]] uint32_t GetTimestampMs() const;
  
  /**
   * @brief Handle CORS preflight requests
   * @return CORS headers for browser compatibility
   */
  APIResponse HandleCORSPreflight(const nlohmann::json& Params, const nlohmann::json& Body);
  
  /**
   * @brief Add CORS headers to response
   * @param Response Response to modify
   */
  void AddCORSHeaders(APIResponse& Response) const;
  
  /**
   * @brief Validate request parameters
   * @param RequiredParams List of required parameter names
   * @param Params Actual parameters
   * @return Error response if validation fails, nullopt if OK
   */
  [[nodiscard]] std::optional<APIResponse> ValidateRequiredParams(
    const std::vector<std::string>& RequiredParams,
    const nlohmann::json& Params) const;
  
  /**
   * @brief Safe JSON parameter extraction with type checking
   * @tparam T Expected parameter type
   * @param JSON JSON object to extract from
   * @param Key Parameter key
   * @param DefaultValue Default value if key missing
   * @return Extracted value or default
   */
  template<typename T>
  [[nodiscard]] T SafeGetParam(const nlohmann::json& JSON, 
                               const std::string& Key, 
                               const T& DefaultValue) const {
    try {
      if (JSON.contains(Key) && !JSON[Key].is_null()) {
        return JSON[Key].get<T>();
      }
    } catch (const nlohmann::json::exception&) {
      // Type conversion failed, return default
    }
    return DefaultValue;
  }
};

} // namespace NexRig::Coms