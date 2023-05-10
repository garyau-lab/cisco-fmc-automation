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


def pre_check(net_obj):
    try:
        match net_obj["object_type"]:
            case "Network":
                response = fmc.object.network.get(name=net_obj['object_name'])
                return ("exist")
            case "NetworkGroup":
                response = fmc.object.networkgroup.get(name=net_obj['object_name'])
                return ("exist")                
            case "Host":
                response = fmc.object.host.get(name=net_obj['object_name'])
                return ("exist")
    except:
        return

def post_check(net_obj):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(net_obj) == "exist":
            return ("exist")

def creation(net_obj):
    payload = {
        'name': net_obj['object_name'],
        "overridable": True,
    }
    match net_obj["object_type"]:
        case "Network":
            fmc.object.network.create(data=payload)
        case "NetworkGroup":
            fmc.object.networkgroup.create(data=payload)            
        case "Host":
            fmc.object.host.create(data=payload)

print_header('Create Overridable Object')
for net_obj in object_dict:
    if net_obj['override'] == "yes":
        print_action(net_obj['object_name']+" ["+net_obj['object_type']+"]")
        if pre_check(net_obj) == "exist":
            print_skip()
        else:
            creation(net_obj)
            if post_check(net_obj) == "exist":
                print_pass()
            else:
                print_fail()
