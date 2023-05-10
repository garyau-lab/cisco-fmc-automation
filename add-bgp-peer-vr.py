import time
import yaml, json, csv
from API_call_library import *
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = fmc_api(fmc_hostname=set_dict['fmc_hostname'], fmc_username=set_dict['fmc_username'], fmc_password=set_dict['fmc_password'], ftd_hostname=set_dict['ftd_hostname'])

# Read CSV file as an array of dictionary
intf_dict = []
with open('fmc-interface.csv') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)
    for row in csv_reader:
        row_data = {key: value for key, value in zip(headers, row)}
        intf_dict.append(row_data)


# BGP API support in FMC v7.1 or over, but there are some limitations observed even in the latest versions (v7.2.3 and v7.3).
# 1. At neighborGeneral level, the option "enableAddress" is not available. Which means new added BGP neighour cannot be enabled via API.
# 2. At neighborGeneral level, the option "fallOverBFD" doesn't work as expected.
# 3. At neighborRoutes level, the option "Generate default routes" is not available.

def pre_check(bgp):
    try:
        object_id = fmc.get_bgp_vr(vr_name=bgp['vn_name'])['items'][0]['id']
        response = fmc.get_bgp_vr_obj(vr_name=bgp['vn_name'], objectId=object_id)
        for i in response['addressFamilyIPv4']['neighbors']:
            if i['ipv4Address'] == bgp['bgp_peer']:
                return("exist")
    except:
        return

def post_check(bgp):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(bgp) == "exist":
            return ("exist")

def creation(bgp):
    payload = {
      "addressFamilyIPv4": {
        "neighbors": [
          {
            "remoteAs": "200",
            "neighborGeneral": {
              "fallOverBFD": "MULTI_HOP"
            },
            "neighborHaMode": {
              "disable": False
            },
            "ipv4Address": bgp['bgp_peer']
          }
        ]
      }
    }
    fmc.add_bgp_vr(vr_name=bgp['vn_name'], payload=payload)

print_header('Add BGP peer for Virtual Router')
for bgp in intf_dict:
    if bgp['bgp_peer'] != "":
        print_action(bgp['vn_name']+" ["+bgp['bgp_peer']+"]")
        if pre_check(bgp) == "exist":
            print_skip()
        else:
            creation(bgp)
            if post_check(bgp) == "exist":
                print_pass_custom("Partially completed")
            else:
                print_fail()