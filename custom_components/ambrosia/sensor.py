"""Sensor platform for Ambrosia & European Pollen integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_LOCATION_NAME, CONF_POLLEN_TYPES, DEFAULT_NAME, DOMAIN, POLLEN_SPECIES
from .coordinator import AmbrosiaDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambrosia sensors from config entry."""
    coordinator: AmbrosiaDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    location_name = entry.data.get(CONF_LOCATION_NAME, DEFAULT_NAME)
    selected_pollens = entry.options.get(CONF_POLLEN_TYPES, entry.data.get(CONF_POLLEN_TYPES, []))

    entities: list[SensorEntity] = []

    for pollen_key in selected_pollens:
        if pollen_key not in POLLEN_SPECIES:
            continue
        p_info = POLLEN_SPECIES[pollen_key]

        # 1. Main Current Concentration Sensor (with rich attributes)
        entities.append(
            AmbrosiaCurrentPollenSensor(
                coordinator=coordinator,
                entry=entry,
                pollen_key=pollen_key,
                pollen_info=p_info,
                location_name=location_name,
            )
        )

        # 2. Risk Level Sensor
        entities.append(
            AmbrosiaRiskLevelSensor(
                coordinator=coordinator,
                entry=entry,
                pollen_key=pollen_key,
                pollen_info=p_info,
                location_name=location_name,
            )
        )

        # 3. Max Today Sensor
        entities.append(
            AmbrosiaMaxTodaySensor(
                coordinator=coordinator,
                entry=entry,
                pollen_key=pollen_key,
                pollen_info=p_info,
                location_name=location_name,
            )
        )

        # 4. Max Tomorrow Sensor
        entities.append(
            AmbrosiaMaxTomorrowSensor(
                coordinator=coordinator,
                entry=entry,
                pollen_key=pollen_key,
                pollen_info=p_info,
                location_name=location_name,
            )
        )

        # 5. Max Day 3 Sensor
        entities.append(
            AmbrosiaMaxDay3Sensor(
                coordinator=coordinator,
                entry=entry,
                pollen_key=pollen_key,
                pollen_info=p_info,
                location_name=location_name,
            )
        )

    async_add_entities(entities)


class AmbrosiaBaseSensor(CoordinatorEntity[AmbrosiaDataCoordinator], SensorEntity):
    """Base sensor for Ambrosia integration."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AmbrosiaDataCoordinator,
        entry: ConfigEntry,
        pollen_key: str,
        pollen_info: dict[str, Any],
        location_name: str,
    ) -> None:
        """Initialize the base sensor."""
        super().__init__(coordinator)
        self.pollen_key = pollen_key
        self.pollen_info = pollen_info
        self.location_name = location_name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{pollen_key}")},
            "name": f"{location_name} {pollen_info['name_en']}",
            "manufacturer": "Copernicus CAMS Europe (Open-Meteo)",
            "model": "Regional Air Quality Ensemble",
            "entry_type": "service",
        }

    @property
    def pollen_data(self) -> dict[str, Any]:
        """Get coordinator data for this pollen."""
        if not self.coordinator.data or "pollens" not in self.coordinator.data:
            return {}
        return self.coordinator.data["pollens"].get(self.pollen_key, {})


class AmbrosiaCurrentPollenSensor(AmbrosiaBaseSensor):
    """Main sensor: Current pollen concentration."""

    _attr_native_unit_of_measurement = "grains/m³"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._attr_unique_id = f"{self.coordinator.name}_{self.pollen_key}_current"
        self._attr_name = f"{self.pollen_info['name_en']} Concentration"
        self._attr_icon = self.pollen_info.get("icon", "mdi:flower-pollen")

    @property
    def native_value(self) -> float | None:
        """Return current concentration in grains/m3."""
        return self.pollen_data.get("current_concentration")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return comprehensive forecast attributes."""
        d = self.pollen_data
        if not d:
            return {}
        return {
            "risk_level_en": d.get("risk_level_en"),
            "risk_level_ro": d.get("risk_level_ro"),
            "risk_color_hex": d.get("risk_color_hex"),
            "risk_color_dec": d.get("risk_color_dec"),
            "max_today": d.get("max_today"),
            "peak_hour_today": d.get("peak_hour_today"),
            "max_tomorrow": d.get("max_tomorrow"),
            "peak_hour_tomorrow": d.get("peak_hour_tomorrow"),
            "max_day3": d.get("max_day3"),
            "peak_hour_day3": d.get("peak_hour_day3"),
            "recommendation_en": d.get("recommendation_en"),
            "recommendation_ro": d.get("recommendation_ro"),
            "forecast_48h": d.get("forecast_48h", []),
            "time": self.coordinator.data.get("time_series", []),
            "hourly_values": d.get("hourly_values", []),
        }


class AmbrosiaRiskLevelSensor(AmbrosiaBaseSensor):
    """Sensor: Current Risk Level."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._attr_unique_id = f"{self.coordinator.name}_{self.pollen_key}_risk"
        self._attr_name = f"{self.pollen_info['name_en']} Risk Level"

    @property
    def native_value(self) -> str | None:
        """Return qualitative risk level."""
        return self.pollen_data.get("risk_level_ro")

    @property
    def icon(self) -> str:
        """Return icon adapting to risk."""
        return self.pollen_data.get("risk_icon", "mdi:shield-check")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "risk_level_en": self.pollen_data.get("risk_level_en"),
            "color_hex": self.pollen_data.get("risk_color_hex"),
            "color_dec": self.pollen_data.get("risk_color_dec"),
        }


class AmbrosiaMaxTodaySensor(AmbrosiaBaseSensor):
    """Sensor: Max concentration today."""

    _attr_native_unit_of_measurement = "grains/m³"
    _attr_icon = "mdi:chart-bell-curve"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._attr_unique_id = f"{self.coordinator.name}_{self.pollen_key}_max_today"
        self._attr_name = f"{self.pollen_info['name_en']} Max Today"

    @property
    def native_value(self) -> float | None:
        return self.pollen_data.get("max_today")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "peak_hour": self.pollen_data.get("peak_hour_today"),
        }


class AmbrosiaMaxTomorrowSensor(AmbrosiaBaseSensor):
    """Sensor: Max concentration tomorrow."""

    _attr_native_unit_of_measurement = "grains/m³"
    _attr_icon = "mdi:calendar-today"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._attr_unique_id = f"{self.coordinator.name}_{self.pollen_key}_max_tomorrow"
        self._attr_name = f"{self.pollen_info['name_en']} Max Tomorrow"

    @property
    def native_value(self) -> float | None:
        return self.pollen_data.get("max_tomorrow")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "peak_hour": self.pollen_data.get("peak_hour_tomorrow"),
        }


class AmbrosiaMaxDay3Sensor(AmbrosiaBaseSensor):
    """Sensor: Max concentration day after tomorrow."""

    _attr_native_unit_of_measurement = "grains/m³"
    _attr_icon = "mdi:calendar-arrow-right"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._attr_unique_id = f"{self.coordinator.name}_{self.pollen_key}_max_day3"
        self._attr_name = f"{self.pollen_info['name_en']} Max Day 3"

    @property
    def native_value(self) -> float | None:
        return self.pollen_data.get("max_day3")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "peak_hour": self.pollen_data.get("peak_hour_day3"),
        }
