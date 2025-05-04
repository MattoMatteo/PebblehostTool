import requests
from pathlib import Path
import utils
import sys
import json
import io

with open(utils.resource_path(str(Path("config.json")), internal_data = False), 'r', encoding='utf-8') as file:
    config = json.load(file)

pebbleAPI = config["pebbleAPI"]
server = config["server"]

host = "https://panel.pebblehost.com/"
headers = {
    'Authorization': f'Bearer {pebbleAPI}',
}

#Test api / server id

def check_internet():
    try:
        response = requests.get(host, timeout=5)
        return True
    except requests.ConnectionError:
        return False
    
def test_credentials()->bool:
    try:
        api_call = host + f"/api/client/servers/{server}"
        response = requests.get(api_call, headers=headers).json()
        return True
    except Exception as e:
        return False

#Client API

def get_publicIP():
    return requests.get(host + "/api/client/myip", headers={'Authorization': f'Bearer {pebbleAPI}', 'accept': 'text/plain'}).text

#Firewall API

def get_firewall_rules_info()->list[dict]:
    """
    Return a list of dict like:
    [{'id': 1867934, 'ip': '93.56.141.180', 'port': 25578, 'priority': 4, 'allow': True, 'is_tcpshield': None}, {....}, {...}]
    """
    api_call = host + f"/api/client/servers/{server}/firewall"
    headers["Accept"] = "application/json"
    response = requests.get(api_call, headers=headers)
    if response.status_code == 200:
        data = sorted([item['attributes'] for item in response.json()["data"]], key=lambda x: x['priority'])
        return data
    else:
        print(f"Errore: {response.status_code} - {response.text}")

def add_firewallRule(ip:str, port:int, priority:str, allow:bool):
    api_call = host + f"/api/client/servers/{server}/firewall"
    headers["Accept"] = "application/json"
    rule = {
                "ip": ip,
                "port": port,
                "priority": priority,
                "allow": allow
            }
    r = requests.post(url=api_call, headers=headers, json=rule)

def delete_firewallRule():
    actual_rules = get_firewall_rules_info()
    for rule in actual_rules:
        serverFirewall = rule["id"]
        api_call = host + f"/api/client/servers/{server}/firewall/{serverFirewall}"
        r = requests.delete(url=api_call, headers=headers)
        
#File Manager API

def fileManager_list():
    api_call = host + f"/api/client/servers/{server}/files/list/"
    headers["Accept"] = "application/json"
    r = requests.get(api_call, headers=headers)
    return r.json()

def fileManager_download(file:str)->dict:
    api_call = host + f"/api/client/servers/{server}/files/download"
    headers["Accept"] = "application/json"
    params = {"file_path": file}
    try:
        url = requests.get(api_call, headers=headers, params=params).json()['attributes']['url']
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return {}
    except ConnectionError:
        print("No connection!")
        sys.exit()

def fileManager_uploadData(rules:dict):
    """
    Rules must be a dict of ""{priority}" : "{name}"
    """
    api_call = host + f"/api/client/servers/{server}/files/upload"
    url = requests.get(api_call, headers=headers).json()['attributes']['url']

    json_str = json.dumps(rules)
    file_like = io.StringIO(json_str)

    files_to_upload = {'files': ('my_firewall_rules.json', file_like)}
    r = requests.post(url, files=files_to_upload)
    return r.status_code