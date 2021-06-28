###############################################
#            Under Construction               #
#                Design Phase                 #
#                                             #
###############################################

import paramiko
import textfsm
from getpass import getpass

IPAddr = input("Enter an IP Address")
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
    with open("template.txt") as f:
        re_table = textfsm.TextFSM(f)
        result = re_table.ParseText(stdout)
    collection_of_results = [dict(zip(re_table.header, entry)) for entry in result]
    ssh.close()
    jump_box.close()
    return collection_of_results


def main():
    cdp_details = get_cdp_details(IPAddr)
    print(cdp_details)


if __name__ == "__main__":
    main()
