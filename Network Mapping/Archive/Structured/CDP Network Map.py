###############################################
#            Under Construction               #
#               Testing Phase                 #
#                                             #
###############################################

import source_code
import time as timer
from multiprocessing.pool import ThreadPool


def main():
    start = timer.time()
    source_code.IP_list.append(source_code.IP_Address)
    pool = ThreadPool(30)
    i = 0

    try:
        source_code.log.info(f"Script started for site: {source_code.Sitecode}",)
        print("You will be notified when the script finishes - "
              "This may take a while depending on the size of the network!")
        
        while i < len(source_code.IP_list):
            limit = i + min(30, (len(source_code.IP_list) - i))
            hostnames = source_code.IP_list[i:limit]
            pool.map(source_code.find_ips, hostnames)
            i = limit

        pool.close()
        pool.join()

        cdp_detail = source_code.ExcelWriter(source_code.Sitecode)
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
        for entries in source_code.CDP_Info_List:
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
        source_code.log.error("Main Function Error: An unknown error occurred!")
        source_code.log.error(f"\t Error: {err}")
    finally:
        end = timer.time()
        elapsed = (end - start) / 60
        source_code.log.error(f"Total execution time: {elapsed:.3} minutes.",)
        source_code. log.error(f"Script Complete for site: {source_code.Sitecode}",)
        source_code.messagebox(f"Script Complete for site: {source_code.Sitecode}", "Script Complete")


if __name__ == "__main__":
    main()
