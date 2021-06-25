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
    if source_code.file_loc:
        with open(source_code.file_loc, "r") as file:
            for IP_Address in file:
                ip_list.append(IP_Address.strip())
    else:
        ip_list.append(source_code.IP_Address.strip())

    for IP in ip_list:
        device_hostname = source_code.np_get_hostname(IP)
        device_interfaces = source_code.np_get_interfaces(IP)

        filename = f"Interfaces_{device_hostname}.xlsx"

        workbook = source_code.Workbook()
        workbook.save(filename=filename)
        workbook = source_code.load_workbook(filename=filename)
        workbook.create_sheet("Interface configuration")
        workbook.create_sheet("Switch Information")
        del workbook["Sheet"]
        ws = workbook["Switch Information"]
        ws[f"A1"] = "Hostname"
        ws[f"B1"] = "IP Address"
        ws[f"A2"] = device_hostname
        ws[f"B2"] = IP
        ws.column_dimensions['A'].width = "20"
        ws.column_dimensions['B'].width = "15"
        ws = workbook["Interface configuration"]
        ws[f"A1"] = "Interface"
        ws[f"B1"] = "is_enabled"
        ws[f"C1"] = "is_up"
        ws[f"D1"] = "Description"
        ws[f"E1"] = "MTU"
        ws[f"F1"] = "Speed"
        ws.column_dimensions['A'].width = "25"
        ws.column_dimensions['B'].width = "15"
        ws.column_dimensions['C'].width = "10"
        ws.column_dimensions['D'].width = "60"
        ws.column_dimensions['E'].width = "10"
        ws.column_dimensions['F'].width = "10"

        index = 2
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
