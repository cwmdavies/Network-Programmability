import paramiko
from getpass import getpass
import time
import ctypes
import datetime

now = datetime.datetime.now()

ip = input("Enter the IP Address: ")
username = input("Enter the Username: ")
password = getpass(prompt='Enter the Password: ')

try:
    remote_conn_pre=paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_conn_pre.connect(ip, port=22, username=username,
                            password=password,
                            look_for_keys=False, allow_agent=False)
except (paramiko.ssh_exception.NoValidConnectionsError):
    ctypes.windll.user32.MessageBoxW(0, 'SSH Is not Enabled for this Device.\nPlease enable SSH and try again', 'Error', 0)
    exit()
except (TimeoutError):
    ctypes.windll.user32.MessageBoxW(0, 'Connection Failed!.\nPlease check that the device is up and the IP address is correct.', 'Error', 0)
    exit()
except (paramiko.ssh_exception.AuthenticationException):
    ctypes.windll.user32.MessageBoxW(0, 'Authentication Failed!.\nPlease check that the credentials are correct and try again.', 'Error', 0)
    exit()

remote_conn = remote_conn_pre.invoke_shell()

remote_conn.send("terminal datadump\n")
remote_conn.send("configure terminal\n")
remote_conn.send("interface vlan 630\n")
remote_conn.send("name Video\n")
remote_conn.send("interface range FastEthernet2-8\n")
remote_conn.send("switchport mode access\n")
remote_conn.send("switchport access vlan 630\n")
remote_conn.send("name Video\n")
remote_conn.send("end\n")
remote_conn.send("show vlan tag 630\n")
time.sleep(5)
output = remote_conn.recv(65535)
output_str = output.decode('utf-8')

file=open("output.txt", "w")

print("#############################################################", file=open("output.txt", "a"))
print("#                                                           #", file=open("output.txt", "a"))
print("#                THIS IS THE HOST IP ADDRESS                #", file=open("output.txt", "a"))
print("#                      ", ip, "                       #", file=open("output.txt", "a"))
print("#                   ", now.strftime("%d-%m-%y  %H:%M:%S"), "                    #", file=open("output.txt", "a"))
print("#############################################################", file=open("output.txt", "a"))
print(output_str, file=open("output.txt", "a"))
remote_conn.close()
ctypes.windll.user32.MessageBoxW(0, 'Operation Complete.', 'Info', 0)
