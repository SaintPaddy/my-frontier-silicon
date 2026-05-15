# Logging Configuration Guide

## 🎯 Two Ways to Control Logging

### Method 1: configuration.yaml (Old Way)

**Edit `/config/configuration.yaml`:**

```yaml
logger:
  default: warning
  logs:
    custom_components.my_frontier_silicon: debug
```

**Then restart Home Assistant**

**Pros:**
- ✅ Global logging control
- ✅ Can set different levels (debug, info, warning, error)

**Cons:**
- ❌ Requires HA restart to change
- ❌ Need to edit YAML file
- ❌ All-or-nothing (debug = very verbose!)

---

### Method 2: Options Flow (New Way) ⭐ RECOMMENDED

**Settings → Integrations → Configure:**

```
☑️ Enable debug logging
```

**No restart needed!**

**Pros:**
- ✅ Change via UI (no YAML editing)
- ✅ No HA restart needed
- ✅ Per-integration control
- ✅ Easy to toggle on/off

**Cons:**
- Only two modes (normal/debug)

---

## 🔍 How They Work Together

### If BOTH are set:

**configuration.yaml:**
```yaml
logger:
  logs:
    custom_components.my_frontier_silicon: debug
```

**Options:**
```
Debug logging: OFF
```

**Result:** 
- configuration.yaml wins → DEBUG level logging
- But our code uses `_log_debug()` which respects the option
- Some messages still hidden

**Recommendation:** Pick ONE method!

---

### Best Practice:

**For normal use:**
```yaml
# configuration.yaml - keep minimal
logger:
  default: warning
  # Don't set my_frontier_silicon here
```

```
# Options - use this instead
Debug logging: OFF
```

**For troubleshooting:**
```
# Options - toggle via UI
Debug logging: ON
```

**For deep debugging:**
```yaml
# configuration.yaml - only if needed
logger:
  logs:
    custom_components.my_frontier_silicon: debug
    custom_components.my_frontier_silicon.api: debug
    custom_components.my_frontier_silicon.coordinator: debug
```

---

## 📊 Logging Levels Explained

### What You See at Each Level:

**ERROR (always shown):**
```
ERROR: Failed to connect to device
ERROR: API request failed
```

**WARNING (default, always shown):**
```
WARNING: CREATE_SESSION requested
WARNING: Manual preset refresh ignored
WARNING: SET mode=3
```

**INFO (configuration.yaml: info):**
```
INFO: Power probe result: power=0
INFO: Radio is OFF; skipping queries
INFO: Loaded 10 presets
```

**DEBUG (configuration.yaml: debug OR Option: ON):**
```
DEBUG: Returning cached presets
DEBUG: Finished fetching data in 0.1s
DEBUG: Session exists: false
```

---

## 🎯 Our Smart Logging System

### Normal Mode (debug_logging: false):

```python
_log_info("Power probe result: %s", power)  # → INFO (shown)
_log_debug("Using cached presets")           # → DEBUG (hidden)
```

**Logs:**
```
INFO: Power probe result: 0
INFO: Radio is OFF
[no debug messages]
```

---

### Debug Mode (debug_logging: true):

```python
_log_info("Power probe result: %s", power)  # → INFO (shown)
_log_debug("Using cached presets")           # → INFO [DEBUG] (shown!)
```

**Logs:**
```
INFO: Power probe result: 0
INFO: Radio is OFF
INFO: [DEBUG] Using cached presets
INFO: [DEBUG] Finished fetching in 0.1s
```

**Notice:** Debug messages shown as INFO with `[DEBUG]` prefix!

---

## 💡 Recommended Setup

### For Most Users:

**configuration.yaml:**
```yaml
# Don't add my_frontier_silicon logging config
```

**Options:**
```
Debug logging: OFF
```

**Result:** Clean logs, important events only

---

### When You Have Issues:

**Step 1 - Enable debug via UI:**
```
Settings → Integrations → Configure
☑️ Enable debug logging
```

**Step 2 - Reproduce issue:**
- Restart HA
- Turn radio on/off
- Try preset loading

**Step 3 - Check logs:**
```
Settings → System → Logs
Search: "frontier_silicon"
```

**Step 4 - Disable debug when done:**
```
Settings → Integrations → Configure
☐ Enable debug logging
```

**No HA restart needed!**

---

### For GitHub Issues:

**When reporting bugs, enable BOTH:**

**configuration.yaml:**
```yaml
logger:
  default: info
  logs:
    custom_components.my_frontier_silicon: debug
```

**Options:**
```
Debug logging: ON
```

**Then:**
1. Restart HA
2. Reproduce issue
3. Copy logs
4. Include in GitHub issue

---

## 🔧 Advanced: Module-Specific Logging

**If you want to debug only specific parts:**

```yaml
logger:
  default: warning
  logs:
    # Only API calls
    custom_components.my_frontier_silicon.api: debug
    
    # Only coordinator
    custom_components.my_frontier_silicon.coordinator: debug
    
    # Only config flow
    custom_components.my_frontier_silicon.config_flow: debug
    
    # Everything else: INFO
    custom_components.my_frontier_silicon: info
```

**Useful for:**
- Tracking API call issues (api.py)
- Debugging power state (coordinator.py)
- Fixing setup problems (config_flow.py)

---

## 📋 Quick Reference

| Scenario | configuration.yaml | Options | Result |
|----------|-------------------|---------|--------|
| **Normal use** | (none) | Debug: OFF | Clean logs ✅ |
| **Quick debug** | (none) | Debug: ON | Verbose, no restart ✅ |
| **Deep debug** | debug level | Debug: ON | Maximum verbosity 🔍 |
| **Bug report** | debug level | Debug: ON | Full logs for GitHub 📋 |

---

## ✅ Summary

**Old way (configuration.yaml):**
- Edit YAML
- Restart HA
- All-or-nothing

**New way (Options):**
- Click checkbox
- No restart
- Easy toggle

**Best practice:**
- Use Options for normal debugging ⭐
- Use configuration.yaml only for deep issues
- Don't use both simultaneously

---

**Pro tip:** The `[DEBUG]` prefix in logs helps you see which messages came from our smart logging system vs standard Python logging!

