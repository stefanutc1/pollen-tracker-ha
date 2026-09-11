# 🌿 Ambrosia Pollen Radar for Home Assistant (`ambrosia-ha`)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![Validate](https://img.shields.io/github/actions/workflow/status/ygreq/ambrosia-ha/validate.yml?branch=main&style=for-the-badge)](https://github.com/ygreq/ambrosia-ha/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

An intelligent Home Assistant integration for **Ambrosia (Ragweed) and allergen pollen forecasting**, powered by the European **Copernicus Atmosphere Monitoring Service (CAMS Europe)** via the free **Open-Meteo Air Quality API**.

No physical sensor required! Provides hourly regional forecasts, peak exposure hours, trend analysis, and an optimal daily **Ventilation Window** algorithm.

---

## 🌟 Key Features

* ⚡ **Config Flow (Zero YAML):** Easy visual setup in Home Assistant (*Settings > Devices & Services > Add Integration > Ambrosia Pollen Radar*). Automatically detects your Home Assistant coordinates.
* 🪟 **Smart Ventilation Window Sensor (`ventilation_window`):**
  * Algorithms calculate the optimal 2-hour daytime window (06:00–23:00) with minimal pollen exposure, with protection against morning pollen surge spikes.
  * Includes binary attribute `is_active_now: true/false` to trigger automated home ventilation (HRV, window actuators, or notification reminders).
* 📈 **Pollen Trend Sensor (`trend`):**
  * Immediate 3-hour outlook: **Rising ↗️**, **Falling ↘️**, or **Stable ➡️**.
* 🌿 **Supported Pollen Species:**
  * **Ragweed (Ambrosia)** — `ragweed_pollen` (major autumn allergen)
  * **Mugwort (Artemisia / Pelin)** — `mugwort_pollen`
  * **Grass (Gramineae)** — `grass_pollen`
  * **Birch** — `birch_pollen`
  * **Olive** — `olive_pollen`
  * **Alder** — `alder_pollen`
* ⚖️ **Calibrated 5-Level Severity Scale:**
  * **Very Low:** `< 5` grains/m³ (Green `#2ecc71`)
  * **Low:** `5 – 10` grains/m³ (Yellow-Green `#a3cb38`)
  * **Moderate:** `10 – 30` grains/m³ (Orange `#f39c12`)
  * **High:** `30 – 100` grains/m³ (Red `#e74c3c`)
  * **Very High:** `≥ 100` grains/m³ (Purple `#8e44ad`)
* 🌍 **Native Bilingual Support:**
  * English & Romanian native translations. UI displays in Romanian when HA language is Romanian.
  * All sensors expose bilingual attributes (`risk_level_en` / `risk_level_ro`, `recommendation_en` / `recommendation_ro`, `trend_en` / `trend_ro`).
* 🗺️ **Civic & Community Mapping:**
  * Direct attribute links to **HartaAmbroziei.ro** and legal reference.

---

## 📥 Installation

### Method 1: Via HACS (Recommended)

1. Open **HACS** in your Home Assistant.
2. Click the 3 dots in the upper right corner > **Custom repositories**.
3. Add repository URL: `https://github.com/ygreq/ambrosia-ha`
4. Category: **Integration**.
5. Find **Ambrosia Pollen Radar**, click **Download**, then restart Home Assistant.
6. Go to **Settings > Devices & Services > Add Integration**, search for **Ambrosia Pollen Radar**.

### Method 2: Manual Installation

1. Download the latest release from GitHub.
2. Copy `custom_components/ambrosia` into your `/config/custom_components/` folder.
3. Restart Home Assistant and add the integration via the UI.

---

## 📊 Lovelace Dashboard Card (with ApexCharts & Ventilation Badge)

