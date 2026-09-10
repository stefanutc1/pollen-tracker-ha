# 🌿 Ambrosia & European Pollen for Home Assistant (`ambrosia-ha`)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![Validate](https://img.shields.io/github/actions/workflow/status/ygreq/ambrosia-ha/validate.yml?branch=main&style=for-the-badge)](https://github.com/ygreq/ambrosia-ha/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Community](https://img.shields.io/badge/Community-Home%20Assistant%20Romania-red.svg?style=for-the-badge)](https://facebook.com)

A modern Home Assistant integration providing **Ambrosia (Ragweed) and European pollen forecasts**, powered by the **Copernicus Atmosphere Monitoring Service (CAMS Europe)** via the free **Open-Meteo Air Quality API**.

No physical pollen sensor needed! Get accurate 72-hour regional forecasts, peak concentration hours, dynamic risk severity, and morning notification summaries.

---

## 🇷🇴 Descriere în Română

Un detector și sistem de prognoză pentru **ambrozie** și alți poleni alergeni (peliniță, graminee/iarbă, mesteacăn, măslin, arin). Datele provin direct din modelul european de referință **CAMS Europe (Copernicus)**, prin API-ul Open-Meteo, cu o granularitate orară pe 3 zile.

### 🌟 Funcționalități Cheie
* ⚡ **Config Flow (Fără YAML):** Configurare directă din interfața Home Assistant (*Settings > Devices & Services > Add Integration*). Detectează automat coordonatele casei tale.
* 🌿 **Alergeni Suportați:**
  * **Ambrozie (Ragweed)** — `ragweed_pollen` (principalul alergen de toamnă din România)
  * **Pelin / Peliniță (Mugwort / Artemisia)** — `mugwort_pollen`
  * **Graminee / Iarbă (Grass)** — `grass_pollen`
  * **Mesteacăn (Birch)** — `birch_pollen`
  * **Măslin (Olive)** — `olive_pollen`
  * **Arin (Alder)** — `alder_pollen`
* 📊 **Senzori & Valori Create Automat:**
  * Concentrație actuală orară (`grains/m³`)
  * Nivel de risc calitativ conform standardelor europene de aerobiologie: **Foarte scăzut**, **Scăzut**, **Moderat**, **Ridicat**, **Extrem**
  * Coduri de culoare dinamice (HEX și Decimal) pentru stilizare carduri și notificări Discord
  * **Maximul de Azi + Ora de Vârf** (ex: *14.0 grains/m³ la ora 10:00*)
  * **Maximul de Mâine + Ora de Vârf**
  * **Maximul de Poimâine + Ora de Vârf**
  * Serie orară completă pe 48-72h pregătită pentru grafice ApexCharts
  * Recomandare practică automată (când să aerisiți, închiderea ferestrelor la orele de vârf, pornirea purificatorului de aer).

---

## 📥 Instalare

### Metoda 1: Prin HACS (Recomandat)

1. Deschide **HACS** în Home Assistant.
2. Mergi la cele 3 puncte (dreapta-sus) > **Custom repositories**.
3. Adaugă URL-ul: `https://github.com/ygreq/ambrosia-ha`
4. Alege Categoria: **Integration**.
5. Apasă pe **Ambrosia & European Pollen** și selectează **Download**.
6. Repornește Home Assistant.
7. Mergi la **Settings > Devices & Services > Add Integration** și caută **Ambrosia & European Pollen**.

---

### Metoda 2: Instalare Manuală

1. Descarcă arhiva repository-ului.
2. Copiază folderul `custom_components/ambrosia` în directorul `/config/custom_components/` al instanței tale Home Assistant.
3. Repornește Home Assistant.
4. Adaugă integrarea din **Settings > Devices & Services > Add Integration**.

---

## 📊 Card Lovelace Dashboard (48h Forecast)

Folosește cardurile populare din HACS: `custom:button-card`, `custom:apexcharts-card`, `custom:vertical-stack-in-card`.

