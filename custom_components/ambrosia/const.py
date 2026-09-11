"""Constants for Ambrosia Pollen Radar integration."""
from __future__ import annotations

DOMAIN = "ambrosia"

# Configuration keys
CONF_LOCATION_NAME = "location_name"
CONF_POLLEN_TYPES = "pollen_types"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_FORECAST_DAYS = "forecast_days"

DEFAULT_NAME = "Pollen Tracker"
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
        "default": False,
    },
    "grass_pollen": {
        "name_en": "Grass (Gramineae)",
        "name_ro": "Graminee / Iarbă",
        "icon": "mdi:seed",
        "default": False,
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

# Calibrated 5-level severity scale (grains/m3)
# Very Low (<5), Low (5-10), Moderate (10-30), High (30-100), Very High (>=100)
RISK_LEVELS = [
    {
        "max": 5,
        "level_en": "Very Low",
        "level_ro": "Foarte redus",
        "color_hex": "#2ecc71",
        "color_dec": 3066993,
        "icon": "mdi:shield-check",
    },
    {
        "max": 10,
        "level_en": "Low",
        "level_ro": "Redus",
        "color_hex": "#a3cb38",
        "color_dec": 10734392,
        "icon": "mdi:leaf",
    },
    {
        "max": 30,
        "level_en": "Moderate",
        "level_ro": "Moderat",
        "color_hex": "#f39c12",
        "color_dec": 15965202,
        "icon": "mdi:alert-circle",
    },
    {
        "max": 100,
        "level_en": "High",
        "level_ro": "Ridicat",
        "color_hex": "#e74c3c",
        "color_dec": 15158332,
        "icon": "mdi:alert-octagon",
    },
    {
        "max": 999999,
        "level_en": "Very High",
        "level_ro": "Foarte ridicat",
        "color_hex": "#8e44ad",
        "color_dec": 9323693,
        "icon": "mdi:alert-decagram",
    },
]

# Civic reporting & legal framework (Ambrosia / Ragweed)
CIVIC_MAP_URL = "https://www.hartaambroziei.ro/"
CIVIC_LAW_REF = "Legea nr. 62/2018 (modificată prin Legea 272/2023)"
CIVIC_FINE_REF = "Amenzi: 1.000 – 5.000 lei (persoane fizice) / 10.000 – 20.000 lei (persoane juridice)"
CIVIC_ACTION_GUIDE = "Marchează terenul infestat cu pin GPS și fotografii pe HartaAmbroziei.ro pentru sesizarea primăriilor locale."
