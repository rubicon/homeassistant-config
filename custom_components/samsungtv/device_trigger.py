"""Provides device automations for Samsung TV."""
from typing import List
import voluptuous as vol

from homeassistant.const import (
    CONF_DOMAIN,
    CONF_TYPE,
    CONF_PLATFORM,
    CONF_DEVICE_ID,
    CONF_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant, CALLBACK_TYPE
from homeassistant.helpers import entity_registry
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.automation import state, AutomationActionType
from homeassistant.components.device_automation import TRIGGER_BASE_SCHEMA
from . import DOMAIN, LOGGER

TRIGGER_TYPES = {"turned_on", "turned_off"}

TRIGGER_SCHEMA = TRIGGER_BASE_SCHEMA.extend(
    {vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES)}
)


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> List[dict]:
    """List device triggers for Samsung TV devices."""
    registry = await entity_registry.async_get_registry(hass)
    triggers = []

    # Get all the integrations entities for this device
    LOGGER.error(f"device_id:{device_id}")
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        LOGGER.error(f"entry:{entry} device_id:{device_id}")
        if entry.domain != DOMAIN:
            continue

        # Add triggers for each entity that belongs to this integration
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turned_on",
            }
        )
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turned_off",
            }
        )

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: AutomationActionType,
    automation_info: dict,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    config = TRIGGER_SCHEMA(config)

    if config[CONF_TYPE] == "turned_on":
        from_state = STATE_OFF
        to_state = STATE_ON
    else:
        from_state = STATE_ON
        to_state = STATE_OFF

    return state.async_attach_trigger(
        hass,
        {
            CONF_ENTITY_ID: config[CONF_ENTITY_ID],
            state.CONF_FROM: from_state,
            state.CONF_TO: to_state,
        },
        action,
        automation_info,
        platform_type="device",
    )