```yaml
type: custom:vertical-stack-in-card
title: 🌿 Ambrosia Pollen Radar
cards:
  # Main Dynamic Banner
  - type: custom:button-card
    entity: sensor.ambrosia_radar_home_ragweed_ambrosia_concentration
    name: Ambrosia Concentration
    icon: mdi:flower-pollen
    show_name: true
    show_state: true
    show_label: true
    label: >
      [[[
        const risk = entity.attributes.risk_level_en || 'Calculating...';
        const trend = entity.attributes.trend_en || 'Stable';
        return 'Risk: ' + risk + ' • Trend: ' + trend;
      ]]]
    styles:
      card:
        - padding: 16px
        - border-radius: 12px
        - background-color: >
            [[[
              const v = parseFloat(entity.state) || 0;
              if (v < 5) return 'rgba(46, 204, 113, 0.15)';
              if (v < 10) return 'rgba(163, 203, 56, 0.18)';
              if (v < 30) return 'rgba(243, 156, 18, 0.22)';
              if (v < 100) return 'rgba(231, 76, 60, 0.25)';
              return 'rgba(142, 68, 173, 0.3)';
            ]]]
        - border: >
            [[[
              const v = parseFloat(entity.state) || 0;
              if (v < 5) return '2px solid #2ecc71';
              if (v < 10) return '2px solid #a3cb38';
              if (v < 30) return '2px solid #f39c12';
              if (v < 100) return '2px solid #e74c3c';
              return '2px solid #8e44ad';
            ]]]

  # Quick Indicators: Ventilation Window & Today Peak
  - type: horizontal-stack
    cards:
      - type: custom:button-card
        entity: sensor.ambrosia_radar_home_ragweed_ambrosia_ventilation_window
        name: Best Ventilation
        icon: mdi:window-open-variant
        show_name: true
        show_state: true
        show_label: true
        label: >
          [[[
            return entity.attributes.is_active_now ? '🟢 Active Now!' : 'Optimal Window';
          ]]]
      - type: custom:button-card
        entity: sensor.ambrosia_radar_home_ragweed_ambrosia_max_today
        name: Peak Today
        icon: mdi:chart-bell-curve
        show_name: true
        show_state: true
        show_label: true
        label: >
          [[[
            return 'Peak at ' + (entity.attributes.peak_hour || 'N/A');
          ]]]

  # 48h Forecast Curve
  - type: custom:apexcharts-card
    header:
      show: true
      title: 48-Hour Hourly Forecast
    span:
      start: hour
      offset: "-1h"
    graph_span: 48h
    now:
      show: true
      label: Now
      color: "#e74c3c"
    series:
      - entity: sensor.ambrosia_radar_home_ragweed_ambrosia_concentration
        name: Ambrosia
        unit: grains/m³
        type: area
        color: "#f39c12"
        opacity: 0.35
        data_generator: |
          const forecast = entity.attributes.forecast_48h || [];
          return forecast.map(item => [new Date(item.time).getTime(), item.value]);
```

---

## 🔔 Discord Morning Notification Automation

```yaml
alias: "🌿 Ambrosia Morning Discord Report"
trigger:
  - trigger: time
    at: "07:45:00"
action:
  - action: uri.request
    data:
      url: "YOUR_DISCORD_WEBHOOK_URL"
      method: POST
      headers:
        Content-Type: "application/json"
      body: >
        {% set s = 'sensor.ambrosia_radar_home_ragweed_ambrosia_concentration' %}
        {% set cur = states(s) | float(0) %}
        {% set risc = state_attr(s, 'risk_level_ro') | default('Moderat', true) %}
        {% set col = state_attr(s, 'risk_color_dec') | default(15965202, true) %}
        {% set max_azi = state_attr(s, 'max_today') | default(0, true) %}
        {% set ora_azi = state_attr(s, 'peak_hour_today') | default('N/A', true) %}
        {% set vent = state_attr(s, 'ventilation_window') | default('N/A', true) %}
        {% set reco = state_attr(s, 'recommendation_ro') | default('', true) %}
        {
          "username": "Ambrosia Pollen Radar",
          "avatar_url": "https://brands.home-assistant.io/_/air_quality/icon.png",
          "embeds": [
            {
              "title": "🌿 Raport Polen Ambrozie: Risc " ~ risc,
              "color": {{ col }},
              "fields": [
                {
                  "name": "📍 Nivel Acum",
                  "value": "**" ~ cur ~ " grains/m³** (" ~ risc ~ ")",
                  "inline": true
                },
                {
                  "name": "☀️ Maxim Azi",
                  "value": "**" ~ max_azi ~ " grains/m³** (ora " ~ ora_azi ~ ")",
                  "inline": true
                },
                {
                  "name": "🪟 Fereastră Aerisire",
                  "value": "**" ~ vent ~ "**",
                  "inline": false
                },
                {
                  "name": "💡 Recomandare",
                  "value": "{{ reco }}",
                  "inline": false
                }
              ]
            }
          ]
        }
```

---

# 🇷🇴 Prezentare în Română: Radar polen ambrozie

Integrare Home Assistant dedicată monitorizării și prognozei pentru **ambrozie și polen alergen**, folosind modelul numeric **Copernicus CAMS Europe** via Open-Meteo.

### ✨ Funcții Avansate
1. **Fereastra Optimă de Aerisire (`ventilation_window`):**
   * Calculează intervalul optim de 2 ore din timpul zilei cu expunere minimă la polen, aplicând penalizări la salturile bruște de dimineață.
   * Include atributul `is_active_now: true/false` pentru declanșarea automatizărilor de aerisire.
2. **Tendință Polen (`trend`):**
   * Indică evoluția în următoarele 3 ore: *În creștere*, *În scădere* sau *Stabil*.
3. **Scală Calibrată pe 5 Niveluri:**
   * *Foarte redus (<5)*, *Redus (5–10)*, *Moderat (10–30)*, *Ridicat (30–100)*, *Foarte ridicat (≥100)*.
4. **Bilingv Nativ:**
   * Când limba Home Assistant este Română, interfața, configurarea și senzorii apar automat în limba română.

---

## 📄 License
MIT License • Created with ❤️ by [Cristian Iordache (@ygreq)](https://github.com/ygreq).
