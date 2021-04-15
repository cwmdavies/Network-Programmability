#!/usr/bin/env python
from ncclient import manager
from FILTERS import Set_SNMP_Community

device = manager.connect(host="10.1.1.11", port=830, username="cisco", password="cisco", hostkey_verify=False, device_params={}, allow_agent=False, look_for_keys=False)
response = device.edit_config(target='running', config=Set_SNMP_Community)