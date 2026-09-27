"""Data coordinator for My Frontier Silicon integration - FIXED VERSION."""
import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FrontierSiliconAPI
from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    CONF_PIN,
    DEFAULT_PORT,
    DEFAULT_PIN,
    PRESET_MODE_IDS,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_OFF_DATA: dict[str, Any] = {
    "power": False,
    "available": True,
    "volume": 0,
    "volume_steps": 32,
    "mute": False,
    "mode": None,
    "play_status": None,
    "station_name": None,
    "station_text": None,
    "artist": None,
    "album": None,
    "graphic_uri": None,
    "sleep_timer": 0,
    "eq_preset": None,
    "wifi_rssi": None,
    "wifi_ssid": None,
    "ip_address": None,
    "mac_address": None,
}


class FrontierSiliconCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Frontier Silicon device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.api = FrontierSiliconAPI(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            pin=entry.data.get(CONF_PIN, DEFAULT_PIN),
        )
        self._device_info: dict[str, Any] = {}
        self._modes: list[dict[str, str]] = []
        self._all_presets: dict[str, list[dict[str, str]]] = {}
        self._presets: list[dict[str, str]] = []
        self._preset_lock = asyncio.Lock()
        # Auto-load is attempted once per power-on cycle
        self._auto_load_attempted = False
        
        # Get options with defaults
        self._debug_logging = entry.options.get("debug_logging", False)
        self._auto_load_presets = entry.options.get("auto_load_presets", True)
        scan_interval_off = entry.options.get("scan_interval_off", 60)
        scan_interval_on = entry.options.get("scan_interval_on", 15)
        
        # Use appropriate scan interval based on power state
        # Will be updated dynamically
        self._scan_interval_off = scan_interval_off
        self._scan_interval_on = scan_interval_on

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval_off),  # Start with OFF interval
        )

    def _log_debug(self, msg: str, *args) -> None:
        """Log debug message if debug logging is enabled."""
        if self._debug_logging:
            _LOGGER.info(f"[DEBUG] {msg}", *args)
        else:
            _LOGGER.debug(msg, *args)

    def _log_info(self, msg: str, *args) -> None:
        """Log info message (always shown)."""
        _LOGGER.info(msg, *args)

    def _radio_is_known_on(self) -> bool:
        """Return True only when the latest coordinator data says power is ON."""
        return bool(self.data and self.data.get("power") is True)

    def _update_scan_interval(self, radio_on: bool) -> None:
        """Update scan interval based on current power state.
        
        Args:
            radio_on: Current radio power state (from probe, not self.data)
        """
        if radio_on:
            new_interval = timedelta(seconds=self._scan_interval_on)
        else:
            new_interval = timedelta(seconds=self._scan_interval_off)
        
        if self.update_interval != new_interval:
            self._log_info("Scan interval changed to %s seconds", new_interval.total_seconds())
            self.update_interval = new_interval

    async def _probe_power(self, *, context: str, allow_session_create: bool) -> tuple[bool, str]:
        """Probe radio power state with explicit logging."""
        self._log_info(
            "Power probe: context=%s allow_session_create=%s session_exists=%s",
            context,
            allow_session_create,
            bool(self.api.session_id),
        )
        power, status = await self.api.get_value(
            "netRemote.sys.power",
            allow_session_create=allow_session_create,
            context=context,
        )
        self._log_info("Power probe result: context=%s power=%s status=%s", context, power, status)
        return power == "1", status

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            radio_on, status = await self._probe_power(
                context="periodic_update_power_check",
                allow_session_create=True,
            )

            if not radio_on:
                self._log_info("Radio is OFF/unknown; skipping detailed data and clearing session")
                await self.api.clear_session(context="periodic_update_power_off_or_unknown")
                self._update_scan_interval(radio_on)  # Use current state, not old self.data
                return DEFAULT_OFF_DATA.copy()

            self._log_info("Radio is ON; fetching detailed playback/status data")
            self._update_scan_interval(radio_on)  # Use current state, not old self.data
            
            data = DEFAULT_OFF_DATA.copy()
            data.update({"power": True, "available": True})

            volume, _ = await self.api.get_value("netRemote.sys.audio.volume", context="details:volume")
            mute, _ = await self.api.get_value("netRemote.sys.audio.mute", context="details:mute")
            mode, _ = await self.api.get_value("netRemote.sys.mode", context="details:mode")
            play_status, _ = await self.api.get_value("netRemote.play.status", context="details:play_status")
            station_name, _ = await self.api.get_value("netRemote.play.info.name", context="details:station_name")
            station_text, _ = await self.api.get_value("netRemote.play.info.text", context="details:station_text")
            artist, _ = await self.api.get_value("netRemote.play.info.artist", context="details:artist")
            album, _ = await self.api.get_value("netRemote.play.info.album", context="details:album")
            graphic_uri, _ = await self.api.get_value("netRemote.play.info.graphicUri", context="details:graphic_uri")
            volume_steps, _ = await self.api.get_value("netRemote.sys.caps.volumeSteps", context="details:volume_steps")
            sleep_timer, _ = await self.api.get_value("netRemote.sys.sleep", context="details:sleep_timer")
            eq_preset, _ = await self.api.get_value("netRemote.sys.audio.eqPreset", context="details:eq_preset")
            wifi_rssi, _ = await self.api.get_value("netRemote.sys.net.wlan.rssi", context="details:wifi_rssi")
            wifi_ssid, _ = await self.api.get_value("netRemote.sys.net.wlan.connectedSSID", context="details:wifi_ssid")
            ip_address, _ = await self.api.get_value("netRemote.sys.net.ipConfig.address", context="details:ip_address")
            mac_address, _ = await self.api.get_value("netRemote.sys.net.wlan.macAddress", context="details:mac_address")

            data.update({
                "volume": int(volume) if volume else 0,
                "volume_steps": int(volume_steps) if volume_steps else 32,
                "mute": mute == "1",
                "mode": mode,
                "play_status": play_status,
                "station_name": station_name,
                "station_text": station_text,
                "artist": artist,
                "album": album,
                "graphic_uri": graphic_uri,
                "sleep_timer": int(sleep_timer) if sleep_timer else 0,
                "eq_preset": eq_preset,
                "wifi_rssi": wifi_rssi,
                "wifi_ssid": wifi_ssid,
                "ip_address": ip_address,
                "mac_address": mac_address,
            })

            if self._device_info:
                data.update(self._device_info)

            return data

        except Exception as err:
            _LOGGER.warning("Error communicating with device: %s", err)
            await self.api.clear_session(context="update_exception")
            data = DEFAULT_OFF_DATA.copy()
            data["available"] = False
            return data

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        await self.api.close()

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh and load initial data safely."""
        self._log_info(
            "Frontier Silicon: Safe mode active - presets load only when power confirmed ON"
        )

        self._device_info = {}
        self._modes = []
        self._all_presets = {}
        self._presets = []

        radio_on, _ = await self._probe_power(
            context="startup_power_check",
            allow_session_create=True,
        )

        if radio_on:
            self._log_info("Startup: radio is ON. Loading device info and modes")
            try:
                firmware_version, _ = await self.api.get_value("netRemote.sys.info.version", context="startup:firmware_version")
                device_model, _ = await self.api.get_value("netRemote.sys.info.friendlyName", context="startup:friendly_name")
                self._device_info = {
                    "firmware_version": firmware_version,
                    "device_model": device_model,
                }
                self._log_info("Startup device info: model=%s firmware=%s", device_model, firmware_version)
            except Exception as err:
                _LOGGER.warning("Error loading startup device info: %s", err)
                self._device_info = {}

            try:
                self._modes = await self.api.get_modes()
                self._log_info("Startup: loaded %d modes", len(self._modes))
            except Exception as err:
                _LOGGER.warning("Startup: error loading modes: %s", err)
                self._modes = []
        else:
            self._log_info("Startup: radio is OFF/unknown. No modes, presets or device details will be loaded")
            await self.api.clear_session(context="startup_radio_off")

        await super().async_config_entry_first_refresh()

        # Listeners run after self.data is updated, so the power state seen
        # there is the freshly polled one.
        self.entry.async_on_unload(
            self.async_add_listener(self._async_check_auto_load)
        )
        # Radio may already be ON at startup
        self._async_check_auto_load()

    @callback
    def _async_check_auto_load(self) -> None:
        """Load modes and presets once a poll confirms the radio is ON."""
        if not self._radio_is_known_on():
            self._auto_load_attempted = False
            return
        needs_modes = not self._modes
        needs_presets = self._auto_load_presets and not self._all_presets
        if self._auto_load_attempted or not (needs_modes or needs_presets):
            return
        self._auto_load_attempted = True
        self.entry.async_create_background_task(
            self.hass,
            self._async_auto_load(needs_presets),
            "frontier_silicon_auto_load",
        )

    async def _async_auto_load(self, load_presets: bool) -> None:
        """Load modes (and presets when enabled), then notify entities."""
        if not self._modes:
            self._log_info("Radio confirmed ON; loading modes")
            try:
                self._modes = await self.api.get_modes()
            except Exception as err:
                _LOGGER.warning("Error loading modes: %s", err)
        if load_presets:
            self._log_info("Radio confirmed ON; auto-loading presets")
            await self._async_load_all_presets()
        self.async_update_listeners()

    def _preset_mode_keys(self) -> list[str]:
        """Return keys of the modes that support presets on this device.

        Mode keys differ between devices (DAB is "3" on some radios and "2" on
        others), so match on the mode id or label reported by validModes.
        """
        if not self._modes:
            # Modes unknown; fall back to the most common layout
            return ["0", "3", "4"]

        keys = []
        for mode in self._modes:
            key = mode.get("key")
            if key is None or mode.get("selectable") == "0":
                continue
            mode_id = (mode.get("id") or "").upper()
            label = (mode.get("label") or "").lower()
            if (
                mode_id in PRESET_MODE_IDS
                or "internet radio" in label
                or "dab" in label
                or label == "fm"
            ):
                keys.append(key)
        return keys

    async def _load_presets_for_mode(self, mode_id: str, switch_mode: bool = True) -> list[dict[str, str]]:
        """Load presets for a specific mode.

        The caller is responsible for restoring the original mode afterwards.
        """
        try:
            if switch_mode:
                await self.api.set_mode(mode_id)
                await asyncio.sleep(0.5)
            # get_presets() handles nav.state internally
            presets = await self.api.get_presets()
            self._log_info("Loaded %d presets for mode %s", len(presets), mode_id)
            return presets
        except Exception as err:
            _LOGGER.warning("Error loading presets for mode %s: %s", mode_id, err)
            return []

    async def _async_load_all_presets(self) -> dict[str, list[dict[str, str]]]:
        """Load presets for all preset-capable modes, then restore the mode.

        Presets are read from the current mode first (no switch needed); the
        original mode is restored once at the end.
        """
        async with self._preset_lock:
            if not self._radio_is_known_on():
                _LOGGER.warning("Refusing to load presets: radio is not confirmed ON")
                return self._all_presets

            if not self._modes:
                try:
                    self._modes = await self.api.get_modes()
                except Exception as err:
                    _LOGGER.warning("Error loading modes before presets: %s", err)

            current_mode = self.data.get("mode")
            mode_keys = self._preset_mode_keys()
            if current_mode in mode_keys:
                mode_keys.remove(current_mode)
                mode_keys.insert(0, current_mode)

            self._log_info(
                "Loading presets for modes %s (will restore mode %s after)",
                mode_keys,
                current_mode,
            )
            all_presets: dict[str, list[dict[str, str]]] = {}
            switched = False
            try:
                for mode_id in mode_keys:
                    switch_mode = mode_id != current_mode
                    switched |= switch_mode
                    presets = await self._load_presets_for_mode(mode_id, switch_mode=switch_mode)
                    if presets:
                        all_presets[mode_id] = presets
            finally:
                if switched and current_mode:
                    self._log_info("Restoring original mode %s after preset load", current_mode)
                    try:
                        await self.api.set_mode(current_mode)
                    except Exception as err:
                        _LOGGER.warning("Failed to restore mode %s: %s", current_mode, err)

            self._all_presets = all_presets
            return self._all_presets

    async def get_all_presets(self) -> dict[str, list[dict[str, str]]]:
        """Get all presets for all modes, guarded by current power state."""
        if self._all_presets:
            self._log_debug("Returning cached all-presets (%d modes)", len(self._all_presets))
            return self._all_presets

        if not self._radio_is_known_on():
            self._log_info(
                "Preset auto-load skipped: radio is OFF/not confirmed ON"
            )
            return self._all_presets

        if not self._auto_load_presets:
            self._log_info("Preset auto-load disabled by config option")
            return self._all_presets

        self._log_info("All presets not cached. Radio confirmed ON, loading presets on demand")
        return await self._async_load_all_presets()

    async def refresh_all_presets(self) -> None:
        """Reload presets for all modes, ignoring the cache."""
        if not self._radio_is_known_on():
            _LOGGER.warning("Manual preset refresh ignored: radio is OFF/not confirmed ON")
            return
        await self._async_load_all_presets()
        self.async_update_listeners()

    async def get_modes(self) -> list[dict[str, str]]:
        """Get available modes, guarded by current power state."""
        if self._modes:
            return self._modes
        if not self._radio_is_known_on():
            self._log_info("Mode load skipped: radio is OFF/not confirmed ON")
            return self._modes
        self._log_debug("Modes not cached, fetching from device")
        self._modes = await self.api.get_modes()
        return self._modes

    async def get_presets(self) -> list[dict[str, str]]:
        """Get presets for current mode, guarded by current power state."""
        if self._presets:
            return self._presets
        if not self._radio_is_known_on():
            self._log_info("Preset load skipped: radio is OFF/not confirmed ON")
            return self._presets
        self._log_debug("Presets not cached, fetching from device")
        self._presets = await self.api.get_presets()
        return self._presets

    async def refresh_presets(self) -> None:
        """Force refresh of presets, but only when radio is confirmed ON."""
        if not self._radio_is_known_on():
            _LOGGER.warning("Manual preset refresh ignored: radio is OFF/not confirmed ON")
            return
        self._log_info("Refreshing presets from device")
        self._presets = await self.api.get_presets()
        self._log_info("Loaded %d presets", len(self._presets))
        await self.async_request_refresh()

    async def refresh_modes(self) -> None:
        """Force refresh of modes, but only when radio is confirmed ON."""
        if not self._radio_is_known_on():
            _LOGGER.warning("Manual mode refresh ignored: radio is OFF/not confirmed ON")
            return
        self._log_info("Refreshing modes from device")
        self._modes = await self.api.get_modes()
        await self.async_request_refresh()

    async def force_power_probe(self) -> None:
        """Manual helper for testing power detection from Home Assistant button."""
        _LOGGER.warning("Manual force power probe requested")
        await self.async_request_refresh()
