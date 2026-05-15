"""Switch platform for My Frontier Silicon."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FrontierSiliconCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Frontier Silicon switch entities."""
    coordinator: FrontierSiliconCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        FrontierSiliconBluetoothSwitch(coordinator, entry),
        FrontierSiliconSpotifySwitch(coordinator, entry),
    ])


class FrontierSiliconBluetoothSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to quickly enable Bluetooth mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "bluetooth_mode"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_bluetooth_switch"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def is_on(self) -> bool:
        """Return true if Bluetooth mode is active."""
        current_mode = self.coordinator.data.get("mode")
        return current_mode == "5"  # Mode 5 is Bluetooth

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:bluetooth" if self.is_on else "mdi:bluetooth-off"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on Bluetooth mode."""
        _LOGGER.info("Switching to Bluetooth mode")
        await self.coordinator.api.set_mode("5")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off Bluetooth mode (switch to Internet Radio)."""
        _LOGGER.info("Switching from Bluetooth to Internet Radio")
        await self.coordinator.api.set_mode("0")
        await self.coordinator.async_request_refresh()


class FrontierSiliconSpotifySwitch(CoordinatorEntity, SwitchEntity):
    """Switch to quickly enable Spotify mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "spotify_mode"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_spotify_switch"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def is_on(self) -> bool:
        """Return true if Spotify mode is active."""
        current_mode = self.coordinator.data.get("mode")
        return current_mode == "1"  # Mode 1 is Spotify

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:spotify" if self.is_on else "mdi:spotify"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on Spotify mode."""
        _LOGGER.info("Switching to Spotify mode")
        await self.coordinator.api.set_mode("1")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off Spotify mode (switch to Internet Radio)."""
        _LOGGER.info("Switching from Spotify to Internet Radio")
        await self.coordinator.api.set_mode("0")
        await self.coordinator.async_request_refresh()
