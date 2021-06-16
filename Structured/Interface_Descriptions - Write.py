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
import time as timer


def main():
    start = timer.time()
    int_write(IP_Address)
    end = timer.time()
    elapsed = (end - start) / 60
    log.info(f"Total execution time: {elapsed:.3} minutes.",)
    log.info(f"Script Complete",)


if __name__ == "__main__":
    main()
