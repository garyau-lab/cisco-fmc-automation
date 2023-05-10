import time
import yaml, json, csv
from fireREST import FMC
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = FMC(hostname=set_dict['fmc_hostname'], username=set_dict['fmc_username'], password=set_dict['fmc_password'], domain='Global')

# Read CSV file as an array of dictionary
object_dict = []
with open('fmc-object.csv') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)
    for row in csv_reader:
        row_data = {key: value for key, value in zip(headers, row)}
        object_dict.append(row_data)

ftd_id = fmc.device.devicerecord.get(name=set_dict['ftd_hostname'])['id']

def pre_check(net_obj):
    try:
        response = fmc.object.host.get(name=net_obj['object_name'], override_target_id=ftd_id)
        return ("exist")
    except:
        return

def post_check(net_obj):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(net_obj) == "exist":
            return ("exist")

def creation(net_obj):
    obj_id = fmc.object.host.get(name=net_obj['object_name'])['id']
    payload = {
        "overrides": {
            "parent": {
                "id": obj_id
            },
            "target": {
                "id": ftd_id,
                "type": "Device"
            }
        },
        "value": net_obj['value'],
        "name": net_obj['object_name'],
        "id": obj_id
    }
    fmc.object.host.update(data=payload)

print_header('Add Entry into Overridable Host Object')
for net_obj in object_dict:
    if net_obj['override'] == "yes" and net_obj['object_type'] == "Host":
        print_action(net_obj['object_name']+" ["+set_dict['ftd_hostname']+" "+net_obj['value']+"]")
        if pre_check(net_obj) == "exist":
            print_skip()
        else:
            creation(net_obj)
            if post_check(net_obj) == "exist":
                print_pass()
            else:
                print_fail()
