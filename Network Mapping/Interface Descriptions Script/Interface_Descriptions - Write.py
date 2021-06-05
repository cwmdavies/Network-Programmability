###############################################
#             Under Contruction               #
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
import time as timer
import re
import ipaddress

jumpserver_private_addr = '10.251.6.31'   # The internal IP Address for the Jump server
local_IP_addr = '127.0.0.1' # IP Address of the machine you are connecting from
username = input("Please enter your username: ")
password = getpass("Please enter your password: ")
IP_Address = input("Please enter an IP Address: ")

commands = []
df = pd.read_excel (r'Interfaces.xlsx')

#############################################################################################################################################
##          Logging Functions
#

def error_log(message, debug=0):
    dateTimeObj = time.datetime.now()
    datetime = dateTimeObj.strftime("%d/%m/%Y %H:%M:%S")
    error_file = open("Error Log.txt", "a")
    error_file.write(f"{datetime} - {message}")
    error_file.write("\n")
    error_file.close()
    if debug == 1:
        print(message)

def output_log(message, debug=0):
    dateTimeObj = time.datetime.now()
    datetime = dateTimeObj.strftime("%d/%m/%Y %H:%M:%S")
    output_file = open("Output Log.txt", "a")
    output_file.write(f"{datetime} - {message}")
    output_file.write("\n")
    output_file.close()
    if debug == 1:
        print(message)

#
##
#############################################################################################################################################

def IP_Check(IP):
    try:
        ipaddress.ip_address(IP)
        return True
    except:
        return False

def open_session(IP):
    if IP_Check(IP) != True:
        error_log(f"open_session function error: IP Address {IP} is not a valid Address. Please check and restart the script!", debug=1)
        return None, False
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
        return None, None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        error_log(f"Unable to connect to IP: {IP}!")
        return None, None, False
    except (ConnectionError, TimeoutError):
        error_log(f"Timeout error occured for IP: {IP}!")
        return None, None, False
    except:
        error_log(f"Open Session Error: An unknown error occured for IP: {IP}!")
        return None, None, False

def int_write(IP):
    global commands
    ssh, jumpbox, connection = open_session(IP)
    if not connection:
        return None
    try:
        output_log(f"int_write function: Preparing to writing interface descriptions.")
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
        stdin.close()
        output_log(f"int_write function: Finished writing interface descriptions.")
    except:
        error_log(f"Int_write function Error: An unknown error occured!")
    finally:
        ssh.close()
        jumpbox.close()
def main():
    start = timer.time()
    try:
        int_write(IP_Address)
    except:
        error_log(f"Main function error: An unknown error occured")
    finally:   
        end = timer.time()
        elapsed = (end - start) / 60
        output_log(f"Total execution time: {elapsed:.3} minutes.", debug=1)
        output_log(f"Script Complete", debug=1)

if __name__ == "__main__":
    main()