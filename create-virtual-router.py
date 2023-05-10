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
vr_list = []
for i in intf_dict:
    if i['vn_name'] not in vr_list and i['vn_name'] != "":
        vr_list.append(i['vn_name'])


def pre_check(vr):
    try:
        response = fmc.device.devicerecord.routing.virtualrouter.get(container_name=set_dict['ftd_hostname'],name=vr)
        return ("exist")
    except:
       return

def post_check(vr):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(vr) == "exist":
            return ("exist")

def creation(vr, interfaces):
    payload = {
        "name": vr,
        "interfaces": interfaces[1]
    }
    fmc.device.devicerecord.routing.virtualrouter.create(container_name=set_dict['ftd_hostname'],data=payload)

def construct_intf_list(vr):
    intf_list = []
    intf_payload = []
    for i in intf_dict:
        intf_payload_attrib = {}
        if i['vn_name'] == vr:
            intf_list.append(i['interface_name'])

            match i["interface_type"]:
                case "PhysicalInterface":
                    intf_id = fmc.device.devicerecord.physicalinterface.get(container_name=set_dict['ftd_hostname'],name=i['interface_name'])['id']
                case "SubInterface":
                    #fmc.object.host.create(data=payload)
                    subintf_vlanid = i['interface_name'].split(".")[1]
                    subinterfaces = fmc.device.devicerecord.subinterface.get(container_name=set_dict['ftd_hostname'])
                    for j in subinterfaces:
                        if j['subIntfId'] == int(subintf_vlanid):
                            intf_id = j['id']
                    
            intf_payload_attrib['type'] = i['interface_type']
            intf_payload_attrib['name'] = i['interface_name']
            intf_payload_attrib['id'] = intf_id
            intf_payload.append(intf_payload_attrib)
    return (intf_list, intf_payload)

print_header('Create Virtual Router')
for vr in vr_list:
    interfaces = construct_intf_list(vr)
    print_action(vr+" "+str(interfaces[0]).replace("'",""))
    if pre_check(vr) == "exist":
        print_skip()
    else:
        creation(vr, interfaces)
        if post_check(vr) == "exist":
            print_pass()
        else:
            print_fail()