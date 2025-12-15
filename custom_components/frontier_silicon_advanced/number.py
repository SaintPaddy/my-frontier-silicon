"""Number platform for My Frontier Silicon."""
import logging

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up Frontier Silicon number entities."""
    coordinator: FrontierSiliconCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        FrontierSiliconSleepTimer(coordinator, entry),
    ])


class FrontierSiliconSleepTimer(CoordinatorEntity, NumberEntity):
    """Number entity for sleep timer."""

    _attr_has_entity_name = True
    _attr_translation_key = "sleep_timer"
    _attr_native_min_value = 0
    _attr_native_max_value = 120
    _attr_native_step = 5
    _attr_native_unit_of_measurement = "min"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sleep_timer"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> float | None:
        """Return the current sleep timer value in minutes."""
        sleep_value = self.coordinator.data.get("sleep_timer")
        if sleep_value is not None:
            try:
                # Convert to minutes (API might be in seconds or minutes, adjust if needed)
                return float(sleep_value)
            except (ValueError, TypeError):
                pass
        return 0

    @property
    def icon(self) -> str:
        """Return the icon."""
        if self.native_value and self.native_value > 0:
            return "mdi:sleep"
        return "mdi:sleep-off"

    async def async_set_native_value(self, value: float) -> None:
        """Set the sleep timer value."""
        minutes = int(value)
        _LOGGER.info("Setting sleep timer to: %d minutes", minutes)
        
        # Set sleep timer (value in minutes)
        await self.coordinator.api.set_value("netRemote.sys.sleep", str(minutes))
        
        # Refresh coordinator
        await self.coordinator.async_request_refresh()
