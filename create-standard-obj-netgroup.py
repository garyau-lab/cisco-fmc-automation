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
        response = fmc.object.networkgroup.get(name=net_obj['object_name'])
        return ("exist")                
    except:
        return

def post_check(net_obj):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(net_obj) == "exist":
            return ("exist")

def creation(net_obj,literals):
    payload = {
        'name': net_obj['object_name'],
        'literals': literals,
    }
    fmc.object.networkgroup.create(data=payload)            

def construct_literals(net_obj):
    literals = []
    values = net_obj['value'].split(",")
    for value in values:
        literal_attr = {}
        value = value.replace("/32","")
        if "/" not in value:
            literal_attr['type'] = "Host"
        else:
            literal_attr['type'] = "Network"
        literal_attr['value'] = value
        literals.append(literal_attr)
    return (literals)

print_header('Create Standard NetworkGroup Object')
for net_obj in object_dict:
    if net_obj['override'] == "no" and net_obj['object_type'] == "NetworkGroup":
        literals = construct_literals(net_obj)
        print_action(net_obj['object_name']+" ["+net_obj['object_type']+" "+net_obj['value']+"]")
        if pre_check(net_obj) == "exist":
            print_skip()
        else:
            creation(net_obj,literals)
            if post_check(net_obj) == "exist":
                print_pass()
            else:
                print_fail()
