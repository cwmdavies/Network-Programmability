###############################################
#             Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################
#
#   A simple script that parses the output 
#   of the "show interface descriptions"
#   command and writes it in a neat format
#   to an excel spreadsheet.

import paramiko
from logging_code import *
import re
import ipaddress
from gui import username, password, IP_Address
import pandas as pd

jump_server_address = '10.251.6.31'   # The internal ip Address for the Jump server
local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from
interfaces = list()
df = pd.read_excel(r'Interfaces.xlsx')


def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def open_session(ip):
    if not ip_check(ip):
        log.error(f"open_session function error: "
                  f"ip Address {ip} is not a valid Address. Please check and restart the script!",)
        return None, False
    try:
        log.info(f"Trying to establish a connection to: {ip}")
        jump_box = paramiko.SSHClient()
        jump_box.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_box.connect(jump_server_address, username=username, password=password)
        jump_box_transport = jump_box.get_transport()
        src_address = (local_IP_address, 22)
        destination_address = (ip, 22)
        jump_box_channel = jump_box_transport.open_channel("direct-tcpip", destination_address, src_address)
        target = paramiko.SSHClient()
        target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target.connect(destination_address, username=username, password=password, sock=jump_box_channel)
        log.info(f"Connection to ip: {ip} established")
        return target, jump_box, True
    except paramiko.ssh_exception.AuthenticationException:
        log.error(f"Authentication to ip: {ip} failed! Please check your ip, username and password.")
        return None, None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        log.error(f"Unable to connect to ip: {ip}!")
        return None, None, False
    except (ConnectionError, TimeoutError):
        log.error(f"Timeout error occurred for ip: {ip}!")
        return None, None, False
    except Exception as err:
        log.error(f"Open Session Error: An unknown error occurred for ip: {ip}!")
        log.error(f"\t Error: {err}")
        return None, None, False


def get_interfaces(ip):
    interface_names = list()
    ssh, jump_box, connection = open_session(ip)
    if not connection:
        return None
    try:
        log.info(f"retrieving list of interfaces from ip Address: {ip}")
        _, stdout, _ = ssh.exec_command("show ip interface brief")
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        regex = r"^(\b(Ten|Gig|Loo|Vla|Fas|Twe|Ten|Fo).{20})"
        matches = re.finditer(regex, stdout, re.MULTILINE)
        for match in matches:
            temp_interface_name = match.group(1)
            temp_interface_name = temp_interface_name.strip()
            interface_names.append(temp_interface_name)
        log.info(f"List retrieval successful for ip Address: {ip}")
        return interface_names
    except paramiko.ssh_exception.AuthenticationException:
        log.error(f"Interfaces function Error: Authentication to ip: "
                  f"{ip} failed! Please check your ip, username and password.")
        return None
    except paramiko.ssh_exception.NoValidConnectionsError:
        log.error(f"Interfaces function Error: Unable to connect to ip: {ip}!")
        return None
    except (ConnectionError, TimeoutError):
        log.error(f"Interfaces function Error: Timeout error occurred for ip: {ip}!")
        return None
    except Exception as err:
        log.error(f"Interfaces function Error: An unknown error occurred for ip: {ip}!")
        log.error(f"\t Error: {err}")
        return None
    finally:
        ssh.close()
        jump_box.close()


def get_int_description(int_name):
    global interfaces
    interfaces_dict = dict()
    command = f"show run interface {int_name} | inc description"
    ssh, jump_box, connection = open_session(IP_Address)
    if not connection:
        log.error(f"get_int_description - Function Error: No connection is available for ip: {IP_Address}!")
    try:
        log.info(f"retrieving interface description for interface: {int_name}")
        _, stdout, _ = ssh.exec_command(command)
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        int_description = re.search(".*description.*", stdout)
        int_description = int_description[0]
        int_description = int_description.strip()
        int_description = int_description.strip("description")
        interfaces_dict["Interface"] = int_name
        interfaces_dict["Description"] = int_description
        log.info(f"Description retrieval successful for interface: {int_name}")
    except TypeError:
        interfaces_dict["Interface"] = int_name
        interfaces_dict["Description"] = "No Description found"
    except paramiko.ssh_exception.SSHException:
        log.error(f"get_int_description - Function Error: "
                  f"There is an error connecting or establishing SSH session to ip Address {IP_Address}")
    except Exception as err:
        log.error(f"get_int_description - Function Error: An unknown error occurred for ip: {IP_Address}, "
                  f"on Interface: {int_name}!")
        log.error(f"\t Error: {err}")
    finally:
        interfaces.append(interfaces_dict)
        ssh.close()
        jump_box.close()


def int_write(ip):
    commands = []
    ssh, jump_box, connection = open_session(ip)
    if not connection:
        return None
    try:
        log.info(f"int_write function: Preparing to writing interface descriptions.")
        channel = ssh.invoke_shell()
        stdin = channel.makefile("wb")
        output = channel.makefile("rb")
        commands.append("'''")
        commands.append("conf t")
        for num in range(len(df)):
            commands.append(f"interface {df['Interface'][num]}")
            commands.append(f"description {df['Description'][num]}")
        commands.append("end")
        commands.append("exit")
        commands.append("'''")
        commands = "\n".join(commands)
        stdin.write(str.encode(commands))
        output = output.read()
        output = output.decode("utf-8")
        log.info(f"Output:\n\t{output}")
        stdin.close()
        log.info(f"int_write function: Finished writing interface descriptions.")
    except Exception as err:
        log.error(f"Int_write function Error: An unknown error occurred!")
        log.error(f"\t Error: {err}")
    finally:
        ssh.close()
        jump_box.close()