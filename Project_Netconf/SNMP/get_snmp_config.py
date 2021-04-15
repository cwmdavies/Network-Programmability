#!/usr/bin/env python
from ncclient import manager
from lxml import etree
from FILTERS import Get_SNMP_Config

device = manager.connect(host="10.1.1.11", port=830, username="cisco", password="cisco", hostkey_verify=False, device_params={}, allow_agent=False, look_for_keys=False)

nc_get_reply = device.get(("subtree", Get_SNMP_Config))
print(etree.tostring(nc_get_reply.data, pretty_print=True))