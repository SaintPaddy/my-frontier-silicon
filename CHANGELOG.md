# Changelog - My Frontier Silicon

All notable changes to this integration will be documented in this file.

## [0.0.4] - 2024-12-26

### 🐛 Bug Fixes

**Sleep Timer Fixed!**
- **Fixed seconds/minutes confusion:** API uses seconds, but UI displays minutes
  - Setting 30 minutes now correctly sets 30 minutes (not 30 seconds!)
  - Sleep timer value properly converts between seconds (API) and minutes (display)
  - Setting to 0 now properly cancels the timer
  - Timer automatically counts down and updates in UI

**WiFi Signal Improved!**
- Fixed WiFi RSSI sensor showing no value
- Added unsigned-to-signed conversion (some APIs return 0-255 instead of -128 to 0)
- Handles invalid values (0) by showing as unavailable
- RSSI values now display correctly as negative dBm

### ✨ New Features

**Sleep Timer Enhancements** ⭐⭐⭐
- **New:** `sensor.{device}_sleep_remaining` - Shows remaining time with countdown
  - Displays minutes remaining
  - Shows formatted time (MM:SS) in attributes
  - Icon changes when active
  - Auto-updates every 30 seconds

**Device Information Sensors** ⭐⭐
- **New:** `sensor.{device}_firmware_version` - Shows firmware version
- **New:** `sensor.{device}_device_model` - Shows device model name
- Both loaded once at startup (diagnostic sensors)

**Volume Percentage Sensor** ⭐
- **New:** `sensor.{device}_volume_percent` - Shows volume as 0-100%
  - Dynamic icon based on volume level (off/low/medium/high)
  - Easier to read than raw volume steps

**Sleep Timer Quick Buttons** 📚
- Complete documentation with 3 implementation methods
- Dashboard button examples (15/30/60/90 min presets)
- Script examples for reusable buttons
- Helper/automation examples for dropdown
- See `SLEEP_TIMER_QUICK_BUTTONS.md` for details

### 📊 Complete Entity List (18 Total)

**Selectors (3):**
- select.{device}_preset
- select.{device}_input_mode
- select.{device}_equalizer

**Number (1):**
- number.{device}_sleep_timer

**Switches (2):**
- switch.{device}_bluetooth_mode
- switch.{device}_spotify_mode

**Sensors (10):**
- sensor.{device}_current_mode
- sensor.{device}_current_station
- sensor.{device}_sleep_remaining (NEW!)
- sensor.{device}_volume_percent (NEW!)
- sensor.{device}_wifi_signal (FIXED!)
- sensor.{device}_wifi_ssid
- sensor.{device}_ip_address
- sensor.{device}_mac_address
- sensor.{device}_firmware_version (NEW!)
- sensor.{device}_device_model (NEW!)

**Media Player & Button (2):**
- media_player.{device}
- button.{device}_refresh_presets

### 📝 Technical Details
- Sleep timer: multiply by 60 when setting (min→sec), divide by 60 when reading (sec→min)
- WiFi RSSI: convert unsigned 8-bit to signed 8-bit if value > 127
- Device info: fetched once at startup, cached for performance
- Volume percentage: calculated from raw volume / volume steps
- All new sensors properly categorized (diagnostic/standard)

## [0.0.3] - 2024-12-14

### 🎉 MEGA FEATURE RELEASE!

This is a **major update** with tons of new features based on your radio's capabilities!

### ✨ New Features

**1. Multi-Mode Smart Preset Selector** ⭐⭐⭐
- **30 presets across all modes!** (Internet Radio, DAB+, FM)
- One unified dropdown with all your stations
- Format: `[Radio] 1LIVE`, `[DAB+] Bremen Vier`, `[FM] 89.3 MHz`
- **Auto mode-switching:** Click any preset and it automatically switches to the right mode!
- **Excludes empty presets:** Only shows stations you've actually saved

**2. Sleep Timer** ⭐⭐⭐
- Beautiful slider: 0-120 minutes in 5-minute increments
- Icon changes when active

**3. EQ Preset Selector** ⭐⭐
- 6 equalizer presets

**4. Full Spotify & Bluetooth** ⭐⭐
- Quick mode switches

**5. WiFi Network Sensors** ⭐
- Signal, IP, MAC, SSID

### 📊 Complete: 14 entities total

## [0.0.2] - 2024-12-14
- Bug fixes

## [0.0.1] - 2024-12-14
- Initial release
