import paramiko
import textfsm
import ipaddress
import logging
import sys
import tkinter as tk
from tkinter import ttk
import pandas as np
from os.path import exists

local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from
filename = "CDP_Neighbors_Detail.xlsx"
timeout = 10


# -----------------------------------------------------------
# --------------- TKinter Configuration Start ---------------

# root window
root = tk.Tk()
root.eval('tk::PlaceWindow . center')
root.geometry("300x500")
root.resizable(False, False)
root.title('Required Details')

# store entries
Username_var = tk.StringVar()
password_var = tk.StringVar()
IP_Address1_var = tk.StringVar()
command_var = tk.StringVar()
Debugging_var = tk.StringVar()
JumpServer_var = tk.StringVar()

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
IP_Address1_label = ttk.Label(Site_details, text="\nSwitch IP:")
IP_Address1_label.pack(fill='x', expand=True)
IP_Address1_entry = ttk.Entry(Site_details, textvariable=IP_Address1_var)
IP_Address1_entry.pack(fill='x', expand=True)

# Command
command_label = ttk.Label(Site_details, text="\ncommand:")
command_label.pack(fill='x', expand=True)
command_entry = ttk.Entry(Site_details, textvariable=command_var)
command_entry.pack(fill='x', expand=True)

# Debugging Dropdown Box
Debugging_var.set("Off")
Debugging_label = ttk.Label(Site_details, text="\nDebugging")
Debugging_label.pack(anchor="w")
Debugging = ttk.Combobox(Site_details, values=["Off", "On"], state="readonly", textvariable=Debugging_var, )
Debugging.current(0)
Debugging.pack(anchor="w")

# Dropdown Box
JumpServer_var.set("10.251.131.6")
JumpServer_label = ttk.Label(Site_details, text="\nJumper Server")
JumpServer_label.pack(anchor="w")
JumpServer = ttk.Combobox(Site_details,
                          values=["MMFTH1V-MGMTS02", "AR31NOC"],
                          state="readonly", textvariable=JumpServer_var,
                          )
JumpServer.current(0)
JumpServer.pack(anchor="w")


# Submit button
Submit_button = ttk.Button(Site_details, text="Submit", command=root.destroy)
Submit_button.pack(fill='x', pady=30)


root.attributes('-topmost', True)
root.mainloop()

username = Username_var.get()
password = password_var.get()
IPAddr1 = IP_Address1_var.get()
command = command_var.get()

if Debugging_var.get() == "On":
    Debugging = 1
elif Debugging_var.get() == "Off":
    Debugging = 0

if JumpServer_var.get() == "AR31NOC":
    jump_server = "10.251.6.31"
elif JumpServer_var.get() == "MMFTH1V-MGMTS02":
    jump_server = "10.251.131.6"

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
        level=logging.WARN,
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


def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def jump_session(ip):
    if not ip_check(ip):
        log.error(f"open_session function error: "
                  f"ip Address {ip} is not a valid Address. Please check and restart the script!",)
        return None, None, False
    try:
        log.info(f"Trying to establish a connection to: {ip}")
        jump_box = paramiko.SSHClient()
        jump_box.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_box.connect(jump_server, username=username, password=password)
        jump_box_transport = jump_box.get_transport()
        src_address = (local_IP_address, 22)
        destination_address = (ip, 22)
        jump_box_channel = jump_box_transport.open_channel("direct-tcpip", destination_address, src_address,
                                                           timeout=timeout,)
        target = paramiko.SSHClient()
        target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target.connect(destination_address, username=username, password=password, sock=jump_box_channel,
                       timeout=timeout, auth_timeout=timeout, banner_timeout=timeout)
        log.info(f"Connection to IP: {ip} established")
        return target, jump_box, True
    except paramiko.ssh_exception.AuthenticationException:
        log.error(f"Authentication to IP: {ip} failed! Please check your ip, username and password.")
        return None, None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        log.error(f"Unable to connect to IP: {ip}!")
        return None, None, False
    except (ConnectionError, TimeoutError):
        log.error(f"Connection or Timeout error occurred for IP: {ip}!")
        return None, None, False
    except Exception as err:
        log.error(f"Open Session Error: An unknown error occurred for IP: {ip}!")
        log.error(f"{err}")
        return None, None, False


def send_command(ip: str, _list: list):
    if exists(f"./textfsm/cisco_ios_{command}.textfsm".replace(" ", "_")):
        ssh, jump_box, connection = jump_session(ip)
        if not connection:
            return None, None, False
        _, stdout, _ = ssh.exec_command(command)
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        with open(f"./textfsm/cisco_ios_{command}.textfsm".replace(" ", "_")) as f:
            re_table = textfsm.TextFSM(f)
            result = re_table.ParseText(stdout)
        results = [dict(zip(re_table.header, entry)) for entry in result]
        for entry in results:
            _list.append(entry)
        ssh.close()
        jump_box.close()
    else:
        log.error(f"The command: '{command}', cannot be found. "
                  "Check the command is correct and make sure the TextFSM file exists for that command.")


def main():
    list_1 = []
    send_command(IPAddr1, list_1, )
    array = np.DataFrame(list_1)
    filepath = f'{command}.xlsx'
    array.to_excel(filepath, index=False)


if __name__ == "__main__":
    main()
