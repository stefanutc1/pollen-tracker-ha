"""DataUpdateCoordinator for Ambrosia & European Pollen."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_DOMAIN_MODEL,
    DOMAIN,
    OPEN_METEO_API_URL,
    POLLEN_SPECIES,
    RISK_LEVELS,
)

_LOGGER = logging.getLogger(__name__)


def get_risk_info(value: float) -> dict[str, Any]:
    """Return risk classification based on pollen concentration."""
    for r in RISK_LEVELS:
        if value < r["max"]:
            return r
    return RISK_LEVELS[-1]


class AmbrosiaDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch CAMS Europe pollen forecast from Open-Meteo."""

    def __init__(
        self,
        hass: HomeAssistant,
        latitude: float,
        longitude: float,
        pollen_types: list[str],
        forecast_days: int = 3,
        scan_interval_minutes: int = 60,
    ) -> None:
        """Initialize the coordinator."""
        self.latitude = latitude
        self.longitude = longitude
        self.pollen_types = pollen_types
        self.forecast_days = forecast_days
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval_minutes),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch pollen data from Open-Meteo Air Quality API."""
        hourly_vars = ",".join(self.pollen_types)
        params = {
            "latitude": str(self.latitude),
            "longitude": str(self.longitude),
            "hourly": hourly_vars,
            "domains": DEFAULT_DOMAIN_MODEL,
            "forecast_days": str(self.forecast_days),
            "timezone": "auto",
        }

        try:
            async with self.session.get(OPEN_METEO_API_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise UpdateFailed(f"Open-Meteo API returned HTTP {resp.status}: {text}")
                data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching pollen forecast: {err}") from err

        hourly = data.get("hourly", {})
        times: list[str] = hourly.get("time", [])

        if not times:
            raise UpdateFailed("Empty forecast received from Open-Meteo API")

        # Parse data for each requested pollen type
        now_dt = datetime.now()
        cur_hour_str = now_dt.strftime("%Y-%m-%dT%H:00")
        today_str = now_dt.strftime("%Y-%m-%d")
        tomorrow_str = (now_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        day3_str = (now_dt + timedelta(days=2)).strftime("%Y-%m-%d")

        cur_index = 0
        for i, t in enumerate(times):
            if t.startswith(cur_hour_str[:13]):
                cur_index = i
                break

        results: dict[str, Any] = {
            "latitude": data.get("latitude", self.latitude),
            "longitude": data.get("longitude", self.longitude),
            "elevation": data.get("elevation", 0),
            "timezone": data.get("timezone", "UTC"),
            "time_series": times,
            "pollens": {},
        }

        for p_key in self.pollen_types:
            vals: list[float] = [float(v or 0) for v in hourly.get(p_key, [])]
            if not vals:
                continue

            current_val = round(vals[cur_index], 1) if cur_index < len(vals) else 0.0
            risk = get_risk_info(current_val)

            # Calculate today max + peak hour
            today_pairs = [(t, v) for t, v in zip(times, vals) if t.startswith(today_str)]
            max_today_pair = max(today_pairs, key=lambda x: x[1]) if today_pairs else ("N/A", 0.0)
            max_today = round(max_today_pair[1], 1)
            peak_hour_today = max_today_pair[0][11:16] if len(max_today_pair[0]) >= 16 else "N/A"

            # Calculate tomorrow max + peak hour
            tom_pairs = [(t, v) for t, v in zip(times, vals) if t.startswith(tomorrow_str)]
            max_tom_pair = max(tom_pairs, key=lambda x: x[1]) if tom_pairs else ("N/A", 0.0)
            max_tomorrow = round(max_tom_pair[1], 1)
            peak_hour_tom = max_tom_pair[0][11:16] if len(max_tom_pair[0]) >= 16 else "N/A"

            # Calculate day3 max + peak hour
            day3_pairs = [(t, v) for t, v in zip(times, vals) if t.startswith(day3_str)]
            max_d3_pair = max(day3_pairs, key=lambda x: x[1]) if day3_pairs else ("N/A", 0.0)
            max_day3 = round(max_d3_pair[1], 1)
            peak_hour_d3 = max_d3_pair[0][11:16] if len(max_d3_pair[0]) >= 16 else "N/A"

            # 48h curve for charts
            forecast_48h = [
                {"time": times[idx], "value": round(vals[idx], 1)}
                for idx in range(min(len(times), 48))
            ]

            # Dynamic recommendation
            if max_today >= 50 or current_val >= 50:
                reco_en = f"High pollen risk! Keep windows closed around peak hour ({peak_hour_today}), run your air purifier, and avoid prolonged outdoor activity."
                reco_ro = f"Risc ridicat! Închideți ferestrele în intervalul de vârf (ora {peak_hour_today}), porniți purificatorul de aer și limitați ieșirile prelungite."
            elif max_today >= 10 or current_val >= 10:
                reco_en = f"Moderate risk. Sensitive individuals may experience symptoms. Ventilate early morning before {peak_hour_today}."
                reco_ro = f"Risc moderat. Persoanele alergice pot resimți simptome. Recomandat aerisirea devreme dimineața înainte de ora {peak_hour_today}."
            else:
                reco_en = "Low pollen concentration. Good outdoor and ventilation conditions."
                reco_ro = "Nivel scăzut de polen. Puteți aerisi și desfășura activități în aer liber fără restricții."

            results["pollens"][p_key] = {
                "current_concentration": current_val,
                "risk_level_en": risk["level_en"],
                "risk_level_ro": risk["level_ro"],
                "risk_color_hex": risk["color_hex"],
                "risk_color_dec": risk["color_dec"],
                "risk_icon": risk["icon"],
                "max_today": max_today,
                "peak_hour_today": peak_hour_today,
                "max_tomorrow": max_tomorrow,
                "peak_hour_tomorrow": peak_hour_tom,
                "max_day3": max_day3,
                "peak_hour_day3": peak_hour_d3,
                "forecast_48h": forecast_48h,
                "hourly_values": vals[:72],
                "recommendation_en": reco_en,
                "recommendation_ro": reco_ro,
            }

        return results
