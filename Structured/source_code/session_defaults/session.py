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