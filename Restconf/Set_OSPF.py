#!/usr/bin/env python
import json
import yaml
import requests
from requests.auth import HTTPBasicAuth

if __name__ == "__main__":
    auth = HTTPBasicAuth('cisco', 'cisco')
    headers = {'Accept': 'application/vnd.yang.data+json',
    'Content-Type': 'application/vnd.yang.data+json'
    }
url = 'http://10.1.1.11/restconf/api/config/native/router'

ospf_config = yaml.load(open('Projects/Project_Restconf/Yaml_Files/ospf-config.yml'))

ospf_object_to_send = {
    "ned:router": ospf_config
}

response = requests.put(url, data=json.dumps(ospf_object_to_send), headers=headers, auth=auth)
print(response.status_code)