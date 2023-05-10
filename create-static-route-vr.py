import time
import yaml, json, csv
from API_call_library import *
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = fmc_api(fmc_hostname=set_dict['fmc_hostname'], fmc_username=set_dict['fmc_username'], fmc_password=set_dict['fmc_password'], ftd_hostname=set_dict['ftd_hostname'])

# Read CSV file as an array of dictionary
route_dict = []
with open('fmc-static-route.csv') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)
    for row in csv_reader:
        row_data = {key: value for key, value in zip(headers, row)}
        route_dict.append(row_data)

# Extract Route for Virtual Router
vr_route_dict = []
for i in route_dict:
    if i['vn_name'] != "Global":
        vr_route_dict.append(i)


########### Main Apps ##########

def pre_check(vr_route):
    net_namelist1 = selectedNetworks[0]
    net_namelist1.sort()

    routes = fmc.get_vr_routes(vr_name=vr_route['vn_name'])
    try:
        for i in routes['items']:
            net_namelist2 = []
            route = fmc.get_vr_route(vr_name=vr_route['vn_name'], vr_route_id=i['id'])
            for j in route['selectedNetworks']:
                net_namelist2.append(j['name'])
                net_namelist2.sort()                   

            if net_namelist1 == net_namelist2:
                return ("exist")
    except:
        return

def post_check(vr_route):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(vr_route) == "exist":
            return ("exist")

def creation(vr_route):
    payload = {
        "interfaceName": vr_route['outgoing_intf'],
        "selectedNetworks": selectedNetworks[1]
    }
    if vr_route['next_hop'] != "":
        payload['gateway'] = {
            "literal": {
              "type": "Host",
              "value": "100.64.0.1"
            }
        }
    fmc.create_vr_route(vr_name=vr_route['vn_name'],payload=payload)

def construct_selectedNetworks(vr_route):
    net_names = []
    net_payload = []
    networks = vr_route['network'].split(",")
    for i in networks:
        net_names.append(i)

        Net = {}
        Net['id'] = fmc.get_netobj_id(netobj_name=i)
        net_payload.append(Net)
    return net_names, net_payload


print_header('Create Static Route for Virtual Router')
for i in vr_route_dict:
    selectedNetworks = construct_selectedNetworks(i)

    net_name_list = str(selectedNetworks[0]).replace("'","")
    print ("- "+i['vn_name']+" "+net_name_list)
    print_action_l2("Interface: "+i['outgoing_intf'])

    if pre_check(i) == "exist":
        print_skip()
    else:
        creation(i)
        if post_check(i) == "exist":
            print_pass()
        else:
            print_fail()
