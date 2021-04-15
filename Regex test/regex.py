import re

interface_names = []

def extract_cdp_neighbors():
    command = "show cdp neighbors"
    # print("This command is going to be executed: '{0}'".format(command))
    # skip first 17 characters, then take the next 17 characters which start with Gi,Te,Vl,Loop or F
    # regex = r"^(?!S).+$"
    regex = r"^(?!S)^.{17}(\b(Ten|Gig|Loo|Vla).{15})"
    # try to connect to server, if there is no connection, return none

    output = open("CDP.txt", "r")
    output = output.read()
    _input = open("interfaces.txt", "a")
    # output = output.decode("utf-8")
    # find matching lines in output with regex rule
    matches = re.finditer(regex, output, re.MULTILINE)
    for match in matches:
        # delete the whitespace characters at the end
        temp_interface_name = match.group(1)
        temp_interface_name = temp_interface_name.strip()
        # add the name to the interface_name list
        _input.write(temp_interface_name)
        _input.write("\n")

extract_cdp_neighbors()