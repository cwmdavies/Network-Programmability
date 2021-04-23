###############################################
#             Under Contruction               #
#                 Build Phase                 #
#                                             #
###############################################

import os
import re
import time
from multiprocessing.pool import ThreadPool
import paramiko
from datetime import datetime
from getpass import getpass
from excel_writer import __excel

IP_list = []
CDP_Info_List = []
IPAddr = input("Enter your IP Address: ")

jumpserver_private_addr = '10.251.6.31'   # The internal IP Address for the Jump server
local_IP_addr = '127.0.0.1' # IP Address of the machine you are connecting from

username = input("Type in your username: ")
password = getpass(prompt="Type in your password: ")
Sitename = input("Enter the site name/code: ")
port = "22"

dateTimeObj = datetime.now()
datetime = dateTimeObj.strftime("%d/%m/%Y %H:%M:%S")

def open_session(IP):
    try:
        output_log(f"Trying to establish a connection to: {IP}")
        jumpbox=paramiko.SSHClient()
        jumpbox.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jumpbox.connect(jumpserver_private_addr, username=username, password=password )
        jumpbox_transport = jumpbox.get_transport()
        src_addr = (local_IP_addr, 22)
        dest_addr = (IP, 22)
        jumpbox_channel = jumpbox_transport.open_channel("direct-tcpip", dest_addr, src_addr)
        target=paramiko.SSHClient()
        target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target.connect(dest_addr, username=username, password=password, sock=jumpbox_channel)
        output_log(f"Connection to IP: {IP} established")
        return target, jumpbox, True
    except paramiko.ssh_exception.AuthenticationException:
        error_log(f"Authentication to IP: {IP} failed! Please check your IP, username and password.")
        return None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        error_log(f"Unable to connect to IP: {IP}!")
        return None, False
    except (ConnectionError, TimeoutError):
        error_log(f"Timeout error occured for IP: {IP}!")
        return None, False

def extract_cdp_neighbors(IP):
    interface_names = []
    command = "sh cdp neighbors"
    regex = r"^.{17}(\b(Ten|Gig|Loo|Vla|F|Twe|Ten|Fo).{15})"
    ssh, jumpbox, connection = open_session(IP)
    if not connection:
        return None
    try:
        output_log(f"Extracting CDP Neighbor Information for IP: {IP}")
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
        error_log(f"Extract CDP Neighbor Function Error: There is an error connecting or establishing SSH session to IP Address {IP}")
        return None
    finally:
        ssh.close()
        jumpbox.close()

def neighbor_detail(IP, commands):
    formatted_commands = []
    global IP_list
    regex = r"(?=[\n\r].*IP address:[\s]*([^\n\r]*))"
    ssh, jumpbox, connection = open_session(IP)
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
                found_IP = match.group(i)
                if found_IP not in IP_list:
                    IP_list.append(found_IP)
    except paramiko.ssh_exception.SSHException:
        error_log(f"Neighbor Detail Function Error: There is an error connecting or establishing SSH session to IP Address {IP}")
    finally:
        ssh.close()
        jumpbox.close()

def CDP_Details(IP, commands):
    CDP_Info = {}
    ssh, jumpbox, connection = open_session(IP)
    if not connection:
        return None
    try:
        stdin, stdout, stderr = ssh.exec_command(commands)
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")

        RemoteHost = r"(?=[\n\r].*Device ID:[\s]*([^\n\r]*))"
        Platform = r"(?=[\n\r].*Platform:[\s]*([^\n\r]*))"
        Interface = r"(?=[\n\r].*Interface:[\s]*([^\n\r]*))"
        IPAddr = r"(?=[\n\r].*IP address:[\s]*([^\n\r]*))"
        RemoteInt = r"(?=[\n\r].*Port ID.*: [\s]*([^\n\r]*))"
        Native = r"(?=[\n\r].*Native VLAN:[\s]*([^\n\r]*))"

        RemoteHost_match = re.finditer(RemoteHost, stdout, re.MULTILINE)
        Platform_match = re.finditer(Platform, stdout, re.MULTILINE)
        Interface_match = re.finditer(Interface, stdout, re.MULTILINE)
        IPAddr_match = re.finditer(IPAddr, stdout, re.MULTILINE)
        RemoteInt_match = re.finditer(RemoteInt, stdout, re.MULTILINE)
        Native_match = re.finditer(Native, stdout, re.MULTILINE)

        CDP_Info["LocalHost"] = IP

        for line in RemoteHost_match:
            RemoteHost = line[1].split()
            RemoteHost = RemoteHost[0]
            CDP_Info["RemoteHost"] = RemoteHost
        for line in Platform_match:
            Platform = line[1].split()
            Platform = Platform[1].strip(",")
            CDP_Info["Platform"] = Platform
        for line in Interface_match:
            Interface = line[1].split()
            Interface = Interface[0].strip(",")
            CDP_Info["Local Interface"] = Interface
        for line in IPAddr_match:
            IPAddr = line[1].split()
            IPAddr = IPAddr[0]
            CDP_Info["Remote IP Address"] = IPAddr
        for line in RemoteInt_match:
            RemoteInt = line[1].split()
            RemoteInt = RemoteInt[0]
            CDP_Info["Remote Interface"] = RemoteInt
        for line in Native_match:
            Native = line[1].split()
            Native = Native[0]
            CDP_Info["Native VLAN"] = Native
        CDP_Info_List.append(CDP_Info)
    except paramiko.ssh_exception.SSHException:
        error_log(f"CDP Info Function Error: There is an error connecting or establishing SSH session to IP Address {IP}")
    finally:
        ssh.close()
        jumpbox.close()

def find_IPs(IP):
    commands = []
    
    interface_names = extract_cdp_neighbors(IP)
    if not interface_names:
        return -1
    for name in interface_names:
        commands.append(f"show cdp neighbors {name} detail | include IP")
    commands.append("exit")
    neighbor_detail(IP, commands)

    for name in interface_names:
        command = f"show cdp neighbors {name} detail"
        CDP_Details(IP, command)

def error_log(message):
    print(f"{message}")
    error_file = open("Error Log.txt", "a")
    error_file.write(f"{datetime} - {message}")
    error_file.write("\n")
    error_file.close()

def output_log(message):
    print(f"{message}")
    output_file = open("Output Log.txt", "a")
    output_file.write(f"{datetime} - {message}")
    output_file.write("\n")
    output_file.close()

def main():
    global IPAddr
    global IP_list
    global CDP_Info_List

    start = time.time()
    IP_list.append(IPAddr)
    pool = ThreadPool()
    pool.map(find_IPs, IP_list[0::])
    pool.close()

    end = time.time()
    elapsed = (end - start) / 60
    output_log(f"Total execution time: {elapsed:.3} minutes.")
    output_log("Script Complete!")

if __name__ == "__main__":
    main()