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

import datetime as time
import ipaddress


def ip_check(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


#######################################################################################################################
#          Logging Functions
#

def error_log(message,):
    date_time_object = time.datetime.now()
    datetime = date_time_object.strftime("%d/%m/%Y %H:%M:%S")
    error_file = open("Error Log.txt", "a")
    error_file.write(f"{datetime} - {message}")
    error_file.write("\n")
    error_file.close()


def output_log(message,):
    date_time_object = time.datetime.now()
    datetime = date_time_object.strftime("%d/%m/%Y %H:%M:%S")
    output_file = open("Output Log.txt", "a")
    output_file.write(f"{datetime} - {message}")
    output_file.write("\n")
    output_file.close()

#
#
#######################################################################################################################

