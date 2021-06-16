###############################################
#             Under Construction              #
#                Design Phase                 #
#                                             #
###############################################
#
#   A simple  napalm script that parses the output 
#   of the "show interface descriptions"
#   command and writes it in a neat format
#   to an excel spreadsheet.

from source_code import *
import napalm


def main():
    driver_ios = napalm.get_network_driver("ios")
    device = driver_ios(hostname=IP_Address, username=username, password=password)
    device.open()
    device_interfaces = device.get_interfaces()
    device.close()

    int_detail = ExcelWriter("Interfaces")
    int_detail.add_sheets("Interface configuration",)
    int_detail.write("Interface configuration", "A", "1", "Interface",)
    int_detail.write("Interface configuration", "B", "1", "is_enabled",)
    int_detail.write("Interface configuration", "C", "1", "is_up",)
    int_detail.write("Interface configuration", "D", "1", "Description",)
    int_detail.write("Interface configuration", "E", "1", "MTU",)
    int_detail.write("Interface configuration", "F", "1", "Speed",)
    int_detail.filter_cols("Interface configuration", "A", "30")
    int_detail.filter_cols("Interface configuration", "B", "15")
    int_detail.filter_cols("Interface configuration", "C", "15")
    int_detail.filter_cols("Interface configuration", "D", "50")
    int_detail.filter_cols("Interface configuration", "E", "10")
    int_detail.filter_cols("Interface configuration", "F", "10")

    index = 2
    for interface in device_interfaces:
        int_detail.write("Interface configuration", "A", f"{index}", interface,)
        int_detail.write("Interface configuration", "B", f"{index}", device_interfaces[interface]["is_enabled"],)
        int_detail.write("Interface configuration", "C", f"{index}", device_interfaces[interface]["is_up"],)
        int_detail.write("Interface configuration", "D", f"{index}", device_interfaces[interface]["description"],)
        int_detail.write("Interface configuration", "E", f"{index}", device_interfaces[interface]["mtu"],)
        int_detail.write("Interface configuration", "F", f"{index}", device_interfaces[interface]["speed"],)
        index += 1


if __name__ == "__main__":
    main()
