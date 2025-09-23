/**
 * @file RfController.h
 * @brief RF Hardware Control Interface
 * 
 * Provides hardware abstraction for RF switching, frequency control,
 * and band management. This class implements pure hardware mechanism
 * with no UI policy decisions.
 * 
 * @copyright 2025 NexRig Project - MIT License
 */

#pragma once

#include <array>
#include <atomic>
#include <shared_mutex>
#include <chrono>
#include <span>

namespace NexRig::HW {

/**
 * @brief Main RF control interface for NexRig hardware
 * 
 * Controls frequency synthesis, band switching, TX/RX switching,
 * and antenna selection. Thread-safe with lock-free status queries
 * for real-time operation.
 */
class RfController {
public:
  /**
   * @brief Amateur radio band enumeration
   */
  enum class Band : uint8_t {
    Band160m = 0,  ///< 160 meters (1.8-2.0 MHz)
    Band80m  = 1,  ///< 80 meters (3.5-4.0 MHz)  
    Band40m  = 2,  ///< 40 meters (7.0-7.3 MHz)
    Band20m  = 3,  ///< 20 meters (14.0-14.35 MHz)
    Band17m  = 4,  ///< 17 meters (18.068-18.168 MHz)
    Band15m  = 5,  ///< 15 meters (21.0-21.45 MHz)
    Band12m  = 6,  ///< 12 meters (24.89-24.99 MHz)
    Band10m  = 7,  ///< 10 meters (28.0-29.7 MHz)
    Band6m   = 8,  ///< 6 meters (50.0-54.0 MHz)
    Band2m   = 9,  ///< 2 meters (144.0-148.0 MHz)
    BandCount = 10 ///< Total number of supported bands
  };
  
  /**
   * @brief Operating mode enumeration
   */
  enum class Mode : uint8_t {
    Standby,    ///< Safe standby mode - all RF disabled
    RX,         ///< Receive mode
    TX,         ///< Transmit mode
    Calibrate   ///< Calibration/test mode
  };
  
  /**
   * @brief Antenna selection enumeration
   */
  enum class Antenna : uint8_t {
    Antenna1 = 0,
    Antenna2 = 1,
    Antenna3 = 2,
    Antenna4 = 3,
    AntennaCount = 4
  };
  
  /**
   * @brief Frequency range specification for each band
   */
  struct FrequencyRange {
    uint32_t MinHz;     ///< Minimum frequency in Hz
    uint32_t MaxHz;     ///< Maximum frequency in Hz
    
    /**
     * @brief Check if frequency is within this range
     */
    constexpr bool Contains(uint32_t FreqHz) const noexcept {
      return FreqHz >= MinHz && FreqHz <= MaxHz;
    }
  };
  
  /**
   * @brief RF status structure for atomic status queries
   */
  struct RFStatus {
    uint32_t FrequencyHz;      ///< Current frequency in Hz
    Band CurrentBand;          ///< Current band selection
    Mode CurrentMode;          ///< Current operating mode
    Antenna CurrentAntenna;    ///< Current antenna selection
    bool PLLLocked;            ///< PLL lock status
    float ForwardPowerWatts;   ///< Forward power measurement
    float ReflectedPowerWatts; ///< Reflected power measurement
    float TemperatureC;        ///< RF section temperature
    std::chrono::steady_clock::time_point LastUpdate; ///< Status timestamp
  };
  
  // Band frequency ranges (compile-time constants)
  static constexpr std::array<FrequencyRange, static_cast<size_t>(Band::BandCount)> BandRanges {{
    {.MinHz = 1800000,   .MaxHz = 2000000},   // 160m
    {.MinHz = 3500000,   .MaxHz = 4000000},   // 80m
    {.MinHz = 7000000,   .MaxHz = 7300000},   // 40m
    {.MinHz = 14000000,  .MaxHz = 14350000},  // 20m
    {.MinHz = 18068000,  .MaxHz = 18168000},  // 17m
    {.MinHz = 21000000,  .MaxHz = 21450000},  // 15m
    {.MinHz = 24890000,  .MaxHz = 24990000},  // 12m
    {.MinHz = 28000000,  .MaxHz = 29700000},  // 10m
    {.MinHz = 50000000,  .MaxHz = 54000000},  // 6m
    {.MinHz = 144000000, .MaxHz = 148000000}  // 2m
  }};
  
  /**
   * @brief Constructor
   */
  RFController() = default;
  
  /**
   * @brief Destructor - ensures safe shutdown
   */
  ~RFController();
  
  // Non-copyable, non-movable (hardware singleton)
  RFController(const RFController&) = delete;
  RFController& operator=(const RFController&) = delete;
  RFController(RFController&&) = delete;
  RFController& operator=(RFController&&) = delete;
  
  /**
   * @brief Initialize RF controller hardware
   * @return true if initialization successful
   */
  bool Initialize();
  
  /**
   * @brief Shutdown RF controller and set to safe state
   */
  void Shutdown();
  
  /**
   * @brief Set operating frequency
   * @param FreqHz Frequency in Hz
   * @return true if frequency set successfully
   * @note Thread-safe, validates frequency against current band
   */
  bool SetFrequency(uint32_t FreqHz) noexcept;
  
  /**
   * @brief Set amateur radio band
   * @param TargetBand Band to switch to
   * @return true if band switch successful
   * @note Will select appropriate frequency within band if current frequency invalid
   */
  bool SetBand(Band TargetBand) noexcept;
  
