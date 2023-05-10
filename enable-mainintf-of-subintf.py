import time
import yaml, json, csv
from fireREST import FMC
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = FMC(hostname=set_dict['fmc_hostname'], username=set_dict['fmc_username'], password=set_dict['fmc_password'], domain='Global')

# Read CSV file as an array of dictionary
intf_dict = []
with open('fmc-interface.csv') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)
    for row in csv_reader:
        row_data = {key: value for key, value in zip(headers, row)}
        intf_dict.append(row_data)

main_intf_list = []
for i in intf_dict:
    if i['interface_type'] == "SubInterface":
        main_intf = i['interface_name'].split(".")[0]
        if "Port-channel" not in main_intf and main_intf not in main_intf_list:
            main_intf_list.append(main_intf)


def pre_check(interface):
    response = fmc.device.devicerecord.physicalinterface.get(container_name=set_dict['ftd_hostname'],name=interface)
    if response['enabled'] == True:
        return ("exist")
    else:
       return

def post_check(interface):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(interface) == "exist":
            return ("exist")

def creation(interface):
    payload = fmc.device.devicerecord.physicalinterface.get(container_name=set_dict['ftd_hostname'],name=interface)
    payload['enabled'] = 'true'
    fmc.device.devicerecord.physicalinterface.update(container_name=set_dict['ftd_hostname'],data=payload)

print_header('Enable Main Interface of Subinterface')
for interface in main_intf_list:
    print_action(interface)
    if pre_check(interface) == "exist":
        print_skip()
    else:
        creation(interface)
        if post_check(interface) == "exist":
            print_pass()
        else:
            print_fail()