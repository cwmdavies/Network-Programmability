###############################################
#            Under Construction               #
#                Design Phase                 #
#                                             #
###############################################

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

Debugging = 0
IPAddr = input("Enter an IP Address: ")
username = input("Enter your username: ")
password = getpass("Enter your Password: ")
jump_server_address = '10.251.6.31'  # The internal ip Address for the Jump server
local_IP_address = '127.0.0.1'  # ip Address of the machine you are connecting from
IP_LIST = []
Hostnames_List = []
collection_of_results = []
filename = "CDP_Neighbors_Detail.xlsx"
index = 2
ThreadLock = Lock()


# ---------------------------------------------------------
# -------------- Logging Configuration Start --------------

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


def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


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
        target.connect(destination_address, username=username, password=password, sock=jump_box_channel, timeout=4,)
        with ThreadLock:
            log.info(f"Connection to ip: {ip} established")
        return target, jump_box, True
    except paramiko.ssh_exception.AuthenticationException:
        with ThreadLock:
            log.error(f"Authentication to ip: {ip} failed! Please check your ip, username and password.")
        return None, None, False
    except paramiko.ssh_exception.NoValidConnectionsError:
        with ThreadLock:
            log.error(f"Unable to connect to ip: {ip}!")
        return None, None, False
    except (ConnectionError, TimeoutError):
        with ThreadLock:
            log.error(f"Timeout error occurred for ip: {ip}!")
        return None, None, False
    except Exception as err:
        with ThreadLock:
            log.error(f"Open Session Error: An unknown error occurred for ip: {ip}!")
            log.error(f"\t Error: {err}")
        return None, None, False


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


def get_hostname(ip):
    ssh, jump_box, connection = jump_session(ip)
    if not connection:
        return None
    _, stdout, _ = ssh.exec_command("show run | inc hostname")
    stdout = stdout.read()
    stdout = stdout.decode("utf-8")
    try:
        with open("./textfsm/hostname.txt") as f:
            re_table = textfsm.TextFSM(f)
            result = re_table.ParseText(stdout)
            hostname = result[0][0]
    except:
        hostname = "Not Found"
    ssh.close()
    jump_box.close()
    return hostname


def to_excel(cdp_details):
    global index
    workbook = Workbook()
    workbook.create_sheet("CDP Neighbors Detail")
    del workbook["Sheet"]
    workbook.save(filename=filename)
    workbook = load_workbook(filename=filename)
    ws = workbook["CDP Neighbors Detail"]
    ws["A1"] = "LOCAL_HOST"
    ws["B1"] = "LOCAL_PORT"
    ws["C1"] = "LOCAL_IP"
    ws["D1"] = "REMOTE_HOST"
    ws["E1"] = "REMOTE_PORT"
    ws["F1"] = "REMOTE_IP"
    ws["G1"] = "PLATFORM"
    ws["H1"] = "SOFTWARE_VERSION"
    ws["I1"] = "CAPABILITIES"
    ws.column_dimensions['A'].width = "25"
    ws.column_dimensions['B'].width = "25"
    ws.column_dimensions['C'].width = "25"
    ws.column_dimensions['D'].width = "45"
    ws.column_dimensions['E'].width = "25"
    ws.column_dimensions['F'].width = "25"
    ws.column_dimensions['G'].width = "25"
    ws.column_dimensions['H'].width = "120"
    ws.column_dimensions['I'].width = "45"
    ws.auto_filter.ref = ws.dimensions
    workbook.save(filename=filename)
    try:
        for entry in cdp_details:
            ws[f"A{index}"] = entry["LOCAL_HOST"]
            ws[f"B{index}"] = entry["LOCAL_PORT"]
            ws[f"C{index}"] = entry["LOCAL_IP"]
            ws[f"D{index}"] = entry["REMOTE_HOST"]
            ws[f"E{index}"] = entry["REMOTE_PORT"]
            ws[f"F{index}"] = entry["REMOTE_IP"]
            ws[f"G{index}"] = entry["PLATFORM"]
            ws[f"H{index}"] = entry["SOFTWARE_VERSION"]
            ws[f"I{index}"] = entry["CAPABILITIES"]
            workbook.save(filename=filename)
            index += 1
    except Exception as err:
        print("An Exception Occurred")
        print({err})

    workbook.save(filename=filename)


def main():
    start = time.perf_counter()
    IP_LIST.append(IPAddr)
    pool = ThreadPool(10)

    i = 0
    while i < len(IP_LIST):
        limit = i + min(10, (len(IP_LIST) - i))
        ip_addresses = IP_LIST[i:limit]

        pool.map(get_cdp_details, ip_addresses)

        i = limit
    
    pool.close()
    pool.join()
    
    to_excel(collection_of_results)
    end = time.perf_counter()
    print(f"{end - start:0.4f} seconds")

if __name__ == "__main__":
    main()
