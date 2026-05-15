"""Config flow for My Frontier Silicon integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import FrontierSiliconAPI
from .const import DOMAIN, CONF_PIN, DEFAULT_PORT, DEFAULT_PIN

_LOGGER = logging.getLogger(__name__)


class FrontierSiliconConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Frontier Silicon."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Test connection
            api = FrontierSiliconAPI(
                host=user_input[CONF_HOST],
                port=user_input.get(CONF_PORT, DEFAULT_PORT),
                pin=user_input.get(CONF_PIN, DEFAULT_PIN),
            )

            try:
                # Try to create session
                session_id = await api.create_session(context="config_flow_test")
                if session_id:
                    # Get device name for unique_id
                    device_name, _ = await api.get_value(
                        "netRemote.sys.info.friendlyName",
                        context="config_flow_device_name"
                    )
                    
                    await api.close()

                    # Use device name or host as unique_id
                    unique_id = device_name or user_input[CONF_HOST]
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

					title = (
						user_input.get(CONF_NAME)
						or device_name
						or f"Frontier Silicon {user_input[CONF_HOST]}"
					)

					return self.async_create_entry(
						title=title,
						data=user_input,
					)
                    
                else:
                    errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error("Error connecting to device: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                await api.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_PIN, default=DEFAULT_PIN): str,
					vol.Optional(CONF_NAME): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return FrontierSiliconOptionsFlowHandler(config_entry)


class FrontierSiliconOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Frontier Silicon."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "debug_logging",
                        default=self.config_entry.options.get("debug_logging", False),
                    ): bool,
                    vol.Optional(
                        "auto_load_presets",
                        default=self.config_entry.options.get("auto_load_presets", True),
                    ): bool,
                    vol.Optional(
                        "scan_interval_off",
                        default=self.config_entry.options.get("scan_interval_off", 60),
                    ): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
                    vol.Optional(
                        "scan_interval_on",
                        default=self.config_entry.options.get("scan_interval_on", 30),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=60)),
                }
            ),
        )
