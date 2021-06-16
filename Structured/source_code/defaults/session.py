from .logging_code import *
import ipaddress
import paramiko
from .gui import *


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
        log.info(f"Open Session Function: Trying to connect to ip Address: {ip}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=22, username=username, password=password)
        log.info(f"Open Session Function: Connected to ip Address: {ip}")
        return ssh, True
    except paramiko.ssh_exception.AuthenticationException:
        log.error(f"Open Session Function:"
                  f"Authentication to ip Address: {ip} failed! Please check your ip, username and password.")
        return None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        log.error(f"Open Session Function Error: Unable to connect to ip Address: {ip}!")
        return None, False
    except (ConnectionError, TimeoutError):
        log.error(f"Open Session Function Error: Timeout error occurred for ip Address: {ip}!")
        return None, False
    except Exception as err:
        log.error(f"Open Session Function Error: Unknown error occurred for ip Address: {ip}!")
        log.error(f"\t Error: {err}")
        return None, False
