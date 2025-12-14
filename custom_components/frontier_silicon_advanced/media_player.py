"""Media player platform for My Frontier Silicon."""
import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    PLAY_STATUS_PLAYING,
    PLAY_STATUS_PAUSED,
    PLAY_STATUS_STOPPED,
    PLAY_STATUS_BUFFERING,
)
from .coordinator import FrontierSiliconCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Frontier Silicon media player."""
    coordinator: FrontierSiliconCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FrontierSiliconMediaPlayer(coordinator, entry)])


class FrontierSiliconMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Representation of a Frontier Silicon device."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the media player."""
        super().__init__(coordinator)
        self._attr_unique_id = entry.entry_id
        
        # Get device info
        device_name = entry.title
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Frontier Silicon",
            model="Internet Radio",
        )

        # Supported features
        self._attr_supported_features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("available", False)

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        if not self.coordinator.data.get("power"):
            return MediaPlayerState.OFF
        
        play_status = self.coordinator.data.get("play_status")
        
        if play_status == PLAY_STATUS_PLAYING:
            return MediaPlayerState.PLAYING
        elif play_status == PLAY_STATUS_PAUSED:
            return MediaPlayerState.PAUSED
        elif play_status == PLAY_STATUS_BUFFERING:
            return MediaPlayerState.BUFFERING
        elif play_status == PLAY_STATUS_STOPPED:
            return MediaPlayerState.IDLE
        
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        volume = self.coordinator.data.get("volume", 0)
        volume_steps = self.coordinator.data.get("volume_steps", 32)
        
        if volume_steps > 0:
            return volume / volume_steps
        return 0.0

    @property
    def is_volume_muted(self) -> bool:
        """Boolean if volume is currently muted."""
        return self.coordinator.data.get("mute", False)

    @property
    def media_title(self) -> str | None:
        """Title of current playing media."""
        return self.coordinator.data.get("station_name")

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media."""
        # Use station_text if no artist available
        artist = self.coordinator.data.get("artist")
        if artist:
            return artist
        return self.coordinator.data.get("station_text")

    @property
    def media_album_name(self) -> str | None:
        """Album name of current playing media."""
        return self.coordinator.data.get("album")

    @property
    def media_image_url(self) -> str | None:
        """Image url of current playing media."""
        return self.coordinator.data.get("graphic_uri")

    @property
    def source(self) -> str | None:
        """Name of the current input source."""
        mode_id = self.coordinator.data.get("mode")
        if mode_id is None:
            return None
        
        # Get mode name from cached modes
        if hasattr(self.coordinator, "_modes"):
            for mode in self.coordinator._modes:
                if mode.get("key") == mode_id:
                    return mode.get("label") or mode.get("name")
        
        return f"Mode {mode_id}"

    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        if not hasattr(self.coordinator, "_modes"):
            return None
        
        return [
            mode.get("label") or mode.get("name") or f"Mode {mode.get('key')}"
            for mode in self.coordinator._modes
        ]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = {}
        
        # Add current mode ID
        if mode_id := self.coordinator.data.get("mode"):
            attrs["mode_id"] = mode_id
        
        # Add station text
        if station_text := self.coordinator.data.get("station_text"):
            attrs["station_text"] = station_text
        
        return attrs

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self.coordinator.api.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self.coordinator.api.power_off()
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volume_steps = self.coordinator.data.get("volume_steps", 32)
        target_volume = int(volume * volume_steps)
        
        await self.coordinator.api.set_volume(target_volume)
        await self.coordinator.async_request_refresh()

    async def async_volume_up(self) -> None:
        """Volume up the media player."""
        current_volume = self.coordinator.data.get("volume", 0)
        volume_steps = self.coordinator.data.get("volume_steps", 32)
        
        if current_volume < volume_steps:
            await self.coordinator.api.set_volume(current_volume + 1)
            await self.coordinator.async_request_refresh()

    async def async_volume_down(self) -> None:
        """Volume down the media player."""
        current_volume = self.coordinator.data.get("volume", 0)
        
        if current_volume > 0:
            await self.coordinator.api.set_volume(current_volume - 1)
            await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        if mute:
            await self.coordinator.api.mute()
        else:
            await self.coordinator.api.unmute()
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        # Find mode ID from name
        if hasattr(self.coordinator, "_modes"):
            for mode in self.coordinator._modes:
                mode_name = mode.get("label") or mode.get("name")
                if mode_name == source:
                    mode_id = mode.get("key")
                    await self.coordinator.api.set_mode(mode_id)
                    await self.coordinator.async_request_refresh()
                    return
        
        _LOGGER.error("Source %s not found", source)

    async def async_media_play(self) -> None:
        """Send play command."""
        await self.coordinator.api.play()
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.coordinator.api.pause()
        await self.coordinator.async_request_refresh()

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self.coordinator.api.stop()
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.coordinator.api.next_track()
        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self.coordinator.api.previous_track()
        await self.coordinator.async_request_refresh()
