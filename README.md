# My Frontier Silicon Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A complete and feature-rich Home Assistant integration for Frontier Silicon-based internet radios, including:
- **Majority Homerton** (all models)
- **Roberts Stream** series
- **Hama IR** series
- **Medion LifeStream**
- **Auna Connect** radios
- And many more Frontier Silicon devices!

## Why This Integration?

The built-in Home Assistant Frontier Silicon integration is basic and doesn't expose many features. This **Advanced** version gives you:

### ✨ Key Features

- 🎛️ **Full Media Player Control** - Power, volume, mute, play/pause
- 📻 **Complete Source Switching** - Switch between Internet Radio, DAB+, FM, Spotify, Bluetooth, CD, USB, AUX
- ⭐ **Preset Selection** - Direct access to your favorite radio stations via dropdown
- 🔄 **Automatic Discovery** - Auto-detects all capabilities of your specific radio model
- 📊 **Rich Sensors** - Current mode, station info, playback details
- 🖼️ **Album Art** - Displays station logos and album artwork
- 🔘 **Utility Buttons** - Refresh presets when you add new stations
- 🎨 **Clean UI** - Perfectly integrated into Home Assistant's interface
- ⚡ **Fast & Reliable** - Efficient polling with session management

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on **Integrations**
3. Click the **3 dots** menu → **Custom repositories**
4. Add this repository URL: `https://github.com/SaintPaddy/my-frontier-silicon`
5. Category: **Integration**
6. Click **Add**
7. Find "My Frontier Silicon" in HACS
8. Click **Download**
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/my_frontier_silicon` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for **My Frontier Silicon**
4. Enter your device details:
   - **IP Address**: Your radio's IP (e.g., `10.8.11.30`)
   - **Port**: Usually `80` (default)
   - **PIN**: Usually `1234` (check your radio's settings)
   - **Name**: Friendly name for your device

The integration will automatically:
- ✅ Test the connection
- ✅ Discover all available modes
- ✅ Load all your presets
- ✅ Create all entities

## Entities Created

For each radio, the integration creates:

### Media Player
- **Main control** - Power, volume, source selection, playback control
- Shows current station/track, artist, album
- Displays station logo or album art

### Select
- **Radio Preset Selector** - Dropdown to choose from your saved stations
- Automatically updates when you add/remove presets

### Sensors
- **Current Mode** - Shows which source is active (Internet Radio, DAB+, etc.)
- **Current Station** - Shows station name with additional info in attributes

### Buttons
- **Refresh Presets** - Update the preset list after adding new stations on the radio

## Usage Examples

### Dashboard Card

**Basic Media Control:**
```yaml
type: media-control
entity: media_player.homerton_2
```

**Advanced Card with All Features:**
```yaml
type: vertical-stack
cards:
  # Main media player
  - type: media-control
    entity: media_player.homerton_2
  
  # Preset selector
  - type: entities
    entities:
      - entity: select.homerton_2_radio_preset
        name: Select Station
  
  # Mode and station info
  - type: entities
    title: Radio Info
    entities:
      - entity: sensor.homerton_2_current_mode
      - entity: sensor.homerton_2_current_station
      - entity: button.homerton_2_refresh_presets
```

### Automations

**Morning Radio:**
```yaml
automation:
  - alias: "Morning Radio"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday: [mon, tue, wed, thu, fri]
    action:
      # Turn on radio
      - service: media_player.turn_on
        target:
          entity_id: media_player.homerton_2
      # Select Internet Radio mode
      - service: media_player.select_source
        target:
          entity_id: media_player.homerton_2
        data:
          source: "Internet radio"
      # Select your favorite morning station
      - service: select.select_option
        target:
          entity_id: select.homerton_2_radio_preset
        data:
          option: "1LIVE"
      # Set comfortable volume
      - service: media_player.volume_set
        target:
          entity_id: media_player.homerton_2
        data:
          volume_level: 0.3
```

**Welcome Home Radio:**
```yaml
automation:
  - alias: "Welcome Home Radio"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "home"
    condition:
      - condition: time
        after: "17:00:00"
        before: "22:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.homerton_2_radio_preset
        data:
          option: "Bremen Vier"
```

**Radio Sleep Timer:**
```yaml
automation:
  - alias: "Radio Bedtime Shutoff"
    trigger:
      - platform: time
        at: "22:30:00"
    action:
      - service: media_player.turn_off
        target:
          entity_id: media_player.homerton_2
