#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from ncclient import manager
import xml.dom.minidom
from connection_info import host, port , username, password, device_params

if __name__ == '__main__':
    m =  manager.connect(host=host,port=port,username=username,password=password,device_params=device_params)

    # Pretty print the XML reply
    xmlDom = xml.dom.minidom.parseString(str(m.get_config('running')))

    # Write Output to file
    with open("Output\\config.txt", "w") as f:
        f.write(xmlDom.toprettyxml( indent = " " ))

    # Close Netconf Session
    m.close_session()
