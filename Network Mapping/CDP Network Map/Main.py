###############################################
#            Under Construction               #
#               Design Phase                  #
#                                             #
###############################################

"""
A script that takes in an IP Address, two can be supplied if there are two core switches, and run the
"Show CDP Neighbors Detail" command and saves it to a numpy array. This information is then used to rewrite
the interface descriptions to ensure each is correct. A an excel spreadsheet is used to collect the information
of the interfaces that were amended.

Threading is used to connect to multiple switches at a time.
Each IP Address is checked to ensure each IP Address is valid.
"""

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
import pandas as np
from os.path import exists

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
root.geometry("300x350")
root.resizable(False, True)
root.title('Required Details')

# store entries
Username_var = tk.StringVar()
password_var = tk.StringVar()
IP_Address1_var = tk.StringVar()
IP_Address2_var = tk.StringVar()
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
password_label = ttk.Label(Site_details, text="\nPassword:")
password_label.pack(fill='x', expand=True)
password_entry = ttk.Entry(Site_details, textvariable=password_var, show="*")
password_entry.pack(fill='x', expand=True)

# ip Address 1
IP_Address1_label = ttk.Label(Site_details, text="\nCore Switch 1:")
IP_Address1_label.pack(fill='x', expand=True)
IP_Address1_entry = ttk.Entry(Site_details, textvariable=IP_Address1_var)
IP_Address1_entry.pack(fill='x', expand=True)

# ip Address 2
IP_Address2_label = ttk.Label(Site_details, text="\nCore Switch 2 (Optional):")
IP_Address2_label.pack(fill='x', expand=True)
IP_Address2_entry = ttk.Entry(Site_details, textvariable=IP_Address2_var)
IP_Address2_entry.pack(fill='x', expand=True)

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
IPAddr1 = IP_Address1_var.get()
IPAddr2 = IP_Address2_var.get()
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


# Checks that the IP address is valid.
# Returns True or false.
def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


# Connected to the IP address through a jump host using SSH.
# Returns the SSH session.
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


# Connects to the host's IP Address and runs the 'show cdp neighbors detail'
# command and parses the output using TextFSM and saves it to a list of dicts.
# Returns None.
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
            with open("./TextFSM/cisco_ios_show_cdp_neighbors_detail.textfsm") as f:
                re_table = textfsm.TextFSM(f)
                result = re_table.ParseText(stdout)
        result = [dict(zip(re_table.header, entry)) for entry in result]
        for entry in result:
            entry['LOCAL_HOST'] = hostname.upper()
            entry['LOCAL_IP'] = ip
            entry['DESTINATION_HOST'] = entry['DESTINATION_HOST'].replace(".cns.muellergroup.com", "").upper()
            collection_of_results.append(entry)
            if entry["MANAGEMENT_IP"] not in IP_LIST:
                if 'Switch' in entry['CAPABILITIES']:
                    IP_LIST.append(entry["MANAGEMENT_IP"])
    ssh.close()
    jump_box.close()


# Connects to the host's IP Address and runs the 'show run | inc hostname'
# command and parses the output using TextFSM and saves it to a list.
# Returns the Hostname.
def get_hostname(ip):
    ssh, jump_box, connection = jump_session(ip)
    if not connection:
        return None
    _, stdout, _ = ssh.exec_command("show run | inc hostname")
    stdout = stdout.read()
    stdout = stdout.decode("utf-8")
    try:
        with ThreadLock:
            with open("./textfsm/hostname.textfsm") as f:
                re_table = textfsm.TextFSM(f)
                result = re_table.ParseText(stdout)
                hostname = result[0][0]
    except:
        hostname = "Not Found"
    ssh.close()
    jump_box.close()
    return hostname


'''
Connects to the host's IP Address and runs a list of commands
on the switch to rename the interfaces descriptions.
Returns the list.
'''


def main():
    # Start timer.
    start = time.perf_counter()

    # Define amount of threads.
    thread_count = 10
    pool = ThreadPool(thread_count)

    # Added IP Addresses to the list if they exist, if not log an error.
    IP_LIST.append(IPAddr1) if ip_check(IPAddr1) else log.error(
        "No valid IP Address was found. Please check and try again")
    IP_LIST.append(IPAddr2) if ip_check(IPAddr2) else log.info(
        "No valid IP Address was found.")

    # Start the CDP recursive lookup on the network and save the results.
    i = 0
    while i < len(IP_LIST):
        limit = i + min(thread_count, (len(IP_LIST) - i))
        ip_addresses = IP_LIST[i:limit]

        pool.map(get_cdp_details, ip_addresses)

        i = limit

    # Close off and join the pools together.
    pool.close()
    pool.join()

    array = np.DataFrame(collection_of_results, columns=["LOCAL_HOST",
                                                         "LOCAL_IP",
                                                         "LOCAL_PORT",
                                                         "DESTINATION_HOST",
                                                         "REMOTE_PORT",
                                                         "MANAGEMENT_IP",
                                                         "PLATFORM",
                                                         "SOFTWARE_VERSION",
                                                         "CAPABILITIES"
                                                         ])
    filepath = 'CDP_Neighbors_Detail.xlsx'
    array.to_excel(filepath, index=False)

    # End timer.
    end = time.perf_counter()
    print(f"{end - start:0.4f} seconds")


if __name__ == "__main__":
    main()
