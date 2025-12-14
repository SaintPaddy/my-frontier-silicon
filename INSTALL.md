# Installation Guide - My Frontier Silicon

## Prerequisites

- Home Assistant 2024.1.0 or newer
- HACS installed (recommended) OR manual installation capability
- Your radio's IP address
- Your radio's PIN code (usually `1234`)

## Method 1: HACS Installation (Recommended)

### Step 1: Add Custom Repository

1. Open **HACS** in Home Assistant
2. Click on **Integrations**
3. Click the **⋮** (three dots menu) in the top right
4. Select **Custom repositories**
5. Enter the repository URL:
   ```
   https://github.com/SaintPaddy/my-frontier-silicon
   ```
6. Select category: **Integration**
7. Click **Add**

### Step 2: Install the Integration

1. In HACS, search for **"My Frontier Silicon"**
2. Click on it
3. Click **Download** (bottom right)
4. Select the latest version
5. Click **Download** again

### Step 3: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart** (top right)
3. Confirm restart

### Step 4: Add Your Radio

1. After restart, go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION** (bottom right)
3. Search for **"My Frontier Silicon"**
4. Click on it

### Step 5: Configure

Enter your radio's details:

**IP Address:** 
- Find this in your router or radio settings
- Example: `10.8.11.30` or `192.168.1.50`

**Port:**
- Usually `80`
- Leave as default unless you know it's different

**PIN Code:**
- Usually `1234`
- Check your radio's settings if different
- Some radios show PIN in Settings → Network

**Name:**
- Friendly name for your radio
- Example: "Living Room Radio", "Homerton 2", etc.

### Step 6: Wait for Setup

The integration will:
1. Test connection to your radio ✓
2. Fetch device information ✓
3. Discover all available modes ✓
4. Load your presets ✓
5. Create all entities ✓

You should see: **"Success! Device configured."**

### Step 7: Verify Entities

Go to **Settings** → **Devices & Services** → **My Frontier Silicon**

You should see entities like:
- `media_player.your_radio_name` - Main control
- `select.your_radio_name_radio_preset` - Preset selector
- `sensor.your_radio_name_current_mode` - Mode display
- `sensor.your_radio_name_current_station` - Station info
- `button.your_radio_name_refresh_presets` - Refresh button

## Method 2: Manual Installation

### Step 1: Download

1. Download the latest release from GitHub
2. Extract the ZIP file

### Step 2: Copy Files

Copy the `custom_components/my_frontier_silicon` folder to your Home Assistant installation:

**Docker:**
```bash
# From extracted folder
scp -r custom_components/my_frontier_silicon user@homeassistant:/config/custom_components/
```

**Home Assistant OS:**
1. Use **File Editor** add-on or **Samba share**
2. Navigate to `/config/custom_components/`
3. Create folder: `my_frontier_silicon`
4. Copy all files into this folder

**Supervised:**
```bash
sudo cp -r custom_components/my_frontier_silicon /usr/share/hassio/homeassistant/custom_components/
```

### Step 3: Verify Structure

Your folder structure should be:
```
/config/
└── custom_components/
    └── my_frontier_silicon/
        ├── __init__.py
        ├── api.py
        ├── button.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── manifest.json
        ├── media_player.py
        ├── select.py
        ├── sensor.py
        ├── strings.json
        └── translations/
            └── en.json
```

### Step 4: Restart and Configure

Follow **Steps 3-7** from Method 1 above.

## Finding Your Radio's IP Address

### Method 1: Router

1. Log into your router admin page
2. Look for **Connected Devices** or **DHCP Clients**
3. Find your radio by name:
   - "Frontier Silicon"
   - "Homerton"
   - "Roberts"
   - Or your radio's model name
4. Note the IP address

### Method 2: Radio Display

**Most radios:**
1. Menu → Settings → Network → Network Settings
2. Look for "IP Address" or "WLAN"

**Homerton 2:**
1. Press and hold **Info** button
2. Scroll to network information
3. IP address shown on display

### Method 3: Network Scanner

**Using Fing (Phone App):**
1. Download "Fing" app
2. Scan network
3. Look for "Frontier Silicon" device

**Using nmap (Linux/Mac):**
```bash
sudo nmap -sn 192.168.1.0/24 | grep -B2 Frontier
```

**Using Advanced IP Scanner (Windows):**
1. Download and run Advanced IP Scanner
2. Scan your network range
3. Look for your radio's name

