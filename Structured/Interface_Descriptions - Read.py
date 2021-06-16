###############################################
#            Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################
#
#   A simple script that parses the output 
#   of the "show interface descriptions"
#   command and writes it in a neat format
#   to an excel spreadsheet.

from source_code import *
import time as timer


def main():
    start = timer.time()

    int_detail = ExcelWriter("Interfaces")
    int_detail.add_sheets("Interface Descriptions",)
    int_detail.write("Interface Descriptions", "A", "1", "Interface",)
    int_detail.write("Interface Descriptions", "B", "1", "Description",)
    int_detail.filter_cols("Interface Descriptions", "A", "30")
    int_detail.filter_cols("Interface Descriptions", "B", "60")

    try:
        interface_names = get_interfaces(gui.IP_Address)

        for int_name in interface_names:
            get_int_description(int_name)

        index = 2
        for entries in interfaces:
            int_detail.write("Interface Descriptions", "A", f"{index}", entries["Interface"],)
            int_detail.write("Interface Descriptions", "B", f"{index}", entries["Description"],)
            index += 1
    except Exception as err:
        error_log(f"Main function error: An unknown error occurred")
        error_log(f"\t Error: {err}")

    finally:   
        end = timer.time()
        elapsed = (end - start) / 60
        output_log(f"Total execution time: {elapsed:.3} minutes.",)
        output_log(f"Script Complete",)


if __name__ == "__main__":
    main()
