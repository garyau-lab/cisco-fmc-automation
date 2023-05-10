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


def pre_check(interface):
    response = fmc.device.devicerecord.physicalinterface.get(container_name=set_dict['ftd_hostname'],name=interface['interface_name'])
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
    payload = fmc.device.devicerecord.physicalinterface.get(container_name=set_dict['ftd_hostname'],name=interface['interface_name'])
    payload['enabled'] = 'true'
    fmc.device.devicerecord.physicalinterface.update(container_name=set_dict['ftd_hostname'],data=payload)

print_header('Enable Interface')
for interface in intf_dict:
    if interface['interface_type'] == "PhysicalInterface":
        print_action(interface['interface_name'])
        if pre_check(interface) == "exist":
            print_skip()
        else:
            creation(interface)
            if post_check(interface) == "exist":
                print_pass()
            else:
                print_fail()