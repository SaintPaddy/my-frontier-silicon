"""Config flow for My Frontier Silicon integration."""
import logging
from typing import Any

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_PIN, DEFAULT_NAME, CONF_PIN
from .api import FrontierSiliconAPI

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)
    pin = data.get(CONF_PIN, DEFAULT_PIN)
    
    api = FrontierSiliconAPI(host, port, pin)
    
    # Test connection
    try:
        session_id = await api.create_session()
        if not session_id:
            raise ValueError("Failed to create session")
        
        # Get device name
        device_info = await api.get_device_info()
        device_name = device_info.get("name", DEFAULT_NAME)
        
        return {"title": device_name}
    except Exception as err:
        _LOGGER.error("Failed to connect to device: %s", err)
        raise


class FrontierSiliconConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Frontier Silicon."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Create unique ID from host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)
            except ValueError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_PIN, default=DEFAULT_PIN): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "name": "Frontier Silicon Device",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return FrontierSiliconOptionsFlow(config_entry)


class FrontierSiliconOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for My Frontier Silicon."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PIN,
                        default=self.config_entry.data.get(CONF_PIN, DEFAULT_PIN),
                    ): str,
                }
            ),
        )
