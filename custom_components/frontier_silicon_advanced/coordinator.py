"""Data coordinator for My Frontier Silicon integration."""
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
            power, _ = await self.api.get_value("netRemote.sys.power")
            
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
                })
            
            return data
            
        except Exception as err:
            _LOGGER.error("Error communicating with device: %s", err)
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        await self.api.close()

    async def get_modes(self) -> list[dict[str, str]]:
        """Get available modes (cached)."""
        if not hasattr(self, "_modes"):
            self._modes = await self.api.get_modes()
        return self._modes

    async def get_presets(self) -> list[dict[str, str]]:
        """Get presets (cached)."""
        if not hasattr(self, "_presets"):
            self._presets = await self.api.get_presets()
        return self._presets

    async def refresh_presets(self) -> None:
        """Force refresh of presets."""
        self._presets = await self.api.get_presets()

    async def refresh_modes(self) -> None:
        """Force refresh of modes."""
        self._modes = await self.api.get_modes()