```

### Scripts

**Quick Station Selection:**
```yaml
script:
  play_morning_news:
    alias: "Play Morning News"
    sequence:
      - service: media_player.turn_on
        target:
          entity_id: media_player.homerton_2
      - service: select.select_option
        target:
          entity_id: select.homerton_2_radio_preset
        data:
          option: "NDR 2"
  
  play_evening_music:
    alias: "Play Evening Music"
    sequence:
      - service: select.select_option
        target:
          entity_id: select.homerton_2_radio_preset
        data:
          option: "Sky Radio"
```

## Features by Radio Model

| Feature | Homerton 2 | Roberts Stream | Most Frontier Radios |
|---------|-----------|----------------|---------------------|
| Power Control | ✅ | ✅ | ✅ |
| Volume Control | ✅ | ✅ | ✅ |
| Mode Switching | ✅ | ✅ | ✅ |
| Preset Selection | ✅ | ✅ | ✅ |
| Play/Pause | Internet Radio: ⚠️ | ✅ | Varies |
| Next/Prev Track | CD/USB: ✅ | ✅ | Varies |
| Album Art | ✅ | ✅ | ✅ |

⚠️ = Feature may not work in all modes

## Troubleshooting

### Connection Issues

**Cannot connect to device:**
1. Verify the IP address: `ping 10.8.11.30`
2. Check the radio is powered on (not just standby)
3. Verify the PIN (usually `1234`, check radio settings)
4. Ensure port `80` is not blocked by firewall

### Presets Not Showing

1. Make sure you have presets saved on the radio
2. Switch to Internet Radio mode on the radio
3. Click the **Refresh Presets** button
4. Check Home Assistant logs for errors

### Commands Not Working

1. Ensure radio is fully powered on (not standby)
2. Some commands only work in specific modes (e.g., pause doesn't work for streaming radio)
3. Check the integration logs in Home Assistant

### Finding Your Radio's IP Address

**Option 1: Router**
- Log into your router
- Look for "Frontier Silicon", "Homerton", or your radio's name
- Note the IP address

**Option 2: Radio Display**
- Go to radio's settings menu
- Navigate to Network → Network Settings
- View IP address

**Option 3: Network Scan**
```bash
# Linux/Mac
sudo nmap -sn 192.168.1.0/24 | grep -B2 "Frontier\|Homerton"

# Or use an app like Fing on your phone
```

## Advanced Configuration

### Static IP (Recommended)

Set a static IP for your radio in your router's DHCP settings to prevent the IP from changing.

### Custom Port

If your radio uses a non-standard port (rare), specify it during setup.

### Multiple Radios

You can add multiple Frontier Silicon radios! Each will get its own set of entities:
- `media_player.homerton_2`
- `media_player.roberts_stream_94i`
- etc.

## Supported Devices

This integration works with **any device using the Frontier Silicon platform**, including:

### Majority
- Homerton (all models)
- Oakington
- Peterhouse
- Willingham

### Roberts
- Stream series (93i, 94i, 218, etc.)
- Revival series

### Hama
- IR series
- DIR series

### Other Brands
- Medion LifeStream
- Auna Connect
- Technisat DigitRadio
- Revo SuperConnect
- Silvercrest
- Many more!

**How to check:** If your radio has the Frontier Silicon chipset and exposes an API at `http://[IP]/fsapi`, it will work!

## Comparison with Native Integration

| Feature | This Integration | Native HA Integration |
|---------|-----------------|----------------------|
| Power Control | ✅ | ✅ |
| Volume Control | ✅ | ✅ |
| Mode Switching | ✅ | ✅ |
| **Preset Selection** | ✅ **Dropdown** | ❌ Not Available |
| **Mode Sensor** | ✅ | ❌ |
| **Station Info Sensor** | ✅ | ⚠️ Limited |
| **Refresh Button** | ✅ | ❌ |
| **Clean UI** | ✅ Modern | ⚠️ Basic |
| **Auto-discovery** | ✅ Full | ⚠️ Partial |

## Contributing

Found a bug? Have a feature request? Want to add support for a new device?

1. Open an issue on GitHub
2. Provide Home Assistant logs
3. Include your radio model
4. Describe expected vs actual behavior

Pull requests welcome!

## Credits

Created for the Home Assistant community by radio enthusiasts!

Special thanks to:
- The Home Assistant team
- Frontier Silicon for their API
- All the beta testers and contributors

## License

MIT License - feel free to use, modify, and share!

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/SaintPaddy/my-frontier-silicon/issues)
- 💬 **Discussion**: [Home Assistant Community](https://community.home-assistant.io/)
- ⭐ **Star this repo** if you find it useful!

---

**Enjoy your smart radio! 📻✨**
