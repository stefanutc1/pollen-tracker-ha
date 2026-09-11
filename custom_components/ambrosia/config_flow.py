"""Config flow for Ambrosia Pollen Radar."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_FORECAST_DAYS,
    CONF_LOCATION_NAME,
    CONF_POLLEN_TYPES,
    CONF_SCAN_INTERVAL,
    DEFAULT_FORECAST_DAYS,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POLLEN_SPECIES,
)

_LOGGER = logging.getLogger(__name__)


def get_pollen_options() -> list[selector.SelectOptionDict]:
    """Return pollen selector options."""
    return [
        selector.SelectOptionDict(
            value=key,
            label=f"{info['name_en']} ({info['name_ro']})"
        )
        for key, info in POLLEN_SPECIES.items()
    ]


class AmbrosiaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ambrosia Pollen Radar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            location_name = user_input.get(CONF_LOCATION_NAME, DEFAULT_NAME).strip()
            lat = round(float(user_input[CONF_LATITUDE]), 4)
            lon = round(float(user_input[CONF_LONGITUDE]), 4)
            selected_pollens = user_input.get(CONF_POLLEN_TYPES, [])

            if not selected_pollens:
                errors[CONF_POLLEN_TYPES] = "no_pollen_selected"
            else:
                unique_id = f"{DOMAIN}_{lat}_{lon}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Ambrosia Radar ({location_name})",
                    data={
                        CONF_LOCATION_NAME: location_name,
                        CONF_LATITUDE: lat,
                        CONF_LONGITUDE: lon,
                        CONF_POLLEN_TYPES: selected_pollens,
                        CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                        CONF_FORECAST_DAYS: user_input.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS),
                    },
                )

        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude
        default_pollens = [k for k, v in POLLEN_SPECIES.items() if v.get("default", False)]

        schema = vol.Schema(
            {
                vol.Required(CONF_LOCATION_NAME, default=self.hass.config.location_name or DEFAULT_NAME): str,
                vol.Required(CONF_LATITUDE, default=default_lat): cv_latitude(),
                vol.Required(CONF_LONGITUDE, default=default_lon): cv_longitude(),
                vol.Required(
                    CONF_POLLEN_TYPES,
                    default=default_pollens,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=get_pollen_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_FORECAST_DAYS, default=DEFAULT_FORECAST_DAYS): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value="3", label="3 Days Forecast"),
                            selector.SelectOptionDict(value="5", label="5 Days Forecast"),
                            selector.SelectOptionDict(value="7", label="7 Days Forecast"),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=1440)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> AmbrosiaOptionsFlow:
        return AmbrosiaOptionsFlow(config_entry)


class AmbrosiaOptionsFlow(config_entries.OptionsFlow):
    """Handle Ambrosia options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_pollens = self.config_entry.options.get(
            CONF_POLLEN_TYPES,
            self.config_entry.data.get(
                CONF_POLLEN_TYPES, [k for k, v in POLLEN_SPECIES.items() if v.get("default")]
            ),
        )
        current_scan = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_POLLEN_TYPES,
                    default=current_pollens,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=get_pollen_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=current_scan): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=1440)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


def cv_latitude():
    return vol.All(vol.Coerce(float), vol.Range(min=-90, max=90))


def cv_longitude():
    return vol.All(vol.Coerce(float), vol.Range(min=-180, max=180))
