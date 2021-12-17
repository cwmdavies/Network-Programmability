import netmiko

device1 = device = {
    "device_type": "cisco_ios_serial",
    "username": "",
    "password": "",
    "secret": "",
    "serial_settings": {"port": "COM7", "baudrate": 9600, }
}

device2 = device = {
    "device_type": "cisco_ios_serial",
    "username": "",
    "password": "",
    "secret": "",
    "serial_settings": {"port": "COM7", "baudrate": 115200, }
}

try:
    device1
except:
    try:
        device2
    finally:
        None
finally:
    None

conn = netmiko.ConnectHandler(**device)

conn.enable()

output1 = conn.send_command('show ip int brief')
output2 = conn.send_command('show int desc')

print(output1)
print(output2)
