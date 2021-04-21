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
from openpyxl import load_workbook, Workbook
from getpass import getpass
from excel_writer import __excel

IP_list = []

username = input("Type in your username: ")
password = getpass(prompt="Type in your password: ")
Sitename = input("Enter the site name/code: ")
port = "22"

dateTimeObj = datetime.now()
datetime = dateTimeObj.strftime("%d/%m/%Y %H:%M:%S")

def open_session(IP):
    try:
        output_log(f"Connected to: {IP}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=IP, port=port, username=username, password=password)
        return ssh, True
    except paramiko.ssh_exception.AuthenticationException:
        error_log(f"Authentication to IP: {IP} failed! Please check your IP, username and password.")
        return None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        error_log(f"Unable to connect to IP: {IP}!")
        return None, False
    except (ConnectionError, TimeoutError):
        error_log(f"Timeout error occured for IP: {IP}!")
        return None, False

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