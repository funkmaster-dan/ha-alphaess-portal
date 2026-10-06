"""Force discharge with explicit, renewable expiry."""
from aiohttp import ClientError
from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import HomeAssistantError
from .entity import PortalEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DischargeSwitch(entry.runtime_data)])

class DischargeSwitch(PortalEntity, SwitchEntity):
    _attr_name = 'AlphaESS Portal Force Discharge'
    _attr_icon = 'mdi:battery-arrow-down'

    def __init__(self, coordinator):
        super().__init__(coordinator)
        # Preserve the original switch's identity and existing automations.
        self._attr_unique_id = 'alphaess_portal_' + coordinator.entry.data['serial'] + '_force_discharge'

    @property
    def is_on(self):
        return (self.power.get('dispatch') or {}).get('source') == 'IMMEDIATE_DISCHARGE'

    @property
    def available(self):
        return super().available and self.coordinator.data.get('status') == 'Normal'

    @property
    def extra_state_attributes(self):
        dispatch = self.power.get('dispatch') or {}
        return {'battery_soc': self.power.get('soc'), 'battery_power_w': self.power.get('battery'), 'grid_power_w': self.power.get('grid'), 'dispatch_source': dispatch.get('source'), 'power_limit_kw': dispatch.get('powerLimitKw'), 'requested_power_w': self.coordinator.setting('power_w'), 'target_soc': self.coordinator.setting('target_soc'), 'expiry_minutes': self.coordinator.setting('duration_minutes'), 'observed_at': self.power.get('observedAt')}

    async def async_turn_on(self, **kwargs):
        try:
            await self.coordinator.client.discharge(power=self.coordinator.setting('power_w'), target_soc=self.coordinator.setting('target_soc'), duration=self.coordinator.setting('duration_minutes'))
        except (RuntimeError, ClientError, TimeoutError) as exc:
            raise HomeAssistantError('AlphaESS portal could not start discharge') from exc
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        try:
            await self.coordinator.client.stop()
        except (RuntimeError, ClientError, TimeoutError) as exc:
            raise HomeAssistantError('AlphaESS portal could not stop discharge') from exc
        await self.coordinator.async_request_refresh()
