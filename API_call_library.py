import json
import requests
import urllib3

class fmc_api:
    def __init__(self, fmc_hostname, fmc_username, fmc_password, ftd_hostname):
        self.hostname = fmc_hostname
        self.username = fmc_username
        self.password = fmc_password
        self.ftd_hostname = ftd_hostname

        # Set login parameters
        self.url = "https://"+fmc_hostname
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Get token and prepare header for next call
        login_url = "/api/fmc_platform/v1/auth/generatetoken"
        login_response = requests.post(self.url+login_url, auth=(fmc_username, fmc_password), verify=False)
        token = login_response.headers.get('X-auth-access-token', default=None)

        # Set header for next call
        self.headers = {'Content-Type': 'application/json'}
        self.headers['X-auth-access-token'] = token
        
        # Get Domain ID
        domain_url = '/api/fmc_platform/v1/info/domain'
        domain_response = requests.get(self.url+domain_url, headers=self.headers, verify=False).json()
        self.domainUUID = domain_response['items'][0]['uuid']
        
        # Get Container ID
        ftd_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords'
        ftd_response = requests.get(self.url+ftd_url, headers=self.headers, verify=False).json()
        for i in ftd_response['items']:
            if i['name'] == self.ftd_hostname:
                self.ftdUUID = i['id']

    def get_netobj_id(self, netobj_name):
        try:
            apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/object/networkaddresses?filter="nameOrValue:{netobj_name}"'
            response = requests.get(self.url+apps_url, headers=self.headers, verify=False).json()
            return (response['items'][0]['id'])
        except:
            apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/object/networkgroups?filter="nameOrValue:{netobj_name}"'
            response = requests.get(self.url+apps_url, headers=self.headers, verify=False).json()
            return (response['items'][0]['id'])

    def get_vr_id(self, vr_name):
        containerUUID = self.ftdUUID
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters'
        response = requests.get(self.url+apps_url, headers=self.headers, verify=False).json()
        for i in response['items']:
            if i['name'] == vr_name:
                virtualrouterUUID = i['id']
                return (virtualrouterUUID)

    def get_vr_routes(self, vr_name):
        containerUUID = self.ftdUUID
        virtualrouterUUID = self.get_vr_id(vr_name)
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters/{virtualrouterUUID}/ipv4staticroutes'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())
    
    def get_vr_route(self, vr_name, vr_route_id):
        containerUUID = self.ftdUUID
        virtualrouterUUID = self.get_vr_id(vr_name)
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters/{virtualrouterUUID}/ipv4staticroutes/{vr_route_id}'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())

    def create_vr_route(self, vr_name, payload):
        containerUUID = self.ftdUUID
        virtualrouterUUID = self.get_vr_id(vr_name)
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters/{virtualrouterUUID}/ipv4staticroutes'
        requests.post(self.url+apps_url, headers=self.headers, data=json.dumps(payload), verify=False).json()

    def get_acp(self, acp_name):
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/policy/accesspolicies?name={acp_name}'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())

    def get_acp_obj(self, objectId):
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/policy/accesspolicies/{objectId}'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())

    def update_acp_obj(self, objectId, payload):
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/policy/accesspolicies/{objectId}'
        return (requests.put(self.url+apps_url, headers=self.headers, data=json.dumps(payload), verify=False).json())

    def get_bgpgeneralsettings(self):
        containerUUID = self.ftdUUID
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/bgpgeneralsettings'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())

    def get_bgpgeneralsettings_obj(self, objectId):
        containerUUID = self.ftdUUID
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/bgpgeneralsettings/{objectId}'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())

    def add_bgp_general(self, payload):
        containerUUID = self.ftdUUID
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/bgpgeneralsettings'
        requests.post(self.url+apps_url, headers=self.headers, data=json.dumps(payload), verify=False).json()

    def get_bgp_vr(self, vr_name):
        containerUUID = self.ftdUUID
        virtualrouterUUID = self.get_vr_id(vr_name)
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters/{virtualrouterUUID}/bgp'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())

    def get_bgp_vr_obj(self, vr_name, objectId):
        containerUUID = self.ftdUUID
        virtualrouterUUID = self.get_vr_id(vr_name)
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters/{virtualrouterUUID}/bgp/{objectId}'
        return (requests.get(self.url+apps_url, headers=self.headers, verify=False).json())

    def add_bgp_vr(self, vr_name, payload):
        containerUUID = self.ftdUUID
        virtualrouterUUID = self.get_vr_id(vr_name)
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters/{virtualrouterUUID}/bgp'
        requests.post(self.url+apps_url, headers=self.headers, data=json.dumps(payload), verify=False).json()

    def update_bgp_vr_obj(self, vr_name, objectId, payload):
        containerUUID = self.ftdUUID
        virtualrouterUUID = self.get_vr_id(vr_name)
        apps_url = f'/api/fmc_config/v1/domain/{self.domainUUID}/devices/devicerecords/{containerUUID}/routing/virtualrouters/{virtualrouterUUID}/bgp/{objectId}'
        requests.put(self.url+apps_url, headers=self.headers, data=json.dumps(payload), verify=False).json()

        