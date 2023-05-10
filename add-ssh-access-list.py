import time
import yaml, json, csv
from ftd_connector import ftd_connection
from print_report import *

with open('settings.yml') as info:
    set_dict = yaml.safe_load(info)

# Read CSV file as an array of dictionary
device_dict = []
with open('fmc-device.csv') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)
    for row in csv_reader:
        row_data = {key: value for key, value in zip(headers, row)}
        device_dict.append(row_data)


def pre_check(device):
    ip_list = device['ssh-access-list'].split(",")    
    my_device = {
        "ip": device['ip_address'],
        "username": set_dict['ftd_username'],
        "password": set_dict['ftd_password']
    }
    ftd = ftd_connection(**my_device)
    response = ftd.send_command_clish("show ssh-access-list")
    for i in ip_list:
        if i not in response:
            return
    return("exist")

def post_check(device):
    for i in range(set_dict['verify_retry_normal']):
        time.sleep(set_dict['verify_delay'])
        if pre_check(device) == "exist":
            return ("exist")

def creation(device):
    ip_list = device['ssh-access-list'].split(",")    
    my_device = {
        "ip": device['ip_address'],
        "username": set_dict['ftd_username'],
        "password": set_dict['ftd_password']
    }
    ftd = ftd_connection(**my_device)
    command = "configure ssh-access-list "+device['ssh-access-list']
    ftd.send_command_clish(command)

print_header('Add ssh-access-list to FTD')
for device in device_dict:
    print_action(device['hostname'])
    if pre_check(device) == "exist":
        print_skip()
    else:
        creation(device)
        if post_check(device) == "exist":
            print_pass()
        else:
            print_fail()
