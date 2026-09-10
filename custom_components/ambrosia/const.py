"""Constants for the Ambrosia & European Pollen integration."""
from __future__ import annotations

DOMAIN = "ambrosia"

# Configuration keys
CONF_LOCATION_NAME = "location_name"
CONF_POLLEN_TYPES = "pollen_types"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_FORECAST_DAYS = "forecast_days"

DEFAULT_NAME = "Ambrosia"
DEFAULT_SCAN_INTERVAL = 60  # minutes
DEFAULT_FORECAST_DAYS = 3

# Open-Meteo Air Quality API
OPEN_METEO_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
DEFAULT_DOMAIN_MODEL = "cams_europe"

# Available pollen species supported by CAMS Europe
POLLEN_SPECIES = {
    "ragweed_pollen": {
        "name_en": "Ragweed (Ambrosia)",
        "name_ro": "Ambrozie",
        "icon": "mdi:flower-pollen",
        "default": True,
    },
    "mugwort_pollen": {
        "name_en": "Mugwort (Artemisia)",
        "name_ro": "Pelin / Peliniță",
        "icon": "mdi:grass",
        "default": True,
    },
    "grass_pollen": {
        "name_en": "Grass (Gramineae)",
        "name_ro": "Graminee / Iarbă",
        "icon": "mdi:seed",
        "default": True,
    },
    "birch_pollen": {
        "name_en": "Birch",
        "name_ro": "Mesteacăn",
        "icon": "mdi:tree",
        "default": False,
    },
    "olive_pollen": {
        "name_en": "Olive",
        "name_ro": "Măslin",
        "icon": "mdi:tree-outline",
        "default": False,
    },
    "alder_pollen": {
        "name_en": "Alder",
        "name_ro": "Arin",
        "icon": "mdi:nature",
        "default": False,
    },
}

# European aerobiology thresholds (grains/m3)
# Very Low (<1), Low (1-10), Moderate (10-50), High (50-200), Very High (>200)
RISK_LEVELS = [
    {"max": 1, "level_en": "Very Low", "level_ro": "Foarte scăzut", "color_hex": "#2ecc71", "color_dec": 3066993, "icon": "mdi:shield-check"},
    {"max": 10, "level_en": "Low", "level_ro": "Scăzut", "color_hex": "#a3cb38", "color_dec": 10734392, "icon": "mdi:leaf"},
    {"max": 50, "level_en": "Moderate", "level_ro": "Moderat", "color_hex": "#f39c12", "color_dec": 15965202, "icon": "mdi:alert-circle"},
    {"max": 200, "level_en": "High", "level_ro": "Ridicat", "color_hex": "#e74c3c", "color_dec": 15158332, "icon": "mdi:alert-octagon"},
    {"max": 999999, "level_en": "Extremely High", "level_ro": "Extrem", "color_hex": "#8e44ad", "color_dec": 9323693, "icon": "mdi:alert-decagram"},
]
