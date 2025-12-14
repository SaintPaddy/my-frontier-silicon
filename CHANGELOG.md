# Changelog

All notable changes to the My Frontier Silicon integration will be documented in this file.

## [1.0.0] - 2024-12-14

### 🎉 Initial Release

#### Added
- Complete media player entity with full control
  - Power on/off
  - Volume control (set, up, down)
  - Mute/unmute
  - Source/mode selection
  - Play/pause/stop controls
  - Next/previous track
  - Album art display
- Select entity for preset/station selection
  - Dropdown with all saved presets
  - Automatic filtering of unnamed presets
  - Smart mode switching (auto-switches to Internet Radio)
- Sensor entities
  - Current mode display with smart icons
  - Current station/track information
  - Additional attributes for extended info
- Button entity
  - Refresh presets button
  - Updates preset list without reloading integration
- Config flow for easy setup via UI
  - Connection testing
  - Automatic device discovery
  - PIN validation
  - Smart port handling (omits :80 from URLs)
- Comprehensive error handling
  - Session management with auto-reconnection
  - Timeout handling
  - Clear error messages
- Full async support
  - Efficient polling with coordinator
  - Non-blocking operations
  - Proper cleanup on unload
- HACS compatibility
  - Custom repository support
  - Automatic updates
  - Version tracking
- Complete documentation
  - README with examples
  - Installation guide
  - Troubleshooting section
- Multi-language support (EN)
- Device info with proper identification
- Support for all Frontier Silicon devices
  - Majority Homerton series
  - Roberts Stream series
  - Hama radios
  - And many more!

### Features Tested On
- ✅ Majority Homerton 2
- ✅ Firmware: V4.5.21
- ✅ All modes: Internet Radio, DAB+, FM, Spotify, Bluetooth, CD, USB, AUX
- ✅ Preset selection working
- ✅ Volume control (33 steps)
- ✅ Mode switching
- ✅ Station metadata
- ✅ Album art URLs

### Technical Details
- Integration domain: `my_frontier_silicon`
- Platform: Home Assistant 2024.1+
- Dependencies: aiohttp
- Update interval: 30 seconds
- Session refresh: Every 9 minutes
- Supported platforms: media_player, select, sensor, button

### Known Limitations
- Pause/Next/Prev may not work in Internet Radio mode (this is a radio limitation, not integration)
- Multiroom features not implemented (device dependent)
- Some advanced EQ settings not exposed (planned for future release)

## [Unreleased]

### Planned Features
- 🎚️ EQ preset selector
- ⏰ Sleep timer entity
- 📡 Signal strength sensor
- 🔊 Audio enhancement controls
- 🌐 Network info sensors
- 📻 DAB scan button
- 🎨 Theme presets
- 🔔 Notification support

### Considering
- MQTT discovery support
- Custom services for advanced features
- Lovelace card plugin
- Multiple device grouping
- Scene support

---

## Version History

### Semantic Versioning
This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality
- PATCH version for backwards-compatible bug fixes

### Release Schedule
- Bug fixes: As needed
- Feature updates: Monthly
- Major versions: Quarterly (if needed)

---

[1.0.0]: https://github.com/SaintPaddy/my-frontier-silicon/releases/tag/v1.0.0
