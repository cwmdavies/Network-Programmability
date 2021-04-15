#!/usr/bin/env python3
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

if __name__ == "__main__":
    auth = HTTPBasicAuth('cisco', 'cisco')
    headers = {'Accept': 'application/vnd.yang.data+json',
    'Content-Type': 'application/vnd.yang.data+json'
    }
url = 'http://192.168.37.129/restconf/api/config/native/hostname'
response = requests.get(url, headers=headers, auth=auth)

response = json.loads(response.text)
json_response = json.dumps(response, indent=4)
with open('Outputs\\Hostname.txt', 'w') as f:
    for capability in json_response:
        f.write(str(capability))