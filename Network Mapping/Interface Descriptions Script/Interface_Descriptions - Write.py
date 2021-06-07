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
import time as timer
import ipaddress

jump_server_address = '10.251.6.31'   # The internal ip Address for the Jump server
local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from
username = input("Please enter your username: ")
password = getpass("Please enter your password: ")
IP_Address = input("Please enter an ip Address: ")

commands = []
df = pd.read_excel(r'Interfaces.xlsx')

######################################################################################################################
#          Logging Functions
#


def error_log(message, debug=0):
    date_time_object = time.datetime.now()
    datetime = date_time_object.strftime("%d/%m/%Y %H:%M:%S")
    error_file = open("Error Log.txt", "a")
    error_file.write(f"{datetime} - {message}")
    error_file.write("\n")
    error_file.close()
    if debug == 1:
        print(message)


def output_log(message, debug=0):
    date_time_object = time.datetime.now()
    datetime = date_time_object.strftime("%d/%m/%Y %H:%M:%S")
    output_file = open("Output Log.txt", "a")
    output_file.write(f"{datetime} - {message}")
    output_file.write("\n")
    output_file.close()
    if debug == 1:
        print(message)

#
#
######################################################################################################################


def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def open_session(ip):
    if not ip_check(ip):
        error_log(f"open_session function error: "
                  f"ip Address {ip} is not a valid Address. Please check and restart the script!", debug=1)
        return None, False
    try:
        output_log(f"Trying to establish a connection to: {ip}")
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
        output_log(f"Connection to ip: {ip} established")
        return target, jump_box, True
    except paramiko.ssh_exception.AuthenticationException:
        error_log(f"Authentication to ip: {ip} failed! Please check your ip, username and password.")
        return None, None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        error_log(f"Unable to connect to ip: {ip}!")
        return None, None, False
    except (ConnectionError, TimeoutError):
        error_log(f"Timeout error occurred for ip: {ip}!")
        return None, None, False
    except Exception as err:
        error_log(f"Open Session Error: An unknown error occurred for ip: {ip}!")
        error_log(f"\t Error: {err}")
        return None, None, False


def int_write(ip):
    global commands
    ssh, jump_box, connection = open_session(ip)
    if not connection:
        return None
    try:
        output_log(f"int_write function: Preparing to writing interface descriptions.")
        channel = ssh.invoke_shell()
        stdin = channel.makefile("wb")
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
        stdin.close()
        output_log(f"int_write function: Finished writing interface descriptions.")
    except Exception as err:
        error_log(f"Int_write function Error: An unknown error occurred!")
        error_log(f"\t Error: {err}")
    finally:
        ssh.close()
        jump_box.close()


def main():
    start = timer.time()
    try:
        int_write(IP_Address)
    except Exception as err:
        error_log(f"Main function error: An unknown error occurred")
        error_log(f"\t Error: {err}")
    finally:
        end = timer.time()
        elapsed = (end - start) / 60
        output_log(f"Total execution time: {elapsed:.3} minutes.", debug=1)
        output_log(f"Script Complete", debug=1)


if __name__ == "__main__":
    main()
