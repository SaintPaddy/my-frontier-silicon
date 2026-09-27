"""My Frontier Silicon Integration for Home Assistant."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .coordinator import FrontierSiliconConfigEntry, FrontierSiliconCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.MEDIA_PLAYER,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: FrontierSiliconConfigEntry) -> bool:
    """Set up My Frontier Silicon from a config entry."""
    _LOGGER.info("Setting up My Frontier Silicon integration")
    
    # Create coordinator
    coordinator = FrontierSiliconCoordinator(hass, entry)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    entry.runtime_data = coordinator
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FrontierSiliconConfigEntry) -> bool:
    """Unload a config entry.

    The coordinator is shut down automatically when the entry unloads.
    """
    _LOGGER.info("Unloading My Frontier Silicon integration")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
