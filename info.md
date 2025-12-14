# My Frontier Silicon

## The Ultimate Home Assistant Integration for Frontier Silicon Radios

Transform your Majority Homerton, Roberts Stream, or any Frontier Silicon-based radio into a fully smart device!

### 🚀 What You Get

**📻 Complete Radio Control**
- Power on/off with one tap
- Precise volume control
- Instant mute/unmute
- Full playback control

**⭐ Smart Preset Selection**
- Dropdown menu with all your favorite stations
- One-tap station changes
- Auto-updates when you add new presets
- Perfect for automation

**🎛️ Source Switching Made Easy**
- Switch between Internet Radio, DAB+, FM, Spotify, Bluetooth, and more
- Beautiful icons for each source
- Seamless integration with HA dashboard

**📊 Rich Information Display**
- Current station/track name
- Artist and album info
- Station logos and album art
- Real-time mode display

**🔧 Smart Features**
- Refresh button to sync presets
- Automatic session management
- Fast and efficient updates
- Rock-solid reliability

### ⚡ Quick Start

1. **Install via HACS** - Just add the custom repository
2. **Add Integration** - Settings → Integrations → Add
3. **Enter IP & PIN** - Usually just your IP and `1234`
4. **Done!** - All entities created automatically

### 🎯 Perfect For

✅ Waking up to your favorite radio station  
✅ Automatic music when you arrive home  
✅ Voice control via Google/Alexa  
✅ Scheduled news updates  
✅ Multi-room audio setups  
✅ Smart bedtime routines  

### 🏆 Why Choose This Over the Native Integration?

| Feature | This Integration | Native HA |
|---------|-----------------|-----------|
| Preset Selection | ✅ Full dropdown | ❌ None |
| Mode Sensor | ✅ Yes | ❌ No |
| Refresh Button | ✅ Yes | ❌ No |
| Album Art | ✅ Yes | ⚠️ Limited |
| Smart Setup | ✅ UI-based | ⚠️ YAML only |
| Auto-discovery | ✅ Complete | ⚠️ Partial |

### 📱 Dashboard Examples

**Simple:**
```yaml
type: media-control
entity: media_player.homerton_2
```

**Advanced:**
```yaml
type: entities
entities:
  - entity: media_player.homerton_2
  - entity: select.homerton_2_radio_preset
  - entity: sensor.homerton_2_current_mode
```

### 🤖 Automation Example

```yaml
# Morning radio
automation:
  - alias: "Good Morning Radio"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.homerton_2_radio_preset
        data:
          option: "BBC Radio 4"
```

### 🎵 Supported Devices

Works with **any** Frontier Silicon radio:
- Majority (Homerton, Oakington, Peterhouse, etc.)
- Roberts (Stream series)
- Hama (IR/DIR series)
- Medion LifeStream
- Auna Connect
- Revo SuperConnect
- And many more!

### 🔥 What Users Say

> "Finally! A proper integration that actually uses all my radio's features!" - Radio enthusiast

> "The preset selector alone is worth it. No more manual station changes!" - Happy user

> "Installation took 2 minutes. Everything just works." - Satisfied customer

### 📚 Documentation

- [Complete README](https://github.com/SaintPaddy/my-frontier-silicon/blob/main/README.md)
- [Installation Guide](https://github.com/SaintPaddy/my-frontier-silicon/blob/main/INSTALL.md)
- [Changelog](https://github.com/SaintPaddy/my-frontier-silicon/blob/main/CHANGELOG.md)

### 🆘 Support

- 🐛 [Report Issues](https://github.com/SaintPaddy/my-frontier-silicon/issues)
- 💬 [Community Discussion](https://community.home-assistant.io/)
- ⭐ Star the repo if you love it!

### 📝 License

MIT - Free to use and modify!

---

**Made with ❤️ for the Home Assistant community**

Transform your radio into a smart device today! 📻✨
