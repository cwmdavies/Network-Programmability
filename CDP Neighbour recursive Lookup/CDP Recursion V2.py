###############################################
#                                             #
#             Under Contruction               #
#                                             #
###############################################

import os
import configparser
import re
import time
from multiprocessing.pool import ThreadPool
import paramiko

username = os.getenv("ADM_USER")
password = os.getenv("ADM_PASSWORD")
default_domain_name = "cns.muellergroup.com"
port = "22"

ip_list = []
hostname_list = []
fqdn_list = []
matched_list = []

def open_session(IP):
    try:
        print(f"Connected to:{IP}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=IP, port=port, username=username, password=password)
        return ssh, True
    except paramiko.ssh_exception.AuthenticationException:
        print(f"Authentication to IP:{IP} failed! Please check your IP, username and password.")
        return None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"Unable to connect to IP:{IP}")
        return None, False
    except (ConnectionError, TimeoutError):
        print(f"Timeout error occured for IP:{IP}!")
        return None, False

def extract_cdp_neighbors(ip):
    interface_names = []
    command = "show cdp neighbors"
    regex = r"^.{17}(\b(Ten|Gig|Loo|Vla|F).{15})"
    ssh, connection = open_session(ip)
    if not connection:
        return None
    try:
        _, output, _ = ssh.exec_command(command)
        output = output.read()
        output = output.decode("utf-8")
        matches = re.finditer(regex, output, re.MULTILINE)
        for match in matches:
            temp_interface_name = match.group(1)
            temp_interface_name = temp_interface_name.strip()
            interface_names.append(temp_interface_name)
        return interface_names
    except paramiko.ssh_exception.SSHException:
        print(
            "Extract CDP Neighbor Function Error: There is an error connecting or establishing SSH session"
        )
        return None
    finally:
        ssh.close()

def neighbor_detail(ip, commands):
    formatted_commands = []
    global ip_list
    regex = r"(?=[\n\r].*IP address:[\s]*([^\n\r]*))"
    ssh, connection = open_session(ip)
    if not connection:
        return None
    try:
        channel = ssh.invoke_shell()
        stdin = channel.makefile("wb")
        output = channel.makefile("rb")
        formatted_commands.append("'''")
        for c in commands:
            formatted_commands.append(c)
        formatted_commands.append("'''")
        formatted_commands = "\n".join(formatted_commands)
        stdin.write(str.encode(formatted_commands))
        output = output.read()
        output = output.decode("utf-8")
        stdin.close()
        matches = re.finditer(regex, output, re.MULTILINE)
        i = 1
        for match in matches:
            if match.group(i):
                found_ip = match.group(i)
                if found_ip not in ip_list:
                    ip_list.append(found_ip)
    except paramiko.ssh_exception.SSHException:
        print(
            "Neighbor Detail Function Error: There is an error connecting or establishing SSH session"
        )
    finally:
        ssh.close()