"""DataUpdateCoordinator for Ambrosia Pollen Radar."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CIVIC_ACTION_GUIDE,
    CIVIC_FINE_REF,
    CIVIC_LAW_REF,
    CIVIC_MAP_URL,
    DEFAULT_DOMAIN_MODEL,
    DOMAIN,
    OPEN_METEO_API_URL,
    RISK_LEVELS,
)

_LOGGER = logging.getLogger(__name__)


def get_risk_info(value: float) -> dict[str, Any]:
    """Return risk classification based on the 5-level scale."""
    for r in RISK_LEVELS:
        if value < r["max"]:
            return r
    return RISK_LEVELS[-1]


def calculate_trend(current_val: float, future_val: float | None) -> dict[str, str]:
    """Calculate trend comparing current concentration with +3 hours forecast."""
    if future_val is None:
        return {"en": "Stable", "ro": "Stabil", "icon": "mdi:arrow-right"}

    if future_val > (current_val * 1.12 + 1.0):
        return {"en": "Rising", "ro": "În creștere", "icon": "mdi:arrow-top-right"}
    elif future_val < (current_val * 0.88 - 1.0):
        return {"en": "Falling", "ro": "În scădere", "icon": "mdi:arrow-bottom-right"}
    else:
        return {"en": "Stable", "ro": "Stabil", "icon": "mdi:arrow-right"}


def find_best_ventilation_window(
    times: list[str], vals: list[float], now_dt: datetime
) -> dict[str, Any]:
    """Calculate the best 2-hour ventilation window with minimal pollen and surge penalty."""
    today_str = now_dt.strftime("%Y-%m-%d")
    now_hour = now_dt.hour

    # Parse rows for today between 06:00 and 23:00
    daytime_entries: list[tuple[datetime, float]] = []
    for t_str, v in zip(times, vals):
        if t_str.startswith(today_str):
            try:
                dt = datetime.fromisoformat(t_str)
                if 6 <= dt.hour <= 23:
                    daytime_entries.append((dt, v))
            except Exception:
                continue

    def evaluate_window(pool: list[tuple[datetime, float]]) -> dict[str, Any] | None:
        if len(pool) < 2:
            return None
        best: dict[str, Any] | None = None
        for i in range(len(pool) - 1):
            g0, g1 = pool[i], pool[i + 1]
            avg = (g0[1] + g1[1]) / 2.0
            max_v = max(g0[1], g1[1])
            exit_val = pool[i + 2][1] if (i + 2 < len(pool)) else max_v
            # Penalize if exiting the window causes a sudden pollen spike (e.g. morning blossom)
            surge_penalty = (
                (exit_val - max_v) * 0.7 if (exit_val > max_v * 1.3) else 0.0
            )
            score = avg * 0.5 + max_v * 0.5 + surge_penalty

            if best is None or score < best["score"]:
                end_dt = g1[0] + timedelta(hours=1)
                best = {
                    "score": score,
                    "avg": round(avg, 1),
                    "max": round(max_v, 1),
                    "start_dt": g0[0],
                    "end_dt": end_dt,
                    "start_hour": g0[0].strftime("%H:%M"),
                    "end_hour": end_dt.strftime("%H:%M"),
                }
        return best

    # If morning has passed (>= 08:00), look for best remaining daytime window
    remaining = [e for e in daytime_entries if e[0].hour >= now_hour]
    chosen = None
    if now_hour >= 8 and len(remaining) >= 2:
        chosen = evaluate_window(remaining)

    if not chosen and daytime_entries:
        chosen = evaluate_window(daytime_entries)

    if not chosen:
        return {
            "window": "N/A",
            "start": "N/A",
            "end": "N/A",
            "avg_concentration": 0.0,
            "is_active_now": False,
        }

    is_active_now = chosen["start_dt"] <= now_dt < chosen["end_dt"]
    window_label = f"{chosen['start_hour']} - {chosen['end_hour']}"

    return {
        "window": window_label,
        "start": chosen["start_hour"],
        "end": chosen["end_hour"],
        "avg_concentration": chosen["avg"],
        "is_active_now": is_active_now,
    }


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
        """Initialize coordinator."""
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
            async with self.session.get(
                OPEN_METEO_API_URL, params=params, timeout=15
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise UpdateFailed(
                        f"Open-Meteo API returned HTTP {resp.status}: {text}"
                    )
                data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching pollen forecast: {err}") from err

        hourly = data.get("hourly", {})
        times: list[str] = hourly.get("time", [])

        if not times:
            raise UpdateFailed("Empty forecast received from Open-Meteo API")

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
            "civic_map_url": CIVIC_MAP_URL,
            "civic_law_ref": CIVIC_LAW_REF,
            "civic_fine_ref": CIVIC_FINE_REF,
            "civic_action_guide": CIVIC_ACTION_GUIDE,
        }

        for p_key in self.pollen_types:
            vals: list[float] = [float(v or 0) for v in hourly.get(p_key, [])]
            if not vals:
                continue

            current_val = round(vals[cur_index], 1) if cur_index < len(vals) else 0.0
            risk = get_risk_info(current_val)

            # Trend (+3 hours ahead)
            future_val = vals[cur_index + 3] if (cur_index + 3 < len(vals)) else None
            trend_info = calculate_trend(current_val, future_val)

            # Max today + peak hour
            today_pairs = [
                (t, v) for t, v in zip(times, vals) if t.startswith(today_str)
            ]
            max_today_pair = (
                max(today_pairs, key=lambda x: x[1]) if today_pairs else ("N/A", 0.0)
            )
            max_today = round(max_today_pair[1], 1)
            peak_hour_today = (
                max_today_pair[0][11:16] if len(max_today_pair[0]) >= 16 else "N/A"
            )

            # Max tomorrow + peak hour
            tom_pairs = [
                (t, v) for t, v in zip(times, vals) if t.startswith(tomorrow_str)
            ]
            max_tom_pair = (
                max(tom_pairs, key=lambda x: x[1]) if tom_pairs else ("N/A", 0.0)
            )
            max_tomorrow = round(max_tom_pair[1], 1)
            peak_hour_tom = (
                max_tom_pair[0][11:16] if len(max_tom_pair[0]) >= 16 else "N/A"
            )

            # Max day3 + peak hour
            day3_pairs = [(t, v) for t, v in zip(times, vals) if t.startswith(day3_str)]
            max_d3_pair = (
                max(day3_pairs, key=lambda x: x[1]) if day3_pairs else ("N/A", 0.0)
            )
            max_day3 = round(max_d3_pair[1], 1)
            peak_hour_d3 = max_d3_pair[0][11:16] if len(max_d3_pair[0]) >= 16 else "N/A"

            # 48h forecast points for charts
            forecast_48h = [
                {"time": times[idx], "value": round(vals[idx], 1)}
                for idx in range(min(len(times), 48))
            ]

            # Best 2h ventilation window
            vent_window = find_best_ventilation_window(times, vals, now_dt)

            # Actionable recommendations
            if max_today >= 30 or current_val >= 30:
                reco_en = (
                    f"High pollen exposure! Keep windows closed during peak hours (around {peak_hour_today}). "
                    f"Best ventilation window: {vent_window['window']}."
                )
                reco_ro = (
                    "Expunere ridicată! Păstrați ferestrele închise în orele de vârf "
                    f"(în jurul orei {peak_hour_today}). Fereastră optimă de aerisire: {vent_window['window']}."
                )
            elif max_today >= 10 or current_val >= 10:
                reco_en = (
                    "Moderate pollen levels. Sensitive people may experience symptoms. "
                    f"Aerate preferably during the recommended window ({vent_window['window']})."
                )
                reco_ro = (
                    "Nivel moderat de polen. Persoanele alergice pot resimți simptome. "
                    f"Aerisiți de preferință în fereastra recomandată ({vent_window['window']})."
                )
            else:
                reco_en = (
                    "Low pollen concentration in your area. "
                    f"Favorable outdoor and ventilation conditions ({vent_window['window']})."
                )
                reco_ro = (
                    "Concentrație scăzută de polen în zonă. "
                    f"Condiții bune pentru aerisire și activități exterioare ({vent_window['window']})."
                )

            results["pollens"][p_key] = {
                "current_concentration": current_val,
                "risk_level_en": risk["level_en"],
                "risk_level_ro": risk["level_ro"],
                "risk_color_hex": risk["color_hex"],
                "risk_color_dec": risk["color_dec"],
                "risk_icon": risk["icon"],
                "trend_en": trend_info["en"],
                "trend_ro": trend_info["ro"],
                "trend_icon": trend_info["icon"],
                "max_today": max_today,
                "peak_hour_today": peak_hour_today,
                "max_tomorrow": max_tomorrow,
                "peak_hour_tomorrow": peak_hour_tom,
                "max_day3": max_day3,
                "peak_hour_day3": peak_hour_d3,
                "ventilation_window": vent_window["window"],
                "ventilation_start": vent_window["start"],
                "ventilation_end": vent_window["end"],
                "ventilation_avg": vent_window["avg_concentration"],
                "ventilation_active_now": vent_window["is_active_now"],
                "forecast_48h": forecast_48h,
                "hourly_values": vals[:72],
                "recommendation_en": reco_en,
                "recommendation_ro": reco_ro,
            }

        return results
