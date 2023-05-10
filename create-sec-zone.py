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

# Read VN list
sec_zones = []
for i in intf_dict:
    if i['security_zone'] not in sec_zones and i['security_zone'] != "":
        sec_zones.append(i['security_zone'])


def pre_check(sec_zone):
    try:
        response = fmc.object.securityzone.get(name=sec_zone)
        return ("exist")
    except:
       return

def post_check(sec_zone):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(sec_zone) == "exist":
            return ("exist")

def creation(sec_zone):
    payload = {
      "name": sec_zone,
      "interfaceMode": "ROUTED"
    }
    fmc.object.securityzone.create(data=payload)

print_header('Create Security Zone')
for sec_zone in sec_zones:
    print_action(sec_zone)
    if pre_check(sec_zone) == "exist":
        print_skip()
    else:
        creation(sec_zone)
        if post_check(sec_zone) == "exist":
            print_pass()
        else:
            print_fail()