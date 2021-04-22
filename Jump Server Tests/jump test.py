import paramiko
from getpass import getpass
import re

CDP_Info = {}

local_IP_addr = '10.251.6.31'   # IP Address of the machine you are connecting from
jumpserver_private_addr = '10.2.151.86' # The internal IP Address for the Jump server
target_addr = '10.145.61.10' # The IP Address You are connecting to

username = input("Enter your username: ")
password = getpass(prompt="Enter your password")

def open_session(IP):
  jumpbox=paramiko.SSHClient()
  jumpbox.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  jumpbox.connect(local_IP_addr, username=username, password=password )
  jumpbox_transport = jumpbox.get_transport()
  src_addr = (jumpserver_private_addr, 22)
  dest_addr = (target_addr, 22)
  jumpbox_channel = jumpbox_transport.open_channel("direct-tcpip", dest_addr, src_addr)
  target=paramiko.SSHClient()
  target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  target.connect(IP, username=username, password=password, sock=jumpbox_channel)
  return target, jumpbox

def main():
  target, jumpbox = open_session(target_addr)
  stdin, stdout, stderr = target.exec_command("sh cdp neighbors Gig 1/0/50 detail")
  stdout = stdout.read()
  stdout = stdout.decode("utf-8")
  Hostname = r"(?=[\n\r].*Device ID:[\s]*([^\n\r]*))"
  Platform = r"(?=[\n\r].*Platform:[\s]*([^\n\r]*))"
  Interface = r"(?=[\n\r].*Interface:[\s]*([^\n\r]*))"
  IPAddr = r"(?=[\n\r].*IP address:[\s]*([^\n\r]*))"
  RemoteInt = r"(?=[\n\r].*Port ID.*: [\s]*([^\n\r]*))"
  Native = r"(?=[\n\r].*Native VLAN:[\s]*([^\n\r]*))"

  Hostname_match = re.finditer(Hostname, stdout, re.MULTILINE)
  Platform_match = re.finditer(Platform, stdout, re.MULTILINE)
  Interface_match = re.finditer(Interface, stdout, re.MULTILINE)
  IPAddr_match = re.finditer(IPAddr, stdout, re.MULTILINE)
  RemoteInt_match = re.finditer(RemoteInt, stdout, re.MULTILINE)
  Native_match = re.finditer(Native, stdout, re.MULTILINE)

  for line in Hostname_match:
      Hostname = line[1].split()
      Hostname = Hostname[0]
      CDP_Info["Hostname"] = Hostname
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
      CDP_Info["IP Address"] = IPAddr
  for line in RemoteInt_match:
      RemoteInt = line[1].split()
      RemoteInt = RemoteInt[0]
      CDP_Info["Remote Interface"] = RemoteInt
  for line in Native_match:
      Native = line[1].split()
      Native = Native[0]
      CDP_Info["Native VLAN"] = Native
  
  target.close()
  jumpbox.close()

if __name__ == "__main__":
    main()