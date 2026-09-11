# 🌿 Pollen Tracker for Home Assistant (`pollen-tracker-ha`)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![Validate](https://img.shields.io/github/actions/workflow/status/ygreq/pollen-tracker-ha/validate.yml?branch=main&style=for-the-badge)](https://github.com/ygreq/pollen-tracker-ha/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

An intelligent Home Assistant integration for **comprehensive seasonal pollen, allergen, and ragweed forecasting** across Europe, powered by the European Union's **Copernicus Atmosphere Monitoring Service (CAMS Europe)** via the free **Open-Meteo Air Quality API**.

No physical sensor required! Provides hourly regional forecasts, peak exposure hours, 3-hour trend analysis, an optimal daily **Smart Ventilation Window** algorithm, and built-in **civic reporting tools for Ragweed hot-spots in Romania (HartaAmbroziei.ro)**.

> [!IMPORTANT]
> **🌍 Geographic Coverage: Europe Only (Copernicus CAMS)**
> Pollen forecasting is powered by the European Union's **Copernicus CAMS European Air Quality Ensemble**. Consequently, **pollen data is exclusively available for locations within Europe** (latitudes ~30°N–72°N, longitudes ~25°W–45°E). Coordinates outside Europe (such as the US, Canada, or Asia) will return `null` for pollen parameters.
> 
> 🇷🇴 **Special Calibration for Romania & Romanian Users:**
> Ragweed (*Ambrosia artemisiifolia*) is an aggressive invasive weed severely affecting Central & Eastern Europe, with Romania experiencing heavy autumn infestations. This integration provides fine-tuned algorithms: a realistic 5-level concentration scale (`<5`, `5-10`, `10-30`, `30-100`, `≥100` grains/m³), civic reporting links ([HartaAmbroziei.ro](https://www.hartaambroziei.ro/) / Law 62/2018), and full bilingual attribute support (`_ro` and `_en`) for seamless Romanian automations and family dashboards.

---

## 🌾 Supported Pollen Species (Full Annual Coverage)

The integration monitors the 6 major aeroallergens modeled by Copernicus CAMS. You can enable any combination in the configuration flow:

| Species | English Name | Romanian Name | Peak Season | Allergy Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| `ragweed_pollen` | **Ragweed (Ambrosia)** | **Ambrozie** | Aug – Oct | Highly aggressive autumn allergen; morning pollen spikes. |
| `mugwort_pollen` | **Mugwort (Artemisia)** | **Pelin / Peliniță** | Jul – Sep | Blooms concurrently with Ragweed; **frequent cross-allergic reactions**. |
| `grass_pollen` | **Grass (Gramineae)** | **Graminee / Iarbă** | May – Jul | Most common pollen allergen across Europe. |
| `birch_pollen` | **Birch** | **Mesteacăn** | Mar – May | Major spring tree allergen in Northern and Central Europe. |
| `olive_pollen` | **Olive** | **Măslin** | Apr – Jun | Prominent Mediterranean allergen. |
| `alder_pollen` | **Alder** | **Arin** | Jan – Apr | Earliest blooming winter/spring tree allergen. |

> [!TIP]
> **💡 Late Summer / Autumn Recommendation (August – September):**  
> If you suffer from autumn allergies, **we strongly recommend tracking both Ragweed (Ambrosia) and Mugwort (Artemisia)**. They bloom in parallel, and over 60% of people sensitive to ragweed exhibit cross-reactivity with mugwort.

---

## 🌟 Key Features

* ⚡ **Config Flow (Zero YAML):** Easy visual setup in Home Assistant (*Settings > Devices & Services > Add Integration > Pollen Tracker*). Automatically detects your Home Assistant coordinates.
* 📦 **7 Dedicated Entities per Enabled Pollen:**
  * **Current Concentration** (`grains/m³`) with 48h hourly forecast array in attributes.
  * **Risk Level** (`Very Low`, `Low`, `Moderate`, `High`, `Very High`).
  * **Pollen Trend** (Immediate 3-hour outlook: **Rising ↗️**, **Falling ↘️**, or **Stable ➡️**).
  * **Smart Ventilation Window (`ventilation_window`):** Calculates the optimal 2-hour daytime window with lowest pollen exposure (protecting against diurnal morning bursts), including binary attribute `is_active_now: true/false` to trigger automated HRV ventilation or window alerts.
  * **Max Today** (forecast maximum + peak exposure hour).
  * **Max Tomorrow** (forecast maximum + peak exposure hour).
  * **Max Day 3** (forecast maximum + peak exposure hour).
* ⚖️ **Calibrated 5-Level Severity Scale:**
  * **Very Low:** `< 5` grains/m³ (Green `#2ecc71`)
  * **Low:** `5 – 10` grains/m³ (Yellow-Green `#a3cb38`)
  * **Moderate:** `10 – 30` grains/m³ (Orange `#f39c12`)
  * **High:** `30 – 100` grains/m³ (Red `#e74c3c`)
  * **Very High:** `≥ 100` grains/m³ (Purple `#8e44ad`)
* 🏛️ **Civic Action & Legal Framework (HartaAmbroziei.ro):**
  * Ragweed is the only allergen in Romania subject to statutory eradication under **Law 62/2018 (amended by Law 272/2023)**, with fines up to 20,000 RON.
  * Ragweed sensors expose direct attributes (`civic_map_url`, `civic_law_ref`, `civic_fine_ref`, `civic_action_guide`) linking to **[HartaAmbroziei.ro](https://www.hartaambroziei.ro/)** for GPS crowd-sourced reporting of unkept infested land.
* 🌍 **Native Bilingual Support (Why bilingual attributes?):**
  * **UI Localization:** Fully translated in both English and Romanian. If your Home Assistant language is set to Romanian, all setup dialogs and sensor names will automatically display in Romanian.
  * **Bilingual Sensor Attributes:** All sensors expose parallel attributes (`risk_level_en` / `risk_level_ro`, `recommendation_en` / `recommendation_ro`, `trend_en` / `trend_ro`).
  * **Why this is useful:** Many users keep their Home Assistant system language in **English** (for community blueprints, integrations, and forums), but want automated push notifications (Discord, Telegram, mobile app) and family dashboards in **Romanian**. Pre-translated attributes eliminate the need to write complex Jinja2 translation logic!

---

## 🏛️ Civic Action: Reporting Ragweed Infestations in Romania (HartaAmbroziei.ro)

Unlike tree or grass pollens, **Ragweed (Ambrosia) is legally regulated in Romania**. Landowners are legally required to clear ragweed by June 30th each year and maintain clean lots until the end of October.

### How Civic Reporting Works:
1. **Open the Map:** Access **[HartaAmbroziei.ro](https://www.hartaambroziei.ro/)** (developed by Asociația Stop Ambroziei).
2. **Mark an Infested Lot:** Tap the **"Marchează o zonă"** button (top right corner), pinpoint the infested land via GPS, and upload clear photos of the blooming ragweed.
3. **Official Action:** Reports are aggregated and forwarded to local town halls (*primării*) and local police to issue summons and fines (1,000–5,000 RON for individuals, 10,000–20,000 RON for companies).

### 📱 Actionable Mobile Notification Automation

When Home Assistant detects a High or Very High Ragweed concentration in your area, this automation sends a notification to your smartphone with an action button that opens **HartaAmbroziei.ro** with one tap:

```yaml
alias: "📢 Ragweed High Alert - Civic Report Notification"
trigger:
  - trigger: numeric_state
    entity_id: sensor.pollen_tracker_home_ragweed_ambrosia_concentration
    above: 30
action:
  - action: notify.notify
    data:
      title: "⚠️ Alertă Polen Ambrozie: Concentrație Ridicată!"
      message: >
        Concentrația de ambrozie a atins {{ states('sensor.pollen_tracker_home_ragweed_ambrosia_concentration') }} grains/m³! 
        Dacă observi terenuri neîngrijite infestate în cartier, raportează focarul către primărie.
      data:
        actions:
          - action: "URI"
            title: "📢 Raportează pe HartaAmbroziei.ro"
            uri: "https://www.hartaambroziei.ro/"
```

---

## 📥 Installation

### Method 1: Via HACS (Recommended)

1. Open **HACS** in your Home Assistant.
2. Click the 3 dots in the upper right corner > **Custom repositories**.
3. Add repository URL: `https://github.com/ygreq/pollen-tracker-ha`
4. Category: **Integration**.
5. Find **Pollen Tracker**, click **Download**, then restart Home Assistant.
6. Go to **Settings > Devices & Services > Add Integration**, search for **Pollen Tracker**.

### Method 2: Manual Installation

1. Download the latest release from GitHub.
2. Copy `custom_components/ambrosia` into your `/config/custom_components/` folder.
3. Restart Home Assistant and add the integration via the UI.

---

## 📊 Lovelace Dashboard Card (with ApexCharts & Civic Report Button)

```yaml
type: custom:vertical-stack-in-card
title: 🌿 Pollen Tracker
cards:
  # Main Dynamic Banner
  - type: custom:button-card
    entity: sensor.pollen_tracker_home_ragweed_ambrosia_concentration
    name: Ragweed Concentration
    icon: mdi:flower-pollen
    show_name: true
    show_state: true
    show_label: true
    label: >
      [[[
        const risk = entity.attributes.risk_level_en || 'Unknown';
        const trend = entity.attributes.trend_en || '';
        return `${risk.toUpperCase()} • Trend: ${trend}`;
      ]]]
    styles:
      card:
        - background-color: >
            [[[ return entity.attributes.risk_color_hex || '#2ecc71'; ]]]
        - color: '#ffffff'
        - font-weight: bold
        - border-radius: 12px
        - margin-bottom: 8px

  # Peak Exposure & Ventilation Times
  - type: glance
    show_name: true
    show_state: true
    entities:
      - entity: sensor.pollen_tracker_home_ragweed_ambrosia_max_today
        name: Peak Today
      - entity: sensor.pollen_tracker_home_ragweed_ambrosia_max_tomorrow
        name: Peak Tomorrow
      - entity: sensor.pollen_tracker_home_ragweed_ambrosia_ventilation_window
        name: Best Airing Window

  # Civic Action Button (HartaAmbroziei.ro)
  - type: custom:button-card
    name: "📢 Raportează teren infestat (HartaAmbroziei.ro)"
    icon: mdi:map-marker-alert
    tap_action:
      action: url
      url_path: https://www.hartaambroziei.ro/
    styles:
      card:
        - padding: 10px
        - border-radius: 8px
        - background-color: rgba(231, 76, 60, 0.12)
        - border: 1px solid #e74c3c
        - margin-top: 4px
        - margin-bottom: 8px
      name:
        - font-size: 13px
        - font-weight: 600
        - color: var(--primary-text-color)
      icon:
        - color: "#e74c3c"
        - width: 22px

  # 48-Hour Forecast Curve (ApexCharts)
  - type: custom:apexcharts-card
    header:
      show: true
      title: 48h Pollen Hourly Forecast
      show_states: false
    graph_span: 48h
    span:
      start: hour
    now:
      show: true
      label: Now
      color: '#e74c3c'
    series:
      - entity: sensor.pollen_tracker_home_ragweed_ambrosia_concentration
        name: Ragweed
        type: area
        color: '#f39c12'
        opacity: 0.3
        stroke_width: 2
        data_generator: |
          const forecast = entity.attributes.forecast_48h || [];
          return forecast.map(item => [new Date(item.time).getTime(), item.value]);
```

---

## 🔔 Discord Morning Notification Automation

```yaml
alias: "🌿 Pollen Morning Discord Report"
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
        {% set s = 'sensor.pollen_tracker_home_ragweed_ambrosia_concentration' %}
        {% set cur = states(s) | float(0) %}
        {% set risc = state_attr(s, 'risk_level_ro') | default('Moderat', true) %}
        {% set col = state_attr(s, 'risk_color_dec') | default(15965202, true) %}
        {% set max_azi = state_attr(s, 'max_today') | default(0, true) %}
        {% set ora_azi = state_attr(s, 'peak_hour_today') | default('N/A', true) %}
        {% set vent = state_attr(s, 'ventilation_window') | default('N/A', true) %}
        {% set reco = state_attr(s, 'recommendation_ro') | default('', true) %}
        {
          "username": "Pollen Tracker",
          "avatar_url": "https://brands.home-assistant.io/_/air_quality/icon.png",
          "embeds": [
            {
              "title": "🌿 Raport Polen & Alergeni: Risc " ~ risc,
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
                },
                {
                  "name": "🏛️ Implicare Civică",
                  "value": "[Raportează focar pe HartaAmbroziei.ro](https://www.hartaambroziei.ro/) (Legea 62/2018)",
                  "inline": false
                }
              ]
            }
          ]
        }
```

---

# 🇷🇴 Prezentare în Română: Tracker Polen & Alergeni

Integrare Home Assistant **pentru monitorizarea și prognoza completă a polenului și alergenilor** pe tot parcursul anului (ambrozie, pelin, graminee, mesteacăn, măslin, arin). Folosește modelul numeric european de referință **Copernicus CAMS Europe** via Open-Meteo.

> [!IMPORTANT]
> **🌍 Acoperire Geografică: Exclusiv Teritoriul Europei (Copernicus CAMS)**
> Prognoza polenului este asigurată de ansamblul european de modele numerice CAMS. Serviciul este disponibil **exclusiv pentru coordonate aflate pe continentul european** (latitudini ~30°N–72°N, longitudini ~25°V–45°E). Pentru locații din afara Europei (cum ar fi America de Nord/SUA), furnizorul de date nu deține modele deschise de polen și returnează valori nule (`null`).
> 
> 🇷🇴 **Calibrare specială pentru România și utilizatorii români:**
> În România, ambrozia este o problemă acută de sănătate publică. Integrarea include ajustări dedicate:
> - **Scală de risc pe 5 praguri** adaptată la expunerea reală locală (`<5` Foarte redus, `5-10` Redus, `10-30` Moderat, `30-100` Ridicat, `≥100` Foarte ridicat).
> - **Algoritm de aerisire (`ventilation_window`)** calibrat să evite orele critice ale dimineții când polenul atinge concentrații periculoase.
> - **Civic & Legal:** Link direct către [HartaAmbroziei.ro](https://www.hartaambroziei.ro/) și referință legislativă la Legea nr. 62/2018 (modificată prin Legea 272/2023).
> - **Atribute bilingve (`_ro` / `_en`):** Permite utilizatorilor cu Home Assistant în limba engleză să trimită notificări pe telefon sau Discord direct în limba română, fără șabloane Jinja2 complicate.

### 🏛️ Specificul Ambroziei în România: Obligație Legală & Sesizări Civice

Ambrozia (*Ambrosia artemisiifolia*) este singura plantă din România cu regim juridic sancționator:
* **Legea nr. 62/2018 (actualizată prin Legea 272/2023):** Proprietarii sau deținătorii de terenuri sunt obligați să desfășoare lucrări de combatere a ambroziei până la data de 30 iunie a fiecărui an și să mențină terenurile curate pe toată durata sezonului de vegetație (până în octombrie).
* **Amenzi:** De la **1.000 la 5.000 lei** pentru persoane fizice și de la **10.000 la 20.000 lei** pentru persoane juridice.
* **Platforma comunitară HartaAmbroziei.ro:** Dezvoltată de Asociația Stop Ambroziei, permite oricărui cetățean să marcheze terenurile infestate pe hartă cu coordonate GPS și fotografii. Sesizările sunt centralizate și transmise primăriilor locale și poliției locale pentru aplicarea legii.

Senzorul de ambrozie expune direct în atribute link-ul de raportare (`civic_map_url`), referința legală (`civic_law_ref`), amenzile (`civic_fine_ref`) și ghidul rapid de acțiune (`civic_action_guide`).

### 🌾 Specii de Polen Monitorizate
1. **Ambrozie (`ragweed_pollen`):** Sezon august – octombrie (alergenul numărul 1 de toamnă).
2. **Pelin / Peliniță (`mugwort_pollen`):** Sezon iulie – septembrie. *Recomandat să fie activat simultan cu ambrozia din cauza alergiilor încrucișate frecvente.*
3. **Graminee / Iarbă (`grass_pollen`):** Sezon mai – iulie (cel mai răspândit alergen din Europa).
4. **Mesteacăn (`birch_pollen`):** Sezon martie – mai (alergen major de primăvară).
5. **Măslin (`olive_pollen`):** Sezon aprilie – iunie (specific regiunilor mediteraneene).
6. **Arin (`alder_pollen`):** Sezon ianuarie – aprilie (polenizator timpuriu de iarnă/primăvară).

### ✨ Funcții Avansate (Generate pentru fiecare polen activat)
1. **Fereastra Optimă de Aerisire (`ventilation_window`):**
   * Calculează intervalul optim de 2 ore din timpul zilei cu expunere minimă la polen, aplicând penalizări la salturile bruște de dimineață.
   * Include atributul `is_active_now: true/false` pentru declanșarea automatizărilor de aerisire (recuperator de căldură HRV, notificări).
2. **Tendință Polen (`trend`):**
   * Indică evoluția în următoarele 3 ore: *În creștere*, *În scădere* sau *Stabil*.
3. **Maximul Zilnic & Ora de Vârf:**
   * Senzori separați pentru *Azi*, *Mâine* și *Poimâine* cu indicarea exactă a orei la care se atinge vârful.
4. **Scală Calibrată pe 5 Niveluri:**
   * *Foarte redus (<5)*, *Redus (5–10)*, *Moderat (10–30)*, *Ridicat (30–100)*, *Foarte ridicat (≥100)*.
5. **Bilingv Nativ & Atribute Bilingve:**
   * Toate denumirile, valorile și atributele sunt disponibile bilingv (`_ro` și `_en`).

---

## 📄 License
MIT License • Created with ❤️ by [Cristian Iordache (@ygreq)](https://github.com/ygreq).
