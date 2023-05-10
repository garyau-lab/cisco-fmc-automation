import time
import yaml, json, csv
from API_call_library import *
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = fmc_api(fmc_hostname=set_dict['fmc_hostname'], fmc_username=set_dict['fmc_username'], fmc_password=set_dict['fmc_password'], ftd_hostname=set_dict['ftd_hostname'])


def pre_check():
    try:
        object_id = fmc.get_bgpgeneralsettings()['items'][0]['id']
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
      "asNumber": set_dict['local_asnum']
    }
    fmc.add_bgp_general(payload=payload)

print_header('Configure BGP General Settings')
print_action("Local AS number: "+str(set_dict['local_asnum']))
if pre_check() == "exist":
    print_skip()
else:
    creation()
    if post_check() == "exist":
        print_pass()
    else:
        print_fail()