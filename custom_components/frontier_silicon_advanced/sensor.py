"""Sensor platform for My Frontier Silicon."""
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
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
    """Set up Frontier Silicon sensor entities."""
    coordinator: FrontierSiliconCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        FrontierSiliconModeSensor(coordinator, entry),
        FrontierSiliconStationSensor(coordinator, entry),
    ])


class FrontierSiliconModeSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the current mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_mode"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_mode_sensor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the current mode name."""
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
    def icon(self) -> str:
        """Return the icon."""
        mode_name = self.native_value
        if mode_name:
            mode_lower = mode_name.lower()
            if "internet" in mode_lower or "radio" in mode_lower:
                return "mdi:radio"
            elif "spotify" in mode_lower:
                return "mdi:spotify"
            elif "bluetooth" in mode_lower:
                return "mdi:bluetooth"
            elif "dab" in mode_lower:
                return "mdi:radio-tower"
            elif "fm" in mode_lower:
                return "mdi:radio-fm"
            elif "cd" in mode_lower:
                return "mdi:disc"
            elif "usb" in mode_lower:
                return "mdi:usb"
            elif "aux" in mode_lower or "audio in" in mode_lower:
                return "mdi:aux"
        
        return "mdi:source"


class FrontierSiliconStationSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the current station/track info."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_station"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_station_sensor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the current station name."""
        return self.coordinator.data.get("station_name")

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional attributes."""
        attrs = {}
        
        if station_text := self.coordinator.data.get("station_text"):
            attrs["station_text"] = station_text
        
        if artist := self.coordinator.data.get("artist"):
            attrs["artist"] = artist
        
        if album := self.coordinator.data.get("album"):
            attrs["album"] = album
        
        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:music-circle"
