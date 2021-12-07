###############################################
#             Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################
#
#   A simple script that parses the output of
#   an excel spreadsheet for interface names
#   and descriptions and writes them to a switch
#   of your choice.

import paramiko
import datetime as time
from getpass import getpass
import pandas as pd
import time
import ipaddress

debug = 0

jump_server_address = '10.251.6.31'   # The internal ip Address for the Jump server
local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from
username = input("Please enter your username: ")
password = getpass("Please enter your password: ")
IP_Address = input("Please enter an ip Address: ")

df = pd.read_excel(r'Interface Details.xlsx')

# ---------------------------------------------------------
# -------------- Logging Configuration Start --------------

# Log file location
logfile = 'debug.log'
# Define the log format
log_format = (
    '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

# Define basic configuration
if Debugging == 0:
    logging.basicConfig(
        # Define logging level
        level=logging.INFO,
        # Declare the object we created to format the log messages
        format=log_format,
        # Declare handlers
        handlers=[
            logging.FileHandler(logfile),
            logging.StreamHandler(sys.stdout),
        ]
    )
elif Debugging == 1:
    logging.basicConfig(
        # Define logging level
        level=logging.DEBUG,
        # Declare the object we created to format the log messages
        format=log_format,
        # Declare handlers
        handlers=[
            logging.FileHandler(logfile),
            logging.StreamHandler(sys.stdout),
        ]
    )

# Define your own logger name
log = logging.getLogger(__name__)

# --------------- Logging Configuration End ---------------
# ---------------------------------------------------------


# Takes in an IP address and checks that it is valid.
def ip_check(ip) -> Bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


# Takes in an IP address and connects to it through a jump host using SSH.
def open_session(ip) -> SSH_Session:
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


# Takes in an IP Address, connects to it, parses the panda data frame to construct the interface description commands
# and issues them to the host.
def int_write(ip) -> None:
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
            commands.append(f"interface {df['INTERFACE'][num]}")
            commands.append(f"description {df['DESCRIPTION'][num]}")
        commands.append("end")
        commands.append("exit")
        commands.append("'''")
        commands = "\n".join(commands)
        stdin.write(str.encode(commands))
        output = output.read()
        output = output.decode("utf-8")
        output_log(f"Output:\n\t{output}")
        stdin.close()
        log.info(f"int_write function: Finished writing interface descriptions.")
    except Exception as err:
        log.error(f"Int_write function Error: An unknown error occurred!")
        log.error(f"\t Error: {err}")
    finally:
        ssh.close()
        jump_box.close()


# Main function that brings everything together.
def main() -> None:
    start = time.perf_counter()

    int_write(IP_Address)

    end = time.perf_counter()
    log.info(f"{end - start:0.4f} seconds")


if __name__ == "__main__":
    main()
