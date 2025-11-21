# SolArk Cloud Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/HammondAutomationHub/HomeAssistant_SolArk.svg)](https://github.com/HammondAutomationHub/HomeAssistant_SolArk/releases)
[![Energy Dashboard](https://img.shields.io/badge/Energy%20Dashboard-Compatible-green.svg)](https://www.home-assistant.io/home-energy-management/)

A Home Assistant custom integration for Sol-Ark inverter systems that connects to the SolArk Cloud API. Monitor your solar system with real-time data and track long-term energy production with full Energy Dashboard support.

## 🌟 Key Features

- **Energy Dashboard Compatible** - Native support for Home Assistant's Energy dashboard
- **Real-time Monitoring** - Live power flow tracking (PV, Battery, Grid, Load)
- **Cloud-based** - No physical connections required
- **9 Comprehensive Sensors** - All critical solar system metrics
- **Beautiful Dashboards** - Pre-built power flow visualizations
- **Long-term Statistics** - Automatic energy tracking and historical data
- **Easy Setup** - Simple configuration through Home Assistant UI

## 📊 Sensors Provided

| Entity ID | Description | Unit | Energy Dashboard |
|-----------|-------------|------|------------------|
| `sensor.solark_pv_power` | Solar panel power | W | Use with Riemann Sum |
| `sensor.solark_battery_power` | Battery charge/discharge | W | Use with Riemann Sum |
| `sensor.solark_battery_soc` | Battery state of charge | % | Battery level |
| `sensor.solark_grid_power` | Net grid power | W | Use with Riemann Sum |
| `sensor.solark_load_power` | Home consumption | W | Use with Riemann Sum |
| `sensor.solark_grid_import_power` | Grid import | W | Use with Riemann Sum |
| `sensor.solark_grid_export_power` | Grid export | W | Use with Riemann Sum |
| `sensor.solark_energy_today` | Daily production | kWh | ✅ Direct use |
| `sensor.solark_energy_total` | Lifetime production | kWh | ✅ Solar production |

**Note:** Battery power: positive = discharging, negative = charging

## 📋 Requirements

- Home Assistant 2023.5.0 or newer
- Sol-Ark inverter (12K, 15K, 8K, 5K models)
- Active Sol-Ark Cloud account
- Your Plant ID from Sol-Ark portal

## 🚀 Installation

### Via HACS (Recommended)

1. Open **HACS** → **Integrations**
2. Click **⋮** → **Custom repositories**
3. Add: `https://github.com/HammondAutomationHub/HomeAssistant_SolArk`
4. Category: **Integration**
5. Find "SolArk Cloud" and click **Download**
6. Restart Home Assistant

### Manual Installation

1. Download latest release
2. Copy `custom_components/solark` to your `/config/custom_components/` directory
3. Restart Home Assistant

## ⚙️ Configuration

### 1. Get Your Plant ID

1. Log into [mysolark.com](https://www.mysolark.com)
2. Navigate to your system
3. Check the URL: `https://www.mysolark.com/plant/12345`
4. Your Plant ID is `12345`

### 2. Add Integration

1. **Settings** → **Devices & Services** → **+ ADD INTEGRATION**
2. Search "SolArk Cloud"
3. Enter:
   - **Username**: Your Sol-Ark email
   - **Password**: Your Sol-Ark password
   - **Plant ID**: From step 1
   - **Scan Interval**: 30 (seconds)
4. Click **SUBMIT**

### 3. Verify

- Go to **Developer Tools** → **States**
- Search `solark`
- Verify 9 sensors with live data

## ⚡ Energy Dashboard Setup

Your integration is fully compatible with Home Assistant's Energy dashboard!

### Quick Setup

1. **Settings** → **Dashboards** → **Energy**
2. **Solar Production** → Add Production
   - Select: `sensor.solark_energy_total`
3. **Grid Consumption** (requires helpers):
   - Create Riemann Sum helper from `sensor.solark_grid_import_power`
   - Add to Energy dashboard
4. **Grid Return** (if you export):
   - Create Riemann Sum helper from `sensor.solark_grid_export_power`
   - Add to Energy dashboard

**📚 Full Guide:** See [ENERGY_DASHBOARD_SETUP.md](ENERGY_DASHBOARD_SETUP.md) for complete instructions including battery tracking.

## 📱 Dashboard Examples

### Power Flow Dashboard

Beautiful real-time monitoring with dynamic power flow indicators:

**Features:**
- Live power values with color coding
- Battery status with dynamic icons
- 24-hour historical charts
- Energy production statistics

**Requirements:**
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) (HACS)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) (HACS)

**Installation:**

**Option A - UI Method:**
1. Copy `dashboards/solark_flow.yaml` content
2. **Settings** → **Dashboards** → **+ ADD DASHBOARD**
3. **⋮** → **Edit Dashboard** → **⋮** → **Raw configuration editor**
4. Paste and save

**Option B - YAML File:**
1. Copy `solark_flow.yaml` to `/config/dashboards/`
2. Add to `configuration.yaml`:
```yaml
lovelace:
  mode: storage
  dashboards:
    solark-power:
      mode: yaml
      title: SolArk Power Flow
      icon: mdi:solar-power
      show_in_sidebar: true
      filename: dashboards/solark_flow.yaml
```
3. Restart Home Assistant

## 🤖 Automation Examples

### Low Battery Alert
```yaml
automation:
  - alias: "Low Battery Warning"
    trigger:
      platform: numeric_state
      entity_id: sensor.solark_battery_soc
      below: 20
    action:
      service: notify.mobile_app
      data:
        title: "Low Battery"
        message: "Battery at {{ states('sensor.solark_battery_soc') }}%"
```

### Excess Solar Notification
```yaml
automation:
  - alias: "Exporting to Grid"
    trigger:
      platform: numeric_state
      entity_id: sensor.solark_grid_export_power
      above: 2000
      for: "00:05:00"
    action:
      service: notify.mobile_app
      data:
        message: "Exporting {{ states('sensor.solark_grid_export_power') }}W"
```

### Battery Full Alert
```yaml
automation:
  - alias: "Battery Fully Charged"
    trigger:
      platform: numeric_state
      entity_id: sensor.solark_battery_soc
      above: 95
    condition:
      condition: numeric_state
      entity_id: sensor.solark_battery_power
      below: 100
    action:
      service: notify.mobile_app
      data:
        message: "Battery full at {{ states('sensor.solark_battery_soc') }}%"
```

## 📐 Template Sensors

### Self-Consumption Percentage
```yaml
template:
  - sensor:
      - name: "Solar Self-Consumption"
        unit_of_measurement: "%"
        state: >
          {% set pv = states('sensor.solark_pv_power') | float(0) %}
          {% set export = states('sensor.solark_grid_export_power') | float(0) %}
          {% if pv > 0 %}
            {{ ((pv - export) / pv * 100) | round(1) }}
          {% else %}
            0
          {% endif %}
```

### Battery Status Text
```yaml
template:
  - sensor:
      - name: "Battery Status"
        state: >
          {% set power = states('sensor.solark_battery_power') | float(0) %}
          {% if power > 100 %}
            Discharging
          {% elif power < -100 %}
            Charging
          {% else %}
            Idle
          {% endif %}
```

## 🔧 Troubleshooting

### Integration Won't Connect
- Verify credentials at mysolark.com
- Confirm Plant ID is correct
- Check logs: **Settings** → **System** → **Logs**

### Sensors Show "Unavailable"
- Check SolArk Cloud service status
- Increase scan interval to 60 seconds
- Reload integration
- Check debug log: `/config/custom_components/solark/solark_debug.log`

### Dashboard Shows Blank
1. Verify sensors exist: **Developer Tools** → **States**
2. Install Mushroom Cards and ApexCharts Card
3. Restart Home Assistant
4. Clear browser cache (Ctrl+Shift+R)

### Energy Dashboard Issues
- Wait 1-2 hours for statistics to build
- Verify `sensor.solark_energy_total` has data
- Check sensor has `state_class: total_increasing`
- See [ENERGY_DASHBOARD_SETUP.md](ENERGY_DASHBOARD_SETUP.md)

### Enable Debug Logging
```yaml
# configuration.yaml
logger:
  logs:
    custom_components.solark: debug
```

Then check **Settings** → **System** → **Logs**

## 🏗️ Technical Details

### Architecture
- Uses `DataUpdateCoordinator` for efficient polling
- OAuth 2.0 authentication with auto-refresh
- Combines data from two API endpoints:
  - Energy flow: `/api/v1/plant/energy/{plant_id}/flow`
  - Live data: `/api/v1/dy/store/{sn}/read`

### Statistics Support
- Power sensors: `state_class: measurement`
- Energy sensors: `state_class: total_increasing`
- Long-term statistics automatically recorded
- Compatible with Energy dashboard

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/HammondAutomationHub/HomeAssistant_SolArk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HammondAutomationHub/HomeAssistant_SolArk/discussions)
- **Community**: [Home Assistant Forums](https://community.home-assistant.io/)

## 📄 License

Provided as-is with no warranty. Use at your own risk.

## 🙏 Acknowledgments

- Home Assistant community
- Sol-Ark for API access
- All contributors

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Note:** Not officially affiliated with Sol-Ark. Community-developed integration.

**Version:** 5.0.0 | **Supports:** Sol-Ark 5K/8K/12K/15K | **HA:** 2023.5.0+
