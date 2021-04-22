import paramiko
import configparser
from getpass import getpass

cfg = configparser.ConfigParser()
cfg.read("credentials.ini")

local_IP_addr = '10.251.6.31'
jumpserver_private_addr = '10.2.151.86'
target_addr = '10.145.61.10'

username = input("Enter your username: ")
password = getpass(prompt="Enter your password: ")

jumpbox=paramiko.SSHClient()
jumpbox.set_missing_host_key_policy(paramiko.AutoAddPolicy())
jumpbox.connect(local_IP_addr, username=username, password=password )

jumpbox_transport = jumpbox.get_transport()
src_addr = (jumpserver_private_addr, 22)
dest_addr = (target_addr, 22)
jumpbox_channel = jumpbox_transport.open_channel("direct-tcpip", dest_addr, src_addr)

target=paramiko.SSHClient()
target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
target.connect(target_addr, username=username, password=password, sock=jumpbox_channel)

with open("output.txt", "w+") as f:
  stdin, stdout, stderr = target.exec_command("sh cdp neighbors Gig 1/0/50 detail")
  stdout = stdout.read()
  stdout = stdout.decode("utf-8")
  for line in stdout:
    f.write(str(line).strip("\n"))

target.close()
jumpbox.close()