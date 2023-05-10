import time
import yaml, json, csv
from fireREST import FMC
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = FMC(hostname=set_dict['fmc_hostname'], username=set_dict['fmc_username'], password=set_dict['fmc_password'], domain='Global')


def pre_check():
    try:
        fmc.policy.accesspolicy.accessrule.get(container_name=set_dict['acp_name'], name=set_dict['acp_rule'])
        return ("exist")
    except:
        return

def post_check():
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check() == "exist":
            return ("exist")

def creation():
    payload = {
      "name": set_dict['acp_rule'],
      "type": "AccessRule",
      "enabled": True,
      "action": "ALLOW"
    }
    fmc.policy.accesspolicy.accessrule.create(container_name=set_dict['acp_name'],data=payload)

print_header('Create a Temporary Rule')
print_action(set_dict['acp_rule'])
if pre_check() == "exist":
    print_skip()
else:
    creation()
    if post_check() == "exist":
        print_pass()
    else:
        print_fail()
