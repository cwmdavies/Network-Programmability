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

import source_code
import time as timer


def main():
    start = timer.time()
    source_code.int_write(source_code.IP_Address)
    end = timer.time()
    elapsed = (end - start) / 60
    source_code.log.info(f"Total execution time: {elapsed:.3} minutes.",)
    source_code.log.info(f"Script Complete",)


if __name__ == "__main__":
    main()
