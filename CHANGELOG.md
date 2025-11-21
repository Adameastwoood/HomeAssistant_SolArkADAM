# Changelog

All notable changes to this project will be documented in this file.

## [5.0.0] - 2024-11-21

### 🎉 Major Features

- **Energy Dashboard Compatible** - Full support for Home Assistant's Energy dashboard
  - Track solar production with `sensor.solark_energy_total`
  - Monitor grid consumption and export
  - Battery energy tracking support
  - Long-term statistics automatically recorded
  - Cost tracking and energy flow diagrams

### ⚠️ Breaking Changes

- **Entity ID Format Changed**
  - Old: `sensor.solark_plant_pv_power`
  - New: `sensor.solark_pv_power`
  - **Migration Required:** Existing users must remove and re-add the integration
  - **Action Required:** Update all automations, dashboards, and scripts with new entity IDs

### ✨ Improvements

- Added `state_class` attribute to all sensors for statistics tracking
  - Power sensors: `state_class: measurement`
  - Energy sensors: `state_class: total_increasing`
- Battery SOC now uses proper `BATTERY` device class
- Device name simplified from "SolArk Plant" to "SolArk"
- Cleaner, more predictable entity IDs
- Enhanced sensor attributes for better Energy dashboard integration

### 📚 Documentation

- **New:** Complete Energy Dashboard setup guide (ENERGY_DASHBOARD_SETUP.md)
- **New:** Quick Start guide for new users (QUICKSTART.md)
- **Updated:** README with comprehensive troubleshooting and examples
- **Added:** Dashboard YAML configuration examples
- **Added:** Automation and template sensor examples
- **Added:** Energy Dashboard compatibility badge

### 🔧 Technical Changes

- Added `_attr_has_entity_name = True` to sensor entities
- Updated sensor descriptions with proper `state_class` attributes
- Improved entity naming for Home Assistant entity system
- All sensors now properly support long-term statistics

### 🔄 Migration Guide for Existing Users

1. **Backup Configuration**
   - Note your Plant ID and credentials
   - Export any dashboards or automations using SolArk sensors

2. **Remove Old Integration**
   - Go to Settings → Devices & Services
   - Find "SolArk Cloud"
   - Click three dots (⋮) → Delete

3. **Update Integration**
   - Update via HACS or manually install new version
   - Restart Home Assistant

4. **Re-add Integration**
   - Settings → Devices & Services → + ADD INTEGRATION
   - Search "SolArk Cloud"
   - Enter your credentials
   - Sensors created with new entity IDs

5. **Update References**
   - Update automations with new entity IDs
   - Update dashboards
   - Update template sensors

### 📋 Entity ID Mapping

| Old Entity ID | New Entity ID |
|---------------|---------------|
| `sensor.solark_plant_pv_power` | `sensor.solark_pv_power` |
| `sensor.solark_plant_battery_power` | `sensor.solark_battery_power` |
| `sensor.solark_plant_battery_soc` | `sensor.solark_battery_soc` |
| `sensor.solark_plant_grid_power` | `sensor.solark_grid_power` |
| `sensor.solark_plant_load_power` | `sensor.solark_load_power` |
| `sensor.solark_plant_grid_import_power` | `sensor.solark_grid_import_power` |
| `sensor.solark_plant_grid_export_power` | `sensor.solark_grid_export_power` |
| `sensor.solark_plant_energy_today` | `sensor.solark_energy_today` |
| `sensor.solark_plant_energy_total` | `sensor.solark_energy_total` |

---

## [4.x] - Previous Versions

See git history for previous version changes.
