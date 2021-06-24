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

import source_code


def main():
    ip_list = []
    with open("ips.txt", "r") as text:
        for IP_Address in text:
            ip_list.append(IP_Address.strip())

    for IP in ip_list:
        device_hostname = source_code.np_get_hostname(source_code.IP_Address)
        device_interfaces = source_code.np_get_interfaces(source_code.IP_Address)

        filename = f"Interfaces_{device_hostname}.xlsx"

        workbook = source_code.Workbook()
        workbook.save(filename=filename)
        workbook = source_code.load_workbook(filename=filename)
        workbook.create_sheet("Interface configuration")
        del workbook["Sheet"]
        ws = workbook["Interface configuration"]
        ws[f"A1"] = device_hostname
        ws[f"B1"] = source_code.IP_Address
        ws[f"A3"] = "Interface"
        ws[f"B3"] = "is_enabled"
        ws[f"C3"] = "is_up"
        ws[f"D3"] = "Description"
        ws[f"E3"] = "MTU"
        ws[f"F3"] = "Speed"
        ws.column_dimensions['A'].width = "25"
        ws.column_dimensions['B'].width = "15"
        ws.column_dimensions['C'].width = "10"
        ws.column_dimensions['D'].width = "60"
        ws.column_dimensions['E'].width = "10"
        ws.column_dimensions['F'].width = "10"

        index = 4
        for interface in device_interfaces:
            ws[f"A{index}"] = interface
            ws[f"B{index}"] = device_interfaces[interface]["is_enabled"]
            ws[f"C{index}"] = device_interfaces[interface]["is_up"]
            ws[f"D{index}"] = device_interfaces[interface]["description"]
            ws[f"E{index}"] = device_interfaces[interface]["mtu"]
            ws[f"F{index}"] = device_interfaces[interface]["speed"]
            workbook.save(filename=filename)
            index += 1


if __name__ == "__main__":
    main()
