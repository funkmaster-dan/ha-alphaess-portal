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
- **Discharge duration**: command expiry in minutes; default five minutes.
- **Battery SoC, battery power, grid power and home load sensors**, refreshed every 30 seconds.

Change settings with the number entities or the integration's **Configure** menu. Settings persist in Home Assistant and apply to the next start/renewal; changing a setting alone does not start discharge. Power requests remain subject to inverter and battery limits. Without solar, household consumption reduces net grid export. Grid power is positive for import and negative for export; battery power is positive for discharge.

Calling `switch.turn_on` again renews the command. If Home Assistant stops renewing, the inverter's timed command expires. Changing the default duration also changes that timeout. Unloading/restarting the integration leaves an existing command to expire; it does not issue a battery command by itself.

## Middle-forecast automation

[examples/middle_forecast_export.yaml](examples/middle_forecast_export.yaml) connects this control to the independent [Evening Energy surplus integration](https://github.com/funkmaster-dan/ha-energy-excess). It renews discharge each minute during the forecast peak, and stops when forecasts are stale, surplus is low, SoC reaches 5%, or the peak ends. Keep the five-minute expiry for this example. Its switch entity ID is the default for a first device; adjust it if you rename the entity or configure several inverters.

The forecasting integration is optional. Any automation can use the switch with ordinary `switch.turn_on` / `switch.turn_off` actions.

## Migration from the local experiment

The integration keeps the `alphaess_portal` domain and original force-discharge unique ID, preserving the existing switch and automations. If the earlier `alphaess_portal:` YAML configuration and `/config/alphaess_portal.json` file are present, it imports them once into a normal config entry. After confirming setup, remove that YAML line and private file. New installations need neither.

Account credentials are stored in Home Assistant's normal config-entry storage, not in this repository. Expired sessions refresh automatically; rejected credentials trigger Home Assistant's reauthentication flow.

## API

This uses the owner's authenticated **private portal interface**, separate from the periodic discharge schedules in the public OpenAPI integration. It has no affiliation with AlphaESS. Portal changes may require an update. Authentication and device discovery are read-only; physical commands are sent only when the discharge switch is operated.
