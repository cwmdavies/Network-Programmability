###############################################
#            Under Construction               #
#                Design Phase                 #
#                                             #
###############################################

import paramiko
import textfsm
from getpass import getpass
from openpyxl import load_workbook, Workbook

IPAddr = input("Enter an IP Address: ")
username = input("Enter your username: ")
password = getpass("Enter your Password: ")
jump_server_address = '10.251.6.31'   # The internal ip Address for the Jump server
local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from


def jump_session(ip):
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
    return target, jump_box, True


def get_cdp_details(ip):
    ssh, jump_box, connection = jump_session(ip)
    if not connection:
        return None
    _, stdout, _ = ssh.exec_command("show cdp neighbors detail")
    stdout = stdout.read()
    stdout = stdout.decode("utf-8")
    with open("TEXTFSM_TEMPLATES/cdp_details.txt") as f:
        re_table = textfsm.TextFSM(f)
        result = re_table.ParseText(stdout)
    collection_of_results = [dict(zip(re_table.header, entry)) for entry in result]
    ssh.close()
    jump_box.close()
    return collection_of_results


def get_hostname(ip):
    ssh, jump_box, connection = jump_session(ip)
    if not connection:
        return None
    _, stdout, _ = ssh.exec_command("show run | inc hostname")
    stdout = stdout.read()
    stdout = stdout.decode("utf-8")
    with open("TEXTFSM_TEMPLATES/hostname.txt") as f:
        re_table = textfsm.TextFSM(f)
        result = re_table.ParseText(stdout)
        hostname = result[0][0]
    ssh.close()
    jump_box.close()
    return hostname


def main():
    hostname = get_hostname(IPAddr)
    cdp_details = get_cdp_details(IPAddr)

    filename = "CDP_Neighbors_Detail.xlsx"
    workbook = Workbook()
    workbook.save(filename=filename)
    workbook = load_workbook(filename=filename)
    workbook.create_sheet("CDP Neighbors Detail")
    del workbook["Sheet"]
    ws = workbook["CDP Neighbors Detail"]
    ws["A1"] = "LOCAL_HOST"
    ws["B1"] = "LOCAL_PORT"
    ws["C1"] = "REMOTE_HOST"
    ws["D1"] = "REMOTE_PORT"
    ws["E1"] = "REMOTE_IP"
    ws["F1"] = "PLATFORM"
    ws["G1"] = "SOFTWARE_VERSION"
    ws["H1"] = "CAPABILITIES"
    ws.column_dimensions['A'].width = "22"
    ws.column_dimensions['B'].width = "22"
    ws.column_dimensions['C'].width = "42"
    ws.column_dimensions['D'].width = "22"
    ws.column_dimensions['E'].width = "22"
    ws.column_dimensions['F'].width = "42"
    ws.column_dimensions['G'].width = "120"
    ws.column_dimensions['H'].width = "42"

    index = 2
    for entry in cdp_details:
        ws[f"A{index}"] = hostname
        ws[f"B{index}"] = entry["LOCAL_PORT"]
        ws[f"C{index}"] = entry["REMOTE_HOST"]
        ws[f"D{index}"] = entry["REMOTE_PORT"]
        ws[f"E{index}"] = entry["REMOTE_IP"]
        ws[f"F{index}"] = entry["PLATFORM"]
        ws[f"G{index}"] = entry["SOFTWARE_VERSION"]
        ws[f"H{index}"] = entry["CAPABILITIES"]
        workbook.save(filename=filename)
        index += 1
    workbook.save(filename=filename)


if __name__ == "__main__":
    main()
