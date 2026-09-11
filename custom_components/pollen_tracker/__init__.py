"""The Ambrosia & European Pollen integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_FORECAST_DAYS,
    CONF_POLLEN_TYPES,
    CONF_SCAN_INTERVAL,
    DEFAULT_FORECAST_DAYS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POLLEN_SPECIES,
)
from .coordinator import AmbrosiaDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Ambrosia component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ambrosia from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    lat = entry.data[CONF_LATITUDE]
    lon = entry.data[CONF_LONGITUDE]
    pollen_types = entry.options.get(
        CONF_POLLEN_TYPES,
        entry.data.get(CONF_POLLEN_TYPES, [k for k, v in POLLEN_SPECIES.items() if v.get("default")]),
    )
    scan_interval = int(entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    ))
    forecast_days = int(entry.data.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS))

    coordinator = AmbrosiaDataCoordinator(
        hass,
        latitude=lat,
        longitude=lon,
        pollen_types=pollen_types,
        forecast_days=forecast_days,
        scan_interval_minutes=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
