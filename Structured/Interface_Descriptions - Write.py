###############################################
#             Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################
#
#   A simple script that parses the output of
#   an excel spreadsheet for interface names
#   and descriptions and writes them to a switch
#   of your choice.

from source_code import *


def main():
    start = timer.time()
    int_write(IP_Address)
    end = timer.time()
    elapsed = (end - start) / 60
    output_log(f"Total execution time: {elapsed:.3} minutes.",)
    output_log(f"Script Complete",)


if __name__ == "__main__":
    main()
