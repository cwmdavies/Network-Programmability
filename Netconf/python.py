#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader, Template
import yaml

ENV = Environment(loader=FileSystemLoader('Git\\Projects\\Project_Netconf\\Jinja_Files'))

template = ENV.get_template('template.j2')

with open('Git\\Projects\\Project_Netconf\\Yaml_Files\\data.yml') as f:
    interfaces = yaml.load(f)
    print(template.render(interface_list=interfaces))