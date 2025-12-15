"""Data coordinator for My Frontier Silicon integration."""
import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FrontierSiliconAPI
from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    CONF_PIN,
    DEFAULT_PORT,
    DEFAULT_PIN,
)

_LOGGER = logging.getLogger(__name__)


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
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            # Get power state
            power, status = await self.api.get_value("netRemote.sys.power")
            
            # If we can't get power state, device might be unavailable
            if status in ("NO_SESSION", "XML_PARSE_ERROR"):
                _LOGGER.debug("Device appears offline or unreachable (status: %s)", status)
                return {
                    "power": False,
                    "available": False,
                }
            
            data = {
                "power": power == "1",
                "available": True,
            }
            
            # Only fetch additional data if powered on
            if data["power"]:
                # Get playback state
                volume, _ = await self.api.get_value("netRemote.sys.audio.volume")
                mute, _ = await self.api.get_value("netRemote.sys.audio.mute")
                mode, _ = await self.api.get_value("netRemote.sys.mode")
                play_status, _ = await self.api.get_value("netRemote.play.status")
                
                # Get playback info
                station_name, _ = await self.api.get_value("netRemote.play.info.name")
                station_text, _ = await self.api.get_value("netRemote.play.info.text")
                artist, _ = await self.api.get_value("netRemote.play.info.artist")
                album, _ = await self.api.get_value("netRemote.play.info.album")
                graphic_uri, _ = await self.api.get_value("netRemote.play.info.graphicUri")
                
                # Get volume steps for percentage calculation
                volume_steps, _ = await self.api.get_value("netRemote.sys.caps.volumeSteps")
                
                # Get sleep timer
                sleep_timer, _ = await self.api.get_value("netRemote.sys.sleep")
                
                # Get EQ preset
                eq_preset, _ = await self.api.get_value("netRemote.sys.audio.eqPreset")
                
                # Get WiFi info
                wifi_rssi, _ = await self.api.get_value("netRemote.sys.net.wlan.rssi")
                wifi_ssid, _ = await self.api.get_value("netRemote.sys.net.wlan.connectedSSID")
                ip_address, _ = await self.api.get_value("netRemote.sys.net.ipConfig.address")
                mac_address, _ = await self.api.get_value("netRemote.sys.net.wlan.macAddress")
                
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
            
            return data
            
        except Exception as err:
            # Only log at warning level for expected errors
            _LOGGER.warning("Error communicating with device: %s", err)
            # Return unavailable state instead of raising
            return {
                "power": False,
                "available": False,
            }

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        await self.api.close()

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh and load initial data."""
        # Load modes first
        _LOGGER.info("Loading modes on startup")
        self._modes = await self.api.get_modes()
        _LOGGER.info("Loaded %d modes", len(self._modes))
        
        # Load presets for all modes (Internet Radio, DAB+, FM)
        _LOGGER.info("Loading presets for all modes")
        self._all_presets = {}
        
        for mode in ["0", "3", "4"]:  # Internet Radio, DAB+, FM
            mode_presets = await self._load_presets_for_mode(mode)
            if mode_presets:
                self._all_presets[mode] = mode_presets
                _LOGGER.info("Loaded %d presets for mode %s", len(mode_presets), mode)
        
        # Then do normal first refresh
        await super().async_config_entry_first_refresh()
    
    async def _load_presets_for_mode(self, mode_id: str) -> list[dict[str, str]]:
        """Load presets for a specific mode."""
        try:
            # Switch to mode
            await self.api.set_mode(mode_id)
            await asyncio.sleep(0.5)
            
            # Navigate and get presets
            await self.api.set_value("netRemote.nav.state", "1")
            await asyncio.sleep(0.3)
            
            presets = await self.api.get_presets()
            return presets
        except Exception as err:
            _LOGGER.warning("Error loading presets for mode %s: %s", mode_id, err)
            return []
    
    async def get_all_presets(self) -> dict[str, list[dict[str, str]]]:
        """Get all presets for all modes."""
        if not hasattr(self, "_all_presets") or not self._all_presets:
            _LOGGER.debug("All presets not cached, loading")
            self._all_presets = {}
            for mode in ["0", "3", "4"]:
                presets = await self._load_presets_for_mode(mode)
                if presets:
                    self._all_presets[mode] = presets
        return self._all_presets

    async def get_modes(self) -> list[dict[str, str]]:
        """Get available modes (cached)."""
        if not hasattr(self, "_modes") or not self._modes:
            _LOGGER.debug("Modes not cached, fetching from device")
            self._modes = await self.api.get_modes()
        return self._modes

    async def get_presets(self) -> list[dict[str, str]]:
        """Get presets (cached)."""
        if not hasattr(self, "_presets") or not self._presets:
            _LOGGER.debug("Presets not cached, fetching from device")
            self._presets = await self.api.get_presets()
        return self._presets

    async def refresh_presets(self) -> None:
        """Force refresh of presets."""
        _LOGGER.info("Refreshing presets from device")
        self._presets = await self.api.get_presets()
        _LOGGER.info("Loaded %d presets", len(self._presets))
        # Trigger UI update
        await self.async_request_refresh()

    async def refresh_modes(self) -> None:
        """Force refresh of modes."""
        _LOGGER.info("Refreshing modes from device")
        self._modes = await self.api.get_modes()
        # Trigger UI update
        await self.async_request_refresh()
