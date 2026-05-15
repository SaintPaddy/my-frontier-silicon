"""Button platform for My Frontier Silicon."""
import logging

from homeassistant.components.button import ButtonEntity
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
    """Set up Frontier Silicon button entities."""
    coordinator: FrontierSiliconCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        FrontierSiliconRefreshPresetsButton(coordinator, entry),
    ])


class FrontierSiliconRefreshPresetsButton(CoordinatorEntity, ButtonEntity):
    """Button to refresh the preset list."""

    _attr_has_entity_name = True
    _attr_translation_key = "refresh_presets"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_refresh_presets"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Refreshing presets from device")
        await self.coordinator.refresh_presets()
        
        # Also refresh modes
        await self.coordinator.refresh_modes()
        
        # Trigger coordinator update
        await self.coordinator.async_request_refresh()
