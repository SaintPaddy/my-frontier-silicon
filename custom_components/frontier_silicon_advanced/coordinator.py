"""Data coordinator for My Frontier Silicon integration - FIXED VERSION."""
import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FrontierSiliconAPI
from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    CONF_PIN,
    DEFAULT_PORT,
    DEFAULT_PIN,
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

    async def _load_presets_for_mode(self, mode_id: str) -> list[dict[str, str]]:
        """Load presets for a specific mode, preserving current mode.
        
        CRITICAL: This saves and restores the current mode to avoid
        interrupting the user's listening experience!
        """
        if not self._radio_is_known_on():
            _LOGGER.warning(
                "Refusing to load presets for mode %s: radio is not confirmed ON",
                mode_id,
            )
            return []

        # CRITICAL: Save current mode before changing it!
        current_mode = self.data.get("mode")
        
        try:
            self._log_info("Loading presets for mode %s (will restore mode %s after)", mode_id, current_mode)
            
            # Switch to target mode
            await self.api.set_mode(mode_id)
            await asyncio.sleep(0.5)
            
            # Load presets (get_presets() handles nav.state internally)
            presets = await self.api.get_presets()
            
            return presets
            
        except Exception as err:
            _LOGGER.warning("Error loading presets for mode %s: %s", mode_id, err)
            return []
            
        finally:
            # CRITICAL: Always restore original mode!
            if current_mode and current_mode != mode_id:
                self._log_info("Restoring original mode %s after preset load", current_mode)
                try:
                    await self.api.set_mode(current_mode)
                    await asyncio.sleep(0.3)
                except Exception as err:
                    _LOGGER.warning("Failed to restore mode %s: %s", current_mode, err)

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
        self._all_presets = {}
        for mode in ["0", "3", "4"]:
            presets = await self._load_presets_for_mode(mode)
            if presets:
                self._all_presets[mode] = presets
        return self._all_presets

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
