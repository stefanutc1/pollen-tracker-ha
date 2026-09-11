"""Config flow for Ambrosia Pollen Radar."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
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
            location_name = str(user_input.get(CONF_LOCATION_NAME, DEFAULT_NAME)).strip()
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
                        CONF_SCAN_INTERVAL: int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
                        CONF_FORECAST_DAYS: int(user_input.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS)),
                    },
                )

        default_lat = float(self.hass.config.latitude) if self.hass.config.latitude is not None else 44.4323
        default_lon = float(self.hass.config.longitude) if self.hass.config.longitude is not None else 26.1063
        default_location = str(self.hass.config.location_name or DEFAULT_NAME)
        default_pollens = [k for k, v in POLLEN_SPECIES.items() if v.get("default", False)]

        schema = vol.Schema(
            {
                vol.Required(CONF_LOCATION_NAME, default=default_location): cv.string,
                vol.Required(CONF_LATITUDE, default=default_lat): cv.latitude,
                vol.Required(CONF_LONGITUDE, default=default_lon): cv.longitude,
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
                vol.Optional(CONF_FORECAST_DAYS, default=str(DEFAULT_FORECAST_DAYS)): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value="3", label="3 Days Forecast"),
                            selector.SelectOptionDict(value="5", label="5 Days Forecast"),
                            selector.SelectOptionDict(value="7", label="7 Days Forecast"),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=15,
                        max=1440,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
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
            return self.async_create_entry(
                title="",
                data={
                    CONF_POLLEN_TYPES: user_input.get(CONF_POLLEN_TYPES, []),
                    CONF_SCAN_INTERVAL: int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
                }
            )

        current_pollens = self.config_entry.options.get(
            CONF_POLLEN_TYPES,
            self.config_entry.data.get(
                CONF_POLLEN_TYPES, [k for k, v in POLLEN_SPECIES.items() if v.get("default")]
            ),
        )
        current_scan = int(self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ))

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
                vol.Optional(CONF_SCAN_INTERVAL, default=current_scan): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=15,
                        max=1440,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
