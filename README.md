# SolArk Cloud – Home Assistant Integration

Custom Home Assistant integration for SolArk Cloud using the new OAuth2 API
behind https://www.mysolark.com.

## Installation via HACS

1. In Home Assistant, open **HACS → Integrations**.
2. Click the three dots → **Custom repositories**.
3. Add:

   ```text
   https://github.com/HammondAutomationHub/HomeAssistant_SolArk
   ```

   Category: **Integration**.

4. Install **SolArk Cloud** from HACS.
5. Restart Home Assistant.

Then go to **Settings → Devices & Services → Add Integration** and search for
**SolArk Cloud**. Enter your SolArk username, password, and plant ID.