## Setting a Static IP (Highly Recommended)

To prevent your radio's IP from changing:

### Option 1: Router DHCP Reservation

1. Log into router
2. Find **DHCP Reservation** or **Static IP**
3. Find your radio's MAC address
4. Reserve its current IP address
5. Save settings

### Option 2: Radio Network Settings

Some radios allow manual IP configuration:
1. Menu → Settings → Network
2. Change from DHCP to Manual/Static
3. Enter desired IP, subnet mask, gateway
4. Save

## Troubleshooting Installation

### "Cannot Connect" Error

**Check 1: IP Address**
```bash
ping 10.8.11.30
# Replace with your radio's IP
```

**Check 2: Radio is On**
- Radio must be fully on, not in standby
- Display should be lit

**Check 3: Same Network**
- Home Assistant and radio must be on same network
- Check router settings if you have multiple networks

**Check 4: Firewall**
- Ensure port 80 is not blocked
- Temporarily disable firewall to test

### "Already Configured" Error

The integration uses IP address as unique identifier:
- Remove old entry: Settings → Devices & Services → Find device → Delete
- Reconfigure with new details

### Integration Not Showing in HACS

**Wait for HACS to Update:**
- HACS updates repository list every few hours
- Manually refresh: HACS → Integrations → ⋮ → Reload

**Check Repository URL:**
- Must be exact
- No trailing slash
- HTTPS, not HTTP

### No Entities Created

**Check Logs:**
1. Settings → System → Logs
2. Search for "frontier_silicon"
3. Look for error messages

**Common Issues:**
- Wrong PIN code
- Radio in standby mode
- Network connectivity problems

### Presets Not Loading

**Try this:**
1. Switch radio to Internet Radio mode
2. Go to HA: Settings → Devices → Your Radio
3. Click the **Refresh Presets** button
4. Wait 30 seconds
5. Refresh page

## Upgrading

### Via HACS

1. HACS → Integrations
2. Find "My Frontier Silicon"
3. Click **Update**
4. Restart Home Assistant

### Manual Update

1. Download new version
2. Replace all files in `custom_components/my_frontier_silicon/`
3. Restart Home Assistant

**Note:** Your configuration is preserved - no need to reconfigure!

## Multiple Radios

You can add multiple radios:

1. Repeat installation for each radio
2. Each needs unique IP address
3. Each gets its own set of entities
4. Can be in different rooms/areas

Example entities:
- `media_player.living_room_radio`
- `media_player.bedroom_radio`
- `media_player.kitchen_radio`

## Post-Installation Setup

### Assign to Areas

1. Settings → Devices & Services
2. Find your radio
3. Click on it
4. Click **No Area** → Select area
5. All entities now show in that area

### Add to Dashboard

**Quick Add:**
1. Edit dashboard
2. Click **+ ADD CARD**
3. Search "media"
4. Select **Media Control**
5. Choose your radio
6. Save

**Custom Card:**
See README.md for advanced dashboard examples

### Create Automations

See README.md for automation examples

## Uninstalling

### Remove Integration

1. Settings → Devices & Services
2. Find "My Frontier Silicon"
3. Click on your device
4. Click **⋮** (three dots)
5. Select **Delete**

### Remove via HACS

1. HACS → Integrations
2. Find "My Frontier Silicon"
3. Click **⋮** (three dots)
4. Select **Remove**
5. Restart Home Assistant

### Remove Manual Installation

Delete folder:
```bash
rm -rf /config/custom_components/my_frontier_silicon
```

Then restart Home Assistant.

## Getting Help

**Before asking for help, collect this info:**

1. Home Assistant version:
   - Settings → About → Version

2. Integration version:
   - HACS → Integrations → My Frontier Silicon

3. Radio model and firmware:
   - Check radio's About/Info menu

4. Error logs:
   - Settings → System → Logs
   - Search for "frontier_silicon"

5. What you tried:
   - List all troubleshooting steps

**Where to ask:**
- GitHub Issues: Bug reports and feature requests
- Home Assistant Community: General questions
- HACS Discord: Installation problems

## Next Steps

✅ **Installation complete!**

Now you can:
1. 📱 Add radio to your dashboard
2. 🤖 Create automations
3. 🎵 Set up favorite station shortcuts
4. ⚙️ Customize entity names and icons
5. 📢 Share your setup with friends!

See **README.md** for usage examples and automation ideas.

---

**Happy listening! 📻✨**
