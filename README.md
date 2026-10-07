# AlphaESS Portal Export for Home Assistant

A HACS custom integration for the AlphaESS portal Dashboard's **Discharge now** control. It requests forced battery discharge so surplus power exports to the grid, without local Modbus hardware or an AlphaESS OpenAPI application key.

## Install

1. In **HACS → Custom repositories**, add `https://github.com/funkmaster-dan/ha-alphaess-portal` with category **Integration**.
2. Download **AlphaESS Portal Export** and restart Home Assistant.
3. In **Settings → Devices & services → Add integration**, select **AlphaESS Portal Export**.
4. Enter your AlphaESS portal email, password and inverter serial number.

Requires Home Assistant 2025.1 or later, a portal account with access to the inverter and its immediate-discharge control, and an online inverter. Regional API discovery is automatic. The implementation has been used with the AU portal and a SMILE-G3-B5; other hardware and regions have not been checked.

## Controls

A registered AlphaESS device provides:

- **Force Discharge switch**: on starts or renews a timed discharge; off cancels it and releases the override back to normal operation.
- **Discharge power**: requested battery output in watts; default 5,000 W.
- **Target state of charge**: stops at the selected SoC; minimum/default 5%, matching the portal UI.
- **Discharge duration**: discharge duration in minutes; default five minutes.

This integration creates **no telemetry sensors**. Use your existing AlphaESS integration for SoC, battery/grid power and home load.

Change settings with the number entities or the integration's **Configure** menu. Settings persist in Home Assistant and apply to the next start/renewal; changing a setting alone does not start discharge. Power requests remain subject to inverter and battery limits. Without solar, household consumption reduces net grid export.

Calling `switch.turn_on` again starts or renews discharge using the configured **Discharge duration**. The portal ends the run when that duration completes. There is one duration setting, sent directly as the portal request’s `duration` field; the integration adds no separate expiry setting or discharge timer. Unloading/restarting the integration does not issue a battery command by itself.

## Managed polling

The integration reads dispatch status to confirm the switch state. Polling defaults are:

| Situation | Status polling |
| --- | --- |
| Force discharge active | Every 30 seconds |
| Force discharge off | Every 5 minutes |
| Immediately after a start/stop command | Requests a status refresh; stays on the active rate briefly for confirmation |
| API failures | Backs off up to 15 minutes; idle retries never become faster than the idle interval |
| HTTP 429 | Honors numeric `Retry-After`, including blocking further portal requests during that cooldown |

Both normal intervals are configurable through the integration's **Configure** menu. Defaults reduce idle background status requests from 2,880 to 288 per day (90%). Authentication/session refresh and device discovery add occasional requests; explicit control commands and their confirmation reads are additional. The per-minute renewal automation still sends its intended control requests while discharge is active.

Polling verifies control state; it does not renew discharge. The portal uses the configured discharge duration; status polling does not extend it. No status poll issues a battery command. External portal changes can take up to the idle interval to appear in HA. A rejected login still triggers reauthentication.

Upgrading from v0.2.x removes the four old Portal telemetry sensor registry entries and redundant SoC/power switch attributes. The force-discharge switch and three setting entities keep their identities. Automations that used the removed telemetry must use their existing monitoring integration instead. The included example uses a separate SoC entity and no longer depends on a three-minute Portal telemetry timestamp, which would conflict with idle polling.

## Middle-forecast automation

[examples/middle_forecast_export.yaml](examples/middle_forecast_export.yaml) connects this control to the independent [Evening Energy surplus integration](https://github.com/funkmaster-dan/ha-energy-excess). It renews discharge each minute during the forecast peak, and stops when forecasts are stale, surplus is low, SoC reaches 5%, or the peak ends. Set its `battery_soc` variable to the SoC entity from your existing integration. Choose a discharge duration suitable for its per-minute renewal cadence (the default is five minutes). Unchanged SoC values remain valid while HA reports the entity available. Its switch entity ID is the default for a first device; adjust it if you rename the entity or configure several inverters.

The forecasting integration is optional. Any automation can use the switch with ordinary `switch.turn_on` / `switch.turn_off` actions.

## Migration from the local experiment

The integration keeps the `alphaess_portal` domain and original force-discharge unique ID, preserving the existing switch and automations. If the earlier `alphaess_portal:` YAML configuration and `/config/alphaess_portal.json` file are present, it imports them once into a normal config entry. After confirming setup, remove that YAML line and private file. New installations need neither.

Account credentials are stored in Home Assistant's normal config-entry storage, not in this repository. Expired sessions refresh automatically; rejected credentials trigger Home Assistant's reauthentication flow.

## API

This uses the owner's authenticated **private portal interface**, separate from the periodic discharge schedules in the public OpenAPI integration. It has no affiliation with AlphaESS. Portal changes may require an update. Authentication and device discovery are read-only; physical commands are sent only when the discharge switch is operated.
