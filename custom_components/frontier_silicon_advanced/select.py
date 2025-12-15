"""Select platform for My Frontier Silicon."""
import asyncio
import logging
import re

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FrontierSiliconCoordinator

_LOGGER = logging.getLogger(__name__)

# Mode ID to name mapping
MODE_NAMES = {
    "0": "Radio",
    "1": "Spotify",
    "2": "Music",
    "3": "DAB+",
    "4": "FM",
    "5": "Bluetooth",
    "6": "AUX",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Frontier Silicon select entities."""
    coordinator: FrontierSiliconCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Load presets and modes
    await coordinator.get_all_presets()
    await coordinator.get_modes()
    
    async_add_entities([
        FrontierSiliconMultiModePresetSelect(coordinator, entry),
        FrontierSiliconModeSelect(coordinator, entry),
        FrontierSiliconEQSelect(coordinator, entry),
    ])


class FrontierSiliconMultiModePresetSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing presets across all modes."""

    _attr_has_entity_name = True
    _attr_translation_key = "preset"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_multi_preset_select"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )
        self._preset_map: dict[str, tuple[str, str]] = {}  # {display_name: (mode_id, preset_key)}
        self._update_preset_map()

    @callback
    def _update_preset_map(self) -> None:
        """Update the preset mapping from all modes."""
        self._preset_map = {}
        
        if hasattr(self.coordinator, "_all_presets"):
            for mode_id, presets in self.coordinator._all_presets.items():
                mode_name = MODE_NAMES.get(mode_id, f"Mode {mode_id}")
                
                for preset in presets:
                    preset_key = preset.get("key", "")
                    preset_name = preset.get("name", "").strip()
                    
                    # Only include named presets (exclude empty)
                    if preset_name and preset_name.lower() not in ["unnamed", "", " "]:
                        # Format: [Radio] 1LIVE
                        display_name = f"[{mode_name}] {preset_name}"
                        self._preset_map[display_name] = (mode_id, preset_key)

    @property
    def options(self) -> list[str]:
        """Return list of available presets across all modes."""
        self._update_preset_map()
        return sorted(list(self._preset_map.keys()))

    @property
    def current_option(self) -> str | None:
        """Return the current preset."""
        current_mode = self.coordinator.data.get("mode")
        current_station = self.coordinator.data.get("station_name")
        
        if current_mode and current_station:
            mode_name = MODE_NAMES.get(current_mode, f"Mode {current_mode}")
            # Try to find matching preset
            for display_name, (mode_id, _) in self._preset_map.items():
                if mode_id == current_mode and current_station in display_name:
                    return display_name
        
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:star-circle"

    async def async_select_option(self, option: str) -> None:
        """Select a preset from any mode."""
        # Parse: "[Radio] 1LIVE" -> mode_id, preset_key
        if option not in self._preset_map:
            _LOGGER.error("Preset %s not found in map", option)
            return
        
        mode_id, preset_key = self._preset_map[option]
        
        _LOGGER.info("Selecting preset: %s (mode: %s, key: %s)", option, mode_id, preset_key)
        
        # Switch to correct mode
        await self.coordinator.api.set_mode(mode_id)
        await asyncio.sleep(0.5)
        
        # Navigate to presets
        await self.coordinator.api.set_value("netRemote.nav.state", "1")
        await asyncio.sleep(0.3)
        
        # Select preset
        await self.coordinator.api.select_preset(preset_key)
        
        # Refresh
        await self.coordinator.async_request_refresh()

    async def async_update(self) -> None:
        """Update the entity."""
        await super().async_update()
        self._update_preset_map()


class FrontierSiliconModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing input mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "mode"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_mode_select"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )
        self._mode_map: dict[str, str] = {}
        self._update_mode_map()

    @callback
    def _update_mode_map(self) -> None:
        """Update the mode mapping."""
        if hasattr(self.coordinator, "_modes"):
            self._mode_map = {}
            for mode in self.coordinator._modes:
                key = mode.get("key", "")
                name = mode.get("label") or mode.get("name", "")
                
                if name:
                    self._mode_map[name] = key

    @property
    def options(self) -> list[str]:
        """Return list of available modes."""
        self._update_mode_map()
        return list(self._mode_map.keys())

    @property
    def current_option(self) -> str | None:
        """Return the current mode."""
        mode_id = self.coordinator.data.get("mode")
        if mode_id is None:
            return None
        
        # Find mode name from ID
        for name, key in self._mode_map.items():
            if key == mode_id:
                return name
        
        return None

    @property
    def icon(self) -> str:
        """Return the icon based on current mode."""
        mode_name = self.current_option
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
            elif "usb" in mode_lower or "music" in mode_lower:
                return "mdi:usb"
            elif "aux" in mode_lower or "audio in" in mode_lower:
                return "mdi:audio-input-rca"
        
        return "mdi:import"

    async def async_select_option(self, option: str) -> None:
        """Select a mode."""
        mode_key = self._mode_map.get(option)
        if mode_key is not None:
            _LOGGER.info("Switching to mode: %s (key: %s)", option, mode_key)
            await self.coordinator.api.set_mode(mode_key)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Mode %s not found", option)

    async def async_update(self) -> None:
        """Update the entity."""
        await super().async_update()
        self._update_mode_map()


class FrontierSiliconEQSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing EQ preset."""

    _attr_has_entity_name = True
    _attr_translation_key = "equalizer"

    def __init__(
        self, coordinator: FrontierSiliconCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_eq_select"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def options(self) -> list[str]:
        """Return list of EQ presets."""
        # 6 EQ presets discovered
        return [
            "EQ Preset 0",
            "EQ Preset 1",
            "EQ Preset 2",
            "EQ Preset 3",
            "EQ Preset 4",
            "EQ Preset 5",
        ]

    @property
    def current_option(self) -> str | None:
        """Return the current EQ preset."""
        eq_value = self.coordinator.data.get("eq_preset")
        if eq_value is not None:
            try:
                return f"EQ Preset {int(eq_value)}"
            except (ValueError, TypeError):
                pass
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:equalizer"

    async def async_select_option(self, option: str) -> None:
        """Select an EQ preset."""
        # Extract number from "EQ Preset X"
        match = re.search(r'(\d+)', option)
        if match:
            eq_number = match.group(1)
            _LOGGER.info("Setting EQ preset to: %s", eq_number)
            await self.coordinator.api.set_value("netRemote.sys.audio.eqPreset", eq_number)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Could not parse EQ preset: %s", option)
