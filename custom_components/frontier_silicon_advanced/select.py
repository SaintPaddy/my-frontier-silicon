"""Select platform for My Frontier Silicon."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
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
    """Set up Frontier Silicon select entities."""
    coordinator: FrontierSiliconCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Load presets
    await coordinator.get_presets()
    
    async_add_entities([FrontierSiliconPresetSelect(coordinator, entry)])


class FrontierSiliconPresetSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing radio presets."""

    _attr_has_entity_name = True
    _attr_translation_key = "preset"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_preset_select"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )
        self._preset_map: dict[str, str] = {}
        self._update_preset_map()

    @callback
    def _update_preset_map(self) -> None:
        """Update the preset mapping."""
        if hasattr(self.coordinator, "_presets"):
            self._preset_map = {}
            for preset in self.coordinator._presets:
                key = preset.get("key", "")
                name = preset.get("name", "").strip()
                
                # Only include named presets
                if name and name.lower() != "unnamed":
                    self._preset_map[name] = key

    @property
    def options(self) -> list[str]:
        """Return list of available presets."""
        self._update_preset_map()
        return list(self._preset_map.keys())

    @property
    def current_option(self) -> str | None:
        """Return the current preset."""
        # Try to match current station name to a preset
        current_station = self.coordinator.data.get("station_name")
        if current_station and current_station in self._preset_map:
            return current_station
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:star-circle"

    async def async_select_option(self, option: str) -> None:
        """Select a preset."""
        preset_key = self._preset_map.get(option)
        if preset_key is not None:
            # Make sure we're in Internet Radio mode
            await self.coordinator.api.set_mode("0")
            await self.coordinator.api.select_preset(preset_key)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Preset %s not found", option)

    async def async_update(self) -> None:
        """Update the entity."""
        await super().async_update()
        self._update_preset_map()
