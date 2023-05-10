import time
import yaml, json, csv
from fireREST import FMC
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = FMC(hostname=set_dict['fmc_hostname'], username=set_dict['fmc_username'], password=set_dict['fmc_password'], domain='Global')

# Read CSV file as an array of dictionary
device_dict = []
with open('fmc-device.csv') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)
    for row in csv_reader:
        row_data = {key: value for key, value in zip(headers, row)}
        device_dict.append(row_data)

for device in device_dict:
    if device['ha_role'] == "active":
        ftd1 = device
    if device['ha_role'] == "standby":
        ftd2 = device        

ftd1_id = fmc.device.devicerecord.get(name=ftd1['hostname'])['id']
ftd2_id = fmc.device.devicerecord.get(name=ftd2['hostname'])['id']

ftd1_ha_intf_id = fmc.device.devicerecord.physicalinterface.get(container_name=ftd1['hostname'], name=ftd1['ha_interface'])['id']

def pre_check():
    try:
        fmc.devicehapair.ftdhapair.get(name=ftd1['ha_name'])
        return ("exist")
    except:
        return

def check_hapair():
    for i in range(set_dict['verify_retry_extended']):
        time.sleep(set_dict['verify_delay'])
        if pre_check() == "exist":
            return ("exist")

def check_insync():
    while 1 < 2:
        time.sleep(15)
        response = fmc.devicehapair.ftdhapair.get(name=ftd1['ha_name'])
        if response['metadata']['secondaryStatus']['currentStatus'] == "Standby":
            return

def creation():
    payload = {
        "name": ftd1['ha_name'],
        "type": "DeviceHAPair",
        "primary": {
            "id": ftd1_id
        },
        "secondary": {
            "id": ftd2_id
        },
        "ftdHABootstrap": {
            "isEncryptionEnabled": "false",
            "useSameLinkForFailovers": "true",
            "lanFailover": {
                "useIPv6Address": "false",
                "logicalName": ftd1['ha_intf_name'],
                "activeIP": ftd1['ha_ip_address'],
                "standbyIP": ftd2['ha_ip_address'],
                "subnetMask": ftd1['ha_mask'],
                "interfaceObject": {
                    "id": ftd1_ha_intf_id,                
                    "type": "PhysicalInterface",
                    "name": ftd1['ha_interface']
                },
            },
            "statefulFailover": {
                "useIPv6Address": "false",
                "logicalName": ftd1['ha_intf_name'],
                "activeIP": ftd1['ha_ip_address'],
                "standbyIP": ftd2['ha_ip_address'],
                "subnetMask": ftd1['ha_mask'],
                "interfaceObject": {
                    "id": ftd1_ha_intf_id,
                    "type": "PhysicalInterface",
                    "name": ftd1['ha_interface']
                },
            }
        }
    }
    fmc.devicehapair.ftdhapair.create(data=payload)

print_header('Add High Availability')
print_action(ftd1['ha_name']+" ["+ftd1['hostname']+" "+ftd2['hostname']+"]")
if pre_check() == "exist":
    print_skip()
else:
    creation()
    if check_hapair() == "exist":
        print_status("Deploying")
        check_insync()
        print_pass()
    else:
        print_fail()
