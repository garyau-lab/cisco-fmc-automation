import time
import yaml, json, csv
from fireREST import FMC
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = FMC(hostname=set_dict['fmc_hostname'], username=set_dict['fmc_username'], password=set_dict['fmc_password'], domain='Global')

def pre_check():
    try:
        acp_response = fmc.policy.accesspolicy.inheritancesettings.get(container_name=set_dict['acp_name'])
        if acp_response[0]['basePolicy']['name'] == set_dict['acp_parent']:
            return ("exist")
    except:
        return

def post_check():
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check() == "exist":
            return ("exist")

def creation():
    parent_resp = fmc.policy.accesspolicy.inheritancesettings.get(container_name=set_dict['acp_parent'])
    parent_id = parent_resp[0]['id']

    payload = fmc.policy.accesspolicy.inheritancesettings.get(container_name=set_dict['acp_name'])    
    payload[0]['basePolicy'] = {
        "name": set_dict['acp_parent'],
        "id": parent_id,
        "type": "AccessPolicy"
    }
    fmc.policy.accesspolicy.inheritancesettings.update(container_name=set_dict['acp_name'], data=payload[0])

print_header('Set Inheritance for Access Control Policy ')
print("- Policy name: "+set_dict['acp_name'])
print_action_l2("Parent name: "+set_dict['acp_parent'])

if pre_check() == "exist":
    print_skip()
else:
    creation()
    if post_check() == "exist":
        print_pass()
    else:
        print_fail()
