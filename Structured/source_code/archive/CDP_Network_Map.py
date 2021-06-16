###############################################
#            Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################

import re
import paramiko
import ipaddress
from gui import username, password

IP_list = []
CDP_Info_List = []
debug = 0


def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def open_session(ip):
    if not ip_check(ip):
        return None, False
    try:
        output_log(f"Open Session Function: Trying to connect to ip Address: {ip}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=22, username=username, password=password)
        output_log(f"Open Session Function: Connected to ip Address: {ip}")
        return ssh, True
    except paramiko.ssh_exception.AuthenticationException:
        error_log(f"Open Session Function:"
                  f"Authentication to ip Address: {ip} failed! Please check your ip, username and password.")
        return None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        error_log(f"Open Session Function Error: Unable to connect to ip Address: {ip}!")
        return None, False
    except (ConnectionError, TimeoutError):
        error_log(f"Open Session Function Error: Timeout error occurred for ip Address: {ip}!")
        return None, False
    except Exception as err:
        error_log(f"Open Session Function Error: Unknown error occurred for ip Address: {ip}!")
        error_log(f"\t Error: {err}")
        return None, False


def extract_cdp_neighbors(ip):
    interface_names = []
    command = "sh cdp neighbors"
    regex = r"^.{17}(\b(Ten|Gig|Loo|Vla|F|Twe|Ten|Fo).{15})"
    ssh, connection = open_session(ip)
    if not connection:
        return None
    try:
        output_log(f"Extract CDP Neighbors Function: Extracting Neighbors: ip Address: {ip}")
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        matches = re.finditer(regex, stdout, re.MULTILINE)
        for match in matches:
            temp_interface_name = match.group(1)
            temp_interface_name = temp_interface_name.strip()
            interface_names.append(temp_interface_name)
        output_log(f"Extract CDP Neighbors Function: Extraction Complete: ip Address: {ip}")
        return interface_names
    except paramiko.ssh_exception.SSHException:
        error_log(f"Extract CDP Neighbors Function Error: "
                  f"There is an error connecting or establishing SSH session to ip Address {ip}")
        return None, False
    except Exception as err:
        error_log(f"Extract CDP Neighbors Function Error: An unknown error occurred for ip: {ip}!")
        error_log(f"\t Error: {err}")
        return None, False
    finally:
        ssh.close()


def cdp_details(ip, command, hostname):
    cdp_info = {}
    ssh, connection = open_session(ip)
    if not connection:
        return None
    try:
        output_log(f"CDP Detail Function: Extracting Neighbor Details: ip Address: {ip}")
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")

        remote_host = r"(?=[\n\r].*Device ID:[\s]*([^\n\r]*))"
        platform = r"(?=[\n\r].*Platform:[\s]*([^\n\r]*))"
        interface = r"(?=[\n\r].*Interface:[\s]*([^\n\r]*))"
        remote_ip_ddr = r"(?=[\n\r].*IP Address:[\s]*([^\n\r]*))"
        remote_int = r"(?=[\n\r].*Port ID.*: [\s]*([^\n\r]*))"
        native_vlan = r"(?=[\n\r].*Native VLAN:[\s]*([^\n\r]*))"

        remote_host_match = re.finditer(remote_host, stdout, re.MULTILINE)
        platform_match = re.finditer(platform, stdout, re.MULTILINE)
        interface_match = re.finditer(interface, stdout, re.MULTILINE)
        remote_ip_addr_match = re.finditer(remote_ip_ddr, stdout, re.MULTILINE)
        remote_int_match = re.finditer(remote_int, stdout, re.MULTILINE)
        native_vlan_match = re.finditer(native_vlan, stdout, re.MULTILINE)

        cdp_info["Local Hostname"] = hostname
        cdp_info["Local ip Address"] = ip

        for line in remote_host_match:
            remote_host = line[1].split()
            remote_host = remote_host[0]
            cdp_info["Remote Host"] = remote_host
        for line in platform_match:
            platform = line[1].split(",")
            platform = platform[0].strip(",")
            cdp_info["Platform"] = platform
        for line in interface_match:
            interface = line[1].split()
            interface = interface[0].strip(",")
            cdp_info["Local Interface"] = interface
        for line in remote_ip_addr_match:
            remote_ip_ddr = line[1].split()
            remote_ip_ddr = remote_ip_ddr[0]
            cdp_info["Remote ip Address"] = remote_ip_ddr
        for line in remote_int_match:
            remote_int = line[1].split(":")
            remote_int = remote_int[0]
            cdp_info["Remote Interface"] = remote_int
        for line in native_vlan_match:
            native_vlan = line[1].split()
            native_vlan = native_vlan[0]
            cdp_info["Native VLAN"] = native_vlan
        if remote_ip_ddr not in IP_list:
            IP_list.append(remote_ip_ddr)
        CDP_Info_List.append(cdp_info)
        output_log(f"CDP Detail Function: Extraction Complete: ip Address: {ip}")
    except paramiko.ssh_exception.SSHException:
        error_log(f"CDP Detail Function Error: "
                  f"There is an error connecting or establishing SSH session to ip Address {ip}")
    except Exception as err:
        error_log(f"CDP Details Function Error: An unknown error occurred for ip: {ip}!")
        error_log(f"\t Error: {err}")
        return None, False
    finally:
        ssh.close()


def get_hostname(ip):
    hostname = None
    regex_hostname = r"^\bhostname[\s\r]+(.*)$"
    ssh, connection = open_session(ip)
    if not connection:
        return "-1"
    try:
        output_log(f"Get Hostname Function: Extracting Hostname: IP Address: {ip}")
        stdin, stdout, stderr = ssh.exec_command("show run | i hostname")
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        hostname_matches = re.finditer(regex_hostname, stdout, re.MULTILINE)
        for h in hostname_matches:
            hostname = h.group(1)
        return hostname
    except paramiko.ssh_exception.SSHException:
        error_log(f"Get Hostname Function Error: "
                  f"There is an error connecting or establishing SSH session to ip Address {ip}")
        return None
    except Exception as err:
        error_log(f"Get Hostname Function Error: Unknown error occurred for ip Address: {ip}!")
        error_log(f"\t Error: {err}")
        return None
    finally:
        ssh.close()


def find_ips(ip):
    interface_names = extract_cdp_neighbors(ip)
    hostname = get_hostname(ip)
    if not interface_names:
        return -1
    for name in interface_names:
        command = f"show cdp neighbors {name} detail"
        cdp_details(ip, command, hostname)
