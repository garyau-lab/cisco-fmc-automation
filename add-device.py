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


acp_id = fmc.policy.accesspolicy.get(name=set_dict['acp_name'])['id']

def pre_check(device):
    try:
        fmc.device.devicerecord.get(name=device['hostname'])
        return ("exist")
    except:
        return

def post_check(device):
    for i in range(set_dict['verify_retry_extended']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(device) == "exist":
            return ("exist")

def check_deploying(device):
    while 1 < 2:
        time.sleep(15)
        try:
            response = fmc.deployment.deployabledevices.get(name=device['hostname'])
            return
        except:
            pass
            
def check_deployed(device):
    while 1 < 2:
        time.sleep(15)
        try:
            response = fmc.deployment.deployabledevices.get(name=device['hostname'])
        except:
            return

def creation(device):
    payload = {
        #"hostName": device['ip_address'],
        "type": "Device",
        "name": device['hostname'],
        "regKey": device['register_key'],
        "accessPolicy": {
          "name": set_dict['acp_name'],
          "id": acp_id,
          "type": "AccessPolicy"
        },
        "license_caps": [
          "BASE"
        ],
        "natID": device['nat_id'],
    }
    fmc.device.devicerecord.create(data=payload)

print_header('Add FTD to FMC')
for device in device_dict:
    print_action(device['hostname'])
    if pre_check(device) == "exist":
        print_skip()
    else:
        creation(device)
        if post_check(device) == "exist":
            check_deploying(device)
            print_status("Deploying")
            check_deployed(device)
            print_pass()
        else:
            print_fail()