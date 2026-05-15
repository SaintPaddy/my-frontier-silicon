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
        FrontierSiliconWiFiSignalSensor(coordinator, entry),
        FrontierSiliconIPAddressSensor(coordinator, entry),
        FrontierSiliconMACAddressSensor(coordinator, entry),
        FrontierSiliconSSIDSensor(coordinator, entry),
        FrontierSiliconSleepRemainingSensor(coordinator, entry),
        FrontierSiliconFirmwareVersionSensor(coordinator, entry),
        FrontierSiliconDeviceModelSensor(coordinator, entry),
        FrontierSiliconVolumePercentSensor(coordinator, entry),
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


class FrontierSiliconWiFiSignalSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing WiFi signal strength."""

    _attr_has_entity_name = True
    _attr_translation_key = "wifi_signal"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_wifi_signal"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> int | None:
        """Return the WiFi signal strength."""
        rssi = self.coordinator.data.get("wifi_rssi")
        if rssi:
            try:
                rssi_int = int(rssi)
                
                # Skip if 0 (invalid/not available)
                if rssi_int == 0:
                    return None
                
                # Convert from unsigned to signed if value > 127
                # (Some APIs return RSSI as unsigned 8-bit: 0-255)
                if rssi_int > 127:
                    rssi_int = rssi_int - 256
                
                # Sanity check: RSSI should be negative
                if rssi_int > 0:
                    rssi_int = -rssi_int
                
                return rssi_int
            except (ValueError, TypeError):
                pass
        return None

    @property
    def icon(self) -> str:
        """Return the icon based on signal strength."""
        if self.native_value:
            if self.native_value >= -50:
                return "mdi:wifi-strength-4"
            elif self.native_value >= -60:
                return "mdi:wifi-strength-3"
            elif self.native_value >= -70:
                return "mdi:wifi-strength-2"
            else:
                return "mdi:wifi-strength-1"
        return "mdi:wifi-strength-outline"


class FrontierSiliconIPAddressSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing IP address."""

    _attr_has_entity_name = True
    _attr_translation_key = "ip_address"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_ip_address"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the IP address."""
        ip_int = self.coordinator.data.get("ip_address")
        if ip_int:
            try:
                # Convert integer to IP address (e.g., 168299294 -> 10.8.11.30)
                ip_num = int(ip_int)
                return f"{(ip_num >> 24) & 0xFF}.{(ip_num >> 16) & 0xFF}.{(ip_num >> 8) & 0xFF}.{ip_num & 0xFF}"
            except (ValueError, TypeError):
                pass
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:ip-network"


class FrontierSiliconMACAddressSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing MAC address."""

    _attr_has_entity_name = True
    _attr_translation_key = "mac_address"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_mac_address"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the MAC address."""
        return self.coordinator.data.get("mac_address")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:network"


class FrontierSiliconSSIDSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing connected WiFi SSID."""

    _attr_has_entity_name = True
    _attr_translation_key = "wifi_ssid"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_wifi_ssid"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the WiFi SSID."""
        return self.coordinator.data.get("wifi_ssid")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:wifi"


class FrontierSiliconSleepRemainingSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing remaining sleep time."""

    _attr_has_entity_name = True
    _attr_translation_key = "sleep_remaining"
    _attr_native_unit_of_measurement = "min"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sleep_remaining"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> int | None:
        """Return the remaining sleep time in minutes."""
        sleep_seconds = self.coordinator.data.get("sleep_timer")
        if sleep_seconds:
            try:
                seconds = int(sleep_seconds)
                if seconds > 0:
                    minutes = round(seconds / 60.0)
                    return minutes
            except (ValueError, TypeError):
                pass
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        if self.native_value and self.native_value > 0:
            return "mdi:timer-sand"
        return "mdi:timer-off"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        attrs = {}
        
        sleep_seconds = self.coordinator.data.get("sleep_timer")
        if sleep_seconds:
            try:
                seconds = int(sleep_seconds)
                if seconds > 0:
                    attrs["seconds_remaining"] = seconds
                    attrs["formatted"] = f"{seconds // 60}:{seconds % 60:02d}"
            except (ValueError, TypeError):
                pass
        
        return attrs


class FrontierSiliconFirmwareVersionSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing firmware version."""

    _attr_has_entity_name = True
    _attr_translation_key = "firmware_version"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_firmware_version"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the firmware version."""
        return self.coordinator.data.get("firmware_version")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:chip"


class FrontierSiliconDeviceModelSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing device model."""

    _attr_has_entity_name = True
    _attr_translation_key = "device_model"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_device_model"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the device model."""
        return self.coordinator.data.get("device_model")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:radio"


class FrontierSiliconVolumePercentSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing volume as percentage."""

    _attr_has_entity_name = True
    _attr_translation_key = "volume_percent"
    _attr_native_unit_of_measurement = "%"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_volume_percent"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> int | None:
        """Return the volume as percentage."""
        volume = self.coordinator.data.get("volume")
        volume_steps = self.coordinator.data.get("volume_steps", 32)
        
        if volume is not None and volume_steps:
            try:
                volume_int = int(volume)
                steps_int = int(volume_steps)
                if steps_int > 0:
                    percentage = round((volume_int / steps_int) * 100)
                    return percentage
            except (ValueError, TypeError, ZeroDivisionError):
                pass
        return None

    @property
    def icon(self) -> str:
        """Return the icon based on volume level."""
        volume = self.native_value
        if volume is None or volume == 0:
            return "mdi:volume-off"
        elif volume < 33:
            return "mdi:volume-low"
        elif volume < 66:
            return "mdi:volume-medium"
        else:
            return "mdi:volume-high"
