import time
import yaml, json, csv
from fireREST import FMC
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

fmc = FMC(hostname=set_dict['fmc_hostname'], username=set_dict['fmc_username'], password=set_dict['fmc_password'], domain='Global')

# Read CSV file as an array of dictionary
route_dict = []
with open('fmc-static-route.csv') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)
    for row in csv_reader:
        row_data = {key: value for key, value in zip(headers, row)}
        route_dict.append(row_data)

# Extract Route for Global Routing Table
global_routes = []
for i in route_dict:
    if i['vn_name'] == "Global":
        global_routes.append(i) 


########### Main Apps ##########

def pre_check():
    net_namelist1 = selectedNetworks[0]
    net_namelist1.sort()
    routes = fmc.device.devicerecord.routing.ipv4staticroute.get(container_name=set_dict['ftd_hostname'])
    for i in routes:
        net_namelist2 = []
        for j in i['selectedNetworks']:
            net_namelist2.append(j['name'])
        net_namelist2.sort()                   
 
        if net_namelist1 == net_namelist2:
            return ("exist")
    return

def post_check():
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check() == "exist":
            return ("exist")

def creation(global_route):
    payload = {
        "interfaceName": global_route['outgoing_intf'],
        "selectedNetworks": selectedNetworks[1]
    }
    if global_route['next_hop'] != "":
        payload['gateway'] = {
            "literal": {
              "type": "Host",
              "value": "100.64.0.1"
            }
        }
    fmc.device.devicerecord.routing.ipv4staticroute.create(container_name=set_dict['ftd_hostname'], data=payload)

def construct_selectedNetworks(global_route):
    net_names = []
    net_payload = []
    networks =  global_route['network'].split(",")
    for i in networks:
        net_names.append(i)

        Net = {}
        try:
            net_id = fmc.object.networkaddress.get(name=i)['id']
        except:
            net_id = fmc.object.networkgroup.get(name=i)['id']
        Net['id'] = net_id
        net_payload.append(Net)
    return net_names, net_payload

print_header('Create Static Route for Global Routing Table')
for i in global_routes:
    selectedNetworks = construct_selectedNetworks(i)

    net_name_list = str(selectedNetworks[0]).replace("'","")
    print ("- Global "+net_name_list)
    print_action_l2("Interface: "+i['outgoing_intf'])

    if pre_check() == "exist":
        print_skip()
    else:
        creation(i)
        if post_check() == "exist":
            print_pass()
        else:
            print_fail()