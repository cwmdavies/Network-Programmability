###############################################
#             Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################
#
#   A simple script that parses the output 
#   of the "show interface descriptions"
#   command and writes it in a neat format
#   to an excel spreadsheet.

import os
import paramiko
import datetime as time
from openpyxl import load_workbook, Workbook
import re
import time as timer
from getpass import getpass
import ipaddress

jump_server_address = '10.251.6.31'   # The internal ip Address for the Jump server
local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from
username = input("Please enter your username: ")
password = getpass("Please enter your password: ")
IP_Address = input("Please enter an ip Address: ")

interfaces = list()


class ExcelWriter:
    def __init__(self, name):
        self.i = 0
        self.name = name
        self.filename = self.name + ".xlsx"
        if os.path.exists(f"{self.filename}"):
            os.remove(f"{self.filename}")
        workbook = Workbook()
        workbook.save(filename=self.filename)

    def get_sheets(self):
        workbook = load_workbook(filename=self.filename)
        return workbook.sheetnames

    def add_sheets(self, *col_name):
        workbook = load_workbook(filename=self.filename)
        for value in col_name:
            if value not in workbook.sheetnames:
                workbook.create_sheet(value)
            else:
                output_log(f"{value} already exists in {self.name}. Ignoring column creation!")
        if "Sheet" in workbook.sheetnames:
            del workbook["Sheet"]
        workbook.save(filename=self.filename)

    def write(self, sheet, key, index, value):
        workbook = load_workbook(filename=self.filename)
        ws = workbook[f"{sheet}"]
        ws[f"{key}{index}"] = value
        workbook.save(filename=self.filename)

    def filter_cols(self, sheet, col, width):
        workbook = load_workbook(filename=self.filename)
        ws = workbook[f"{sheet}"]
        ws.auto_filter.ref = ws.dimensions
        ws.column_dimensions[f'{col}'].width = width
        workbook.save(filename=self.filename)


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


def get_interfaces(ip):
    interface_names = list()
    ssh, jump_box, connection = open_session(ip)
    if not connection:
        return None
    try:
        output_log(f"retrieving list of interfaces from ip Address: {ip}")
        _, stdout, _ = ssh.exec_command("show ip interface brief")
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        regex = r"^(\b(Ten|Gig|Loo|Vla|Fas|Twe|Ten|Fo).{20})"
        matches = re.finditer(regex, stdout, re.MULTILINE)
        for match in matches:
            temp_interface_name = match.group(1)
            temp_interface_name = temp_interface_name.strip()
            interface_names.append(temp_interface_name)
        output_log(f"List retrieval successful for ip Address: {ip}")
        return interface_names
    except paramiko.ssh_exception.AuthenticationException:
        error_log(f"Interfaces function Error: Authentication to ip: "
                  f"{ip} failed! Please check your ip, username and password.")
        return None
    except paramiko.ssh_exception.NoValidConnectionsError:
        error_log(f"Interfaces function Error: Unable to connect to ip: {ip}!")
        return None
    except (ConnectionError, TimeoutError):
        error_log(f"Interfaces function Error: Timeout error occurred for ip: {ip}!")
        return None
    except Exception as err:
        error_log(f"Interfaces function Error: An unknown error occurred for ip: {ip}!")
        error_log(f"\t Error: {err}")
        return None
    finally:
        ssh.close()
        jump_box.close()


def get_int_description(int_name):
    global interfaces
    interfaces_dict = dict()
    command = f"show run interface {int_name} | inc description"
    ssh, jump_box, connection = open_session(IP_Address)
    if not connection:
        error_log(f"get_int_description - Function Error: No connection is available for ip: {IP_Address}!")
    try:
        output_log(f"retrieving interface description for interface: {int_name}")
        _, stdout, _ = ssh.exec_command(command)
        stdout = stdout.read()
        stdout = stdout.decode("utf-8")
        int_description = re.search(".*description.*", stdout)
        int_description = int_description[0]
        int_description = int_description.strip()
        int_description = int_description.strip("description")
        interfaces_dict["Interface"] = int_name
        interfaces_dict["Description"] = int_description
        output_log(f"Description retrieval successful for interface: {int_name}")
    except TypeError:
        interfaces_dict["Interface"] = int_name
        interfaces_dict["Description"] = "No Description found"
    except paramiko.ssh_exception.SSHException:
        error_log(f"get_int_description - Function Error: "
                  f"There is an error connecting or establishing SSH session to ip Address {IP_Address}")
    except Exception as err:
        error_log(f"get_int_description - Function Error: An unknown error occurred for ip: {IP_Address}, "
                  f"on Interface: {int_name}!")
        error_log(f"\t Error: {err}")
    finally:
        interfaces.append(interfaces_dict)
        ssh.close()
        jump_box.close()


#######################################################################################################################
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
#######################################################################################################################


def main():
    global IP_Address
    global interfaces
    
    start = timer.time()

    int_detail = ExcelWriter("Interfaces")
    int_detail.add_sheets("Interface Descriptions",)
    int_detail.write("Interface Descriptions", "A", "1", "Interface",)
    int_detail.write("Interface Descriptions", "B", "1", "Description",)
    int_detail.filter_cols("Interface Descriptions", "A", "30")
    int_detail.filter_cols("Interface Descriptions", "B", "60")

    try:
        interface_names = get_interfaces(IP_Address)

        for int_name in interface_names:
            get_int_description(int_name)

        index = 2
        for entries in interfaces:
            int_detail.write("Interface Descriptions", "A", f"{index}", entries["Interface"],)
            int_detail.write("Interface Descriptions", "B", f"{index}", entries["Description"],)
            index += 1
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
