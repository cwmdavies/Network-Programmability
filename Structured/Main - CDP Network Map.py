###############################################
#            Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################

from source_code import *
import time as timer
from multiprocessing.pool import ThreadPool


def main():
    global CDP_Info_List
    global IP_list

    start = timer.time()
    IP_list.append(IP_Address)
    pool = ThreadPool(30)
    i = 0

    try:
        output_log(f"Script started for site: {Sitecode}",)
        print("You will be notified when the script finishes - "
              "This may take a while depending on the size of the network!")
        
        while i < len(IP_list):
            limit = i + min(30, (len(IP_list) - i))
            hostnames = IP_list[i:limit]
            pool.map(find_ips, hostnames)
            i = limit

        pool.close()
        pool.join()

        cdp_detail = ExcelWriter(Sitecode)
        cdp_detail.add_sheets("CDP_Nei_Info",)
        cdp_detail.write("CDP_Nei_Info", "A", "1", "Local Hostname",)
        cdp_detail.write("CDP_Nei_Info", "B", "1", "Local ip Address",)
        cdp_detail.write("CDP_Nei_Info", "C", "1", "Local Interface",)
        cdp_detail.write("CDP_Nei_Info", "D", "1", "Remote Interface",)
        cdp_detail.write("CDP_Nei_Info", "E", "1", "Remote Hostname",)
        cdp_detail.write("CDP_Nei_Info", "F", "1", "Remote ip Address",)
        cdp_detail.write("CDP_Nei_Info", "G", "1", "Platform",)
        cdp_detail.write("CDP_Nei_Info", "H", "1", "Native VLAN",)
        cdp_detail.filter_cols("CDP_Nei_Info", "A", "30")
        cdp_detail.filter_cols("CDP_Nei_Info", "B", "25")
        cdp_detail.filter_cols("CDP_Nei_Info", "C", "25")
        cdp_detail.filter_cols("CDP_Nei_Info", "D", "25")
        cdp_detail.filter_cols("CDP_Nei_Info", "E", "45")
        cdp_detail.filter_cols("CDP_Nei_Info", "F", "25")
        cdp_detail.filter_cols("CDP_Nei_Info", "G", "25")
        cdp_detail.filter_cols("CDP_Nei_Info", "H", "25")

        index = 2
        for entries in CDP_Info_List:
            cdp_detail.write("CDP_Nei_Info", "A", f"{index}", entries["Local Hostname"],)
            cdp_detail.write("CDP_Nei_Info", "B", f"{index}", entries["Local ip Address"],)
            cdp_detail.write("CDP_Nei_Info", "C", f"{index}", entries["Local Interface"],)
            cdp_detail.write("CDP_Nei_Info", "D", f"{index}", entries["Remote Interface"],)
            cdp_detail.write("CDP_Nei_Info", "E", f"{index}", entries["Remote Host"],)
            cdp_detail.write("CDP_Nei_Info", "F", f"{index}", entries["Remote ip Address"],)
            cdp_detail.write("CDP_Nei_Info", "G", f"{index}", entries["Platform"],)
            if "Native VLAN" in entries:
                cdp_detail.write("CDP_Nei_Info", "H", f"{index}", entries["Native VLAN"],)
            else:
                cdp_detail.write("CDP_Nei_Info", "H", f"{index}", "Not Found",)
            index += 1
    except Exception as err:
        error_log("Main Function Error: An unknown error occurred!")
        error_log(f"\t Error: {err}")
    finally:
        end = timer.time()
        elapsed = (end - start) / 60
        output_log(f"Total execution time: {elapsed:.3} minutes.",)
        output_log(f"Script Complete for site: {Sitecode}",)
        messagebox(f"Script Complete for site: {Sitecode}", "Script Complete")


if __name__ == "__main__":
    main()
