###############################################
#            Under Construction               #
#               Design Phase                  #
#                                             #
###############################################

'''


Threading is used to connect to multiple switches at a time. Each IP Address is checked to ensure each IP Address is valid.
'''

import paramiko
import textfsm
from getpass import getpass
from openpyxl import load_workbook, Workbook
import ipaddress
import logging
import sys
import time
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock
import tkinter as tk
from tkinter import ttk

jump_server_address = '10.251.131.6'  # The internal ip Address for the Jump server
local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from
IP_LIST = []
Hostnames_List = []
collection_of_results = []
filename = "CDP_Neighbors_Detail.xlsx"
index = 2
ThreadLock = Lock()


# -----------------------------------------------------------
# --------------- TKinter Configuration Start ---------------

# root window
root = tk.Tk()
root.eval('tk::PlaceWindow . center')
root.geometry("300x300")
root.resizable(False, True)
root.title('Required Details')

# store entries
Username_var = tk.StringVar()
password_var = tk.StringVar()
IP_Address_var = tk.StringVar()
Debugging_var = tk.IntVar()

# Site details frame
Site_details = ttk.Frame(root)
Site_details.pack(padx=10, pady=10, fill='x', expand=True)

# Username
Username_label = ttk.Label(Site_details, text="Username:")
Username_label.pack(fill='x', expand=True)
Username_entry = ttk.Entry(Site_details, textvariable=Username_var)
Username_entry.pack(fill='x', expand=True)
Username_entry.focus()

# Password
password_label = ttk.Label(Site_details, text="Password:")
password_label.pack(fill='x', expand=True)
password_entry = ttk.Entry(Site_details, textvariable=password_var, show="*")
password_entry.pack(fill='x', expand=True)

# ip Address
IP_Address_label = ttk.Label(Site_details, text="IP Address:")
IP_Address_label.pack(fill='x', expand=True)
IP_Address_entry = ttk.Entry(Site_details, textvariable=IP_Address_var)
IP_Address_entry.pack(fill='x', expand=True)

# Debugging
Debugging_label = ttk.Label(Site_details, text="\nDebugging (0 = OFF, 1 = ON):")
Debugging_label.pack(fill='x', expand=True)
Debugging_entry = ttk.Entry(Site_details, textvariable=Debugging_var)
Debugging_entry.pack(fill='x', expand=True)

resultLabel = ttk.Label(Site_details, text="", wraplength=300)
resultLabel.pack(fill='x', expand=True)

# Submit button
Submit_button = ttk.Button(Site_details, text="Submit", command=root.destroy)
Submit_button.pack(fill='x', pady=10)

root.attributes('-topmost', True)
root.mainloop()

username = Username_var.get()
password = password_var.get()
IPAddr = IP_Address_var.get()
Debugging = Debugging_var.get()

# ---------------- TKinter Configuration End ----------------
# -----------------------------------------------------------


# -----------------------------------------------------------
# --------------- Logging Configuration Start ---------------

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





'''
Checks that the IP address is valid.
Returns True or false.
'''
def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


'''
Connected to the IP address through a jump host using SSH.
Returns the SSH session.
'''
def jump_session(ip):
    if not ip_check(ip):
        with ThreadLock:
            log.error(f"open_session function error: "
                      f"ip Address {ip} is not a valid Address. Please check and restart the script!",)
        return None, False
    try:
        with ThreadLock:
            log.info(f"Trying to establish a connection to: {ip}")
        jump_box = paramiko.SSHClient()
        jump_box.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_box.connect(jump_server_address, username=username, password=password)
        jump_box_transport = jump_box.get_transport()
        src_address = (local_IP_address, 22)
        destination_address = (ip, 22)
        jump_box_channel = jump_box_transport.open_channel("direct-tcpip", destination_address, src_address, timeout=4,)
        target = paramiko.SSHClient()
        target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target.connect(destination_address, username=username, password=password, sock=jump_box_channel, timeout=4,
                       auth_timeout=4, banner_timeout=4)
        with ThreadLock:
            log.info(f"Connection to IP: {ip} established")
        return target, jump_box, True
    except paramiko.ssh_exception.AuthenticationException:
        with ThreadLock:
            log.error(f"Authentication to IP: {ip} failed! Please check your ip, username and password.")
        return None, None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        with ThreadLock:
            log.error(f"Unable to connect to IP: {ip}!")
        return None, None, False
    except (ConnectionError, TimeoutError):
        with ThreadLock:
            log.error(f"Connection or Timeout error occurred for IP: {ip}!")
        return None, None, False
    except Exception as err:
        with ThreadLock:
            log.error(f"Open Session Error: An unknown error occurred for IP: {ip}!")
            log.error(f"{err}")
        return None, None, False


'''
Connects to the host's IP Address and runs the 'show cdp neighbors detail'
command and parses the output using TextFSM and saves it to a list of dicts.
Returns None.
'''
def get_cdp_details(ip):
    ssh, jump_box, connection = jump_session(ip)
    if not connection:
        return None
    hostname = get_hostname(ip)
    if hostname not in Hostnames_List:
        Hostnames_List.append(hostname)
        _, stdout, _ = ssh.exec_command("show cdp neighbors detail")
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        with ThreadLock:
            with open("./textfsm/cdp_details.txt") as f:
                re_table = textfsm.TextFSM(f)
                result = re_table.ParseText(stdout)
        result = [dict(zip(re_table.header, entry)) for entry in result]
        for entry in result:
            entry['LOCAL_HOST'] = hostname
            entry['LOCAL_IP'] = ip
            collection_of_results.append(entry)
            if entry["REMOTE_IP"] not in IP_LIST:
                if 'Switch' in entry['CAPABILITIES']:
                    IP_LIST.append(entry["REMOTE_IP"])
    ssh.close()
    jump_box.close()


'''
Connects to the host's IP Address and runs the 'show run | inc hostname'
command and parses the output using TextFSM and saves it to a list.
Returns the Hostname.
'''
def get_hostname(ip):
    ssh, jump_box, connection = jump_session(ip)
    if not connection:
        return None
    _, stdout, _ = ssh.exec_command("show run | inc hostname")
    stdout = stdout.read()
    stdout = stdout.decode("utf-8")
    try:
        with ThreadLock:
            with open("./textfsm/hostname.txt") as f:
                re_table = textfsm.TextFSM(f)
                result = re_table.ParseText(stdout)
                hostname = result[0][0]
    except:
        hostname = "Not Found"
    ssh.close()
    jump_box.close()
    return hostname


'''
Connects to the host's IP Address and runs the 'show interfaces'
command and parses the output using TextFSM and saves it to a list
of dictionaries.
Returns the list.
'''
def get_interfaces(ip):
    ssh, jump_box, connection = jump_session(ip)
    _, stdout, _ = ssh.exec_command("show interfaces")
    stdout = stdout.read()
    stdout = stdout.decode("utf-8")
    with open("cisco_ios_show_interfaces.textfsm") as f:
        re_table = textfsm.TextFSM(f)
        result = re_table.ParseText(stdout)
    results = [dict(zip(re_table.header, entry)) for entry in result]
    ssh.close()
    jump_box.close()
    return results


'''
Connects to the host's IP Address and runs a list of commands
on the switch to rename the interfaces descriptions.
Returns the list.
'''
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
            commands.append(f"interface {df['INTERFACE'][num]}")
            commands.append(f"description {df['DESCRIPTION'][num]}")
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