```yaml
type: custom:vertical-stack-in-card
title: 🌿 Monitorizare Ambrozie & Polen
cards:
  - type: custom:button-card
    entity: sensor.ambrosia_ragweed_ambrosia_concentration
    name: Concentrație Actuală Ambrozie
    icon: mdi:flower-pollen
    show_name: true
    show_state: true
    show_label: true
    label: >
      [[[
        const risk = states['sensor.ambrosia_ragweed_ambrosia_risk_level'] ? states['sensor.ambrosia_ragweed_ambrosia_risk_level'].state : 'Calculare...';
        return 'Nivel Risc: ' + risk;
      ]]]
    styles:
      card:
        - padding: 18px 16px
        - border-radius: 12px
        - background-color: >
            [[[
              const v = parseFloat(entity.state) || 0;
              if (v < 1) return 'rgba(46, 204, 113, 0.15)';
              if (v < 10) return 'rgba(163, 203, 56, 0.18)';
              if (v < 50) return 'rgba(243, 156, 18, 0.22)';
              if (v < 200) return 'rgba(231, 76, 60, 0.25)';
              return 'rgba(142, 68, 173, 0.3)';
            ]]]
        - border: >
            [[[
              const v = parseFloat(entity.state) || 0;
              if (v < 1) return '2px solid #2ecc71';
              if (v < 10) return '2px solid #a3cb38';
              if (v < 50) return '2px solid #f39c12';
              if (v < 200) return '2px solid #e74c3c';
              return '2px solid #8e44ad';
            ]]]

  - type: horizontal-stack
    cards:
      - type: custom:button-card
        entity: sensor.ambrosia_ragweed_ambrosia_max_today
        name: Maxim Azi
        show_name: true
        show_state: true
        show_label: true
        label: >
          [[[
            const h = entity.attributes.peak_hour || 'N/A';
            return 'Vârf ora ' + h;
          ]]]
      - type: custom:button-card
        entity: sensor.ambrosia_ragweed_ambrosia_max_tomorrow
        name: Maxim Mâine
        show_name: true
        show_state: true
        show_label: true
        label: >
          [[[
            const h = entity.attributes.peak_hour || 'N/A';
            return 'Vârf ora ' + h;
          ]]]
      - type: custom:button-card
        entity: sensor.ambrosia_ragweed_ambrosia_max_day_3
        name: Maxim Poimâine
        show_name: true
        show_state: true
        show_label: true
        label: >
          [[[
            const h = entity.attributes.peak_hour || 'N/A';
            return 'Vârf ora ' + h;
          ]]]

  - type: custom:apexcharts-card
    header:
      show: true
      title: Prognoză Orară Ambrozie (Următoarele 48h)
    span:
      start: hour
      offset: "-1h"
    graph_span: 48h
    now:
      show: true
      label: Acum
      color: "#e74c3c"
    series:
      - entity: sensor.ambrosia_ragweed_ambrosia_concentration
        name: Ambrozie
        unit: grains/m³
        type: area
        color: "#f39c12"
        opacity: 0.35
        data_generator: |
          const forecast = entity.attributes.forecast_48h || [];
          return forecast.map(item => [new Date(item.time).getTime(), item.value]);
```

---

## 🔔 Automatizare Discord: Raport Matinal

Adăugați această automatizare în Home Assistant pentru a primi în fiecare dimineață la 07:45 rezumatul complet pe canalul de Discord (prin Webhook):

```yaml
alias: "🌿 Notificare Matinală Ambrozie pe Discord"
trigger:
  - trigger: time
    at: "07:45:00"
action:
  - action: uri.request # sau rest_command
    data:
      url: "YOUR_DISCORD_WEBHOOK_URL_HERE"
      method: POST
      headers:
        Content-Type: "application/json"
      body: >
        {% set sensor = 'sensor.ambrosia_ragweed_ambrosia_concentration' %}
        {% set cur = states(sensor) | float(0) %}
        {% set risc = state_attr(sensor, 'risk_level_ro') | default('Moderat', true) %}
        {% set col = state_attr(sensor, 'risk_color_dec') | default(15965202, true) %}
        {% set max_azi = state_attr(sensor, 'max_today') | default(0, true) %}
        {% set ora_azi = state_attr(sensor, 'peak_hour_today') | default('N/A', true) %}
        {% set max_tom = state_attr(sensor, 'max_tomorrow') | default(0, true) %}
        {% set ora_tom = state_attr(sensor, 'peak_hour_tomorrow') | default('N/A', true) %}
        {% set reco = state_attr(sensor, 'recommendation_ro') | default('', true) %}
        {
          "username": "Prognoză Ambrozie & Polen",
          "avatar_url": "https://brands.home-assistant.io/_/air_quality/icon.png",
          "embeds": [
            {
              "title": "🌿 Raport Ambrozie: Risc " ~ risc,
              "description": "Prognoză Copernicus CAMS Europe.",
              "color": {{ col }},
              "fields": [
                {
                  "name": "📍 Nivel Acum",
                  "value": "**" ~ cur ~ " grains/m³** (" ~ risc ~ ")",
                  "inline": true
                },
                {
                  "name": "☀️ Maxim Azi",
                  "value": "**" ~ max_azi ~ " grains/m³**\n(Vârf estimat la ora **" ~ ora_azi ~ "**)",
                  "inline": true
                },
                {
                  "name": "🔮 Maxim Mâine",
                  "value": "**" ~ max_tom ~ " grains/m³** (ora " ~ ora_tom ~ ")",
                  "inline": true
                },
                {
                  "name": "💡 Recomandare",
                  "value": "{{ reco }}",
                  "inline": false
                }
              ],
              "footer": {
                "text": "Open-Meteo • CAMS Europe • Home Assistant",
                "icon_url": "https://brands.home-assistant.io/_/homeassistant/icon.png"
              }
            }
          ]
        }
```

---

## 📄 Licență
Acest proiect este licențiat sub licența **MIT** — vezi fișierul [LICENSE](LICENSE) pentru detalii.
Creat de [Cristian Iordache (@ygreq)](https://github.com/ygreq).