  /**
   * @brief Set operating mode (RX/TX/Standby)
   * @param TargetMode Mode to switch to
   * @return true if mode switch successful
   * @note Thread-safe, ensures safe switching sequences
   */
  bool SetMode(Mode TargetMode) noexcept;
  
  /**
   * @brief Set antenna selection
   * @param TargetAntenna Antenna to select
   * @return true if antenna selection successful
   */
  bool SetAntenna(Antenna TargetAntenna) noexcept;
  
  /**
   * @brief Get current frequency (lock-free)
   * @return Current frequency in Hz
   */
  [[nodiscard]] uint32_t GetCurrentFrequency() const noexcept {
    return CurrentFrequencyHz_.load(std::memory_order_acquire);
  }
  
  /**
   * @brief Get current band (lock-free)
   * @return Current band selection
   */
  [[nodiscard]] Band GetCurrentBand() const noexcept {
    return CurrentBand_.load(std::memory_order_acquire);
  }
  
  /**
   * @brief Get current mode (lock-free)
   * @return Current operating mode
   */
  [[nodiscard]] Mode GetCurrentMode() const noexcept {
    return CurrentMode_.load(std::memory_order_acquire);
  }
  
  /**
   * @brief Get current antenna (lock-free)
   * @return Current antenna selection
   */
  [[nodiscard]] Antenna GetCurrentAntenna() const noexcept {
    return CurrentAntenna_.load(std::memory_order_acquire);
  }
  
  /**
   * @brief Get complete RF status (lock-free)
   * @return Current RF status structure
   * @note This provides a consistent snapshot of all RF parameters
   */
  [[nodiscard]] RFStatus GetRFStatus() const noexcept;
  
  /**
   * @brief Check if PLL is locked
   * @return true if PLL locked
   */
  [[nodiscard]] bool IsPLLLocked() const noexcept;
  
  /**
   * @brief Get forward power measurement
   * @return Forward power in watts
   */
  [[nodiscard]] float GetForwardPower() const noexcept;
  
  /**
   * @brief Get reflected power measurement  
   * @return Reflected power in watts
   */
  [[nodiscard]] float GetReflectedPower() const noexcept;
  
  /**
   * @brief Calculate SWR from forward/reflected power
   * @return SWR ratio (1.0 = perfect match)
   */
  [[nodiscard]] float GetSWR() const noexcept;
  
  /**
   * @brief Get RF section temperature
   * @return Temperature in Celsius
   */
  [[nodiscard]] float GetTemperature() const noexcept;
  
  /**
   * @brief Determine band from frequency
   * @param FreqHz Frequency in Hz
   * @return Band containing this frequency, or nullopt if out of range
   */
  [[nodiscard]] static std::optional<Band> FrequencyToBand(uint32_t FreqHz) noexcept;
  
  /**
   * @brief Get frequency range for a band
   * @param TargetBand Band to query
   * @return Frequency range for the band
   */
  [[nodiscard]] static constexpr FrequencyRange GetBandRange(Band TargetBand) noexcept {
    return BandRanges[static_cast<size_t>(TargetBand)];
  }
  
  /**
   * @brief Get string name for band
   * @param TargetBand Band to get name for
   * @return Human-readable band name
   */
  [[nodiscard]] static const char* GetBandName(Band TargetBand) noexcept;
  
  /**
   * @brief Emergency stop - immediate safe state
   * @note Can be called from ISR context
   */
  void EmergencyStop() noexcept;

private:
  // Atomic state for lock-free reads
  std::atomic<uint32_t> CurrentFrequencyHz_{14200000}; // Default to 20m
  std::atomic<Band> CurrentBand_{Band::Band20m};
  std::atomic<Mode> CurrentMode_{Mode::Standby};
  std::atomic<Antenna> CurrentAntenna_{Antenna::Antenna1};
  
  // Hardware status (updated by background task)
  std::atomic<bool> PLLLocked_{false};
  std::atomic<float> ForwardPowerWatts_{0.0f};
  std::atomic<float> ReflectedPowerWatts_{0.0f};
  std::atomic<float> TemperatureC_{25.0f};
  
  // Configuration protection for complex operations
  mutable std::shared_mutex ConfigMutex_;
  
  // Hardware interfaces
  class PinDiodeMatrix* PinMatrix_{nullptr};
  class PLLSynthesizer* PLLSynth_{nullptr};
  class PowerMeter* PowerMeter_{nullptr};
  
  // Initialization state
  std::atomic<bool> Initialized_{false};
  
  // Internal methods
  bool ConfigurePLLForFrequency(uint32_t FreqHz) noexcept;
  bool ConfigureBandFilters(Band TargetBand) noexcept;
  bool ConfigureTRSwitching(Mode TargetMode) noexcept;
  bool ConfigureAntennaSwitch(Antenna TargetAntenna) noexcept;
  void UpdateHardwareStatus() noexcept;
  
  // Safety validation
  bool ValidateFrequencyForBand(uint32_t FreqHz, Band TargetBand) const noexcept;
  bool ValidateModeTransition(Mode FromMode, Mode ToMode) const noexcept;
  
  // Hardware abstraction helpers
  void WriteRegister(uint32_t Address, uint32_t Value) noexcept;
  [[nodiscard]] uint32_t ReadRegister(uint32_t Address) const noexcept;
};

} // namespace NexRig::HW