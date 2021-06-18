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

import source_code
import time as timer


def main():
    start = timer.time()

    try:
        interface_names = source_code.get_interfaces(source_code.IP_Address)

        for int_name in interface_names:
            source_code.get_int_description(int_name)

        int_detail = source_code.ExcelWriter("Interfaces")
        int_detail.add_sheets("Interface Descriptions", )
        int_detail.write("Interface Descriptions", "A", "1", "Interface", )
        int_detail.write("Interface Descriptions", "B", "1", "Description", )
        int_detail.filter_cols("Interface Descriptions", "A", "30")
        int_detail.filter_cols("Interface Descriptions", "B", "60")

        index = 2
        for entries in source_code.interfaces:
            int_detail.write("Interface Descriptions", "A", f"{index}", entries["Interface"],)
            int_detail.write("Interface Descriptions", "B", f"{index}", entries["Description"],)
            index += 1
    except Exception as err:
        source_code.log.exception(f"Main function error: An unknown error occurred")
        source_code.log.exception(f"\t Error: {err}")

    finally:   
        end = timer.time()
        elapsed = (end - start) / 60
        source_code.log.info(f"Total execution time: {elapsed:.3} minutes.",)
        source_code.log.info(f"Script Complete",)


if __name__ == "__main__":
    main()
