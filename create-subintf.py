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
    subintf_id = interface['interface_name'].split(".")[1]
    subinterfaces = fmc.device.devicerecord.subinterface.get(container_name=set_dict['ftd_hostname'])
    for i in subinterfaces:
        if i['subIntfId'] == int(subintf_id):
            return ("exist")
    return

def post_check(interface):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(interface) == "exist":
            return ("exist")

def creation(interface):
    subintf = interface['interface_name'].split(".")
    ipv4_mask = interface['ip_address'].split("/")
    sec_zone_id = fmc.object.securityzone.get(name=interface['security_zone'])['id']
    payload = {
        "subIntfId": subintf[1],
        "vlanId": subintf[1],
        "name": subintf[0],
        "ifname": interface['logical_name'],
        "enabled": True,
        "securityZone": {
          "id": sec_zone_id,
          "type": "SecurityZone"
        },
        "ipv4": {
            "static": {
            "address": ipv4_mask[0],
            "netmask": ipv4_mask[1]
            }
        },        
    }
    fmc.device.devicerecord.subinterface.create(container_name=set_dict['ftd_hostname'],data=payload)

print_header('Create Subinterface')
for interface in intf_dict:
    if interface['interface_type'] == "SubInterface":    
        print_action(interface['interface_name']+" ["+interface['logical_name']+" "+interface['security_zone']+" "+interface['ip_address']+"]")
        if pre_check(interface) == "exist":
            print_skip()
        else:
            creation(interface)
            if post_check(interface) == "exist":
                print_pass()
            else:
                print_fail()
                