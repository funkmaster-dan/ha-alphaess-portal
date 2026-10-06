"""Portal telemetry for the registered ESS device."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from .entity import PortalEntity

SENSORS = [('soc', 'Battery state of charge', '%', SensorDeviceClass.BATTERY), ('battery', 'Battery power', 'W', SensorDeviceClass.POWER), ('grid', 'Grid power', 'W', SensorDeviceClass.POWER), ('load', 'Home load', 'W', SensorDeviceClass.POWER)]

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PortalSensor(entry.runtime_data, item) for item in SENSORS])

class PortalSensor(PortalEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, item):
        super().__init__(coordinator)
        self.key, self._attr_name, self._attr_native_unit_of_measurement, self._attr_device_class = item
        self._attr_unique_id = f"alphaess_portal_{coordinator.entry.data['serial']}_{self.key}"

    @property
    def native_value(self):
        return self.power.get(self.key)
