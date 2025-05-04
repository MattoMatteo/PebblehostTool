import pebblehostAPI
import sys
import os
import ipaddress
import winreg
import platform

def resource_path(relative_path):
    """Used to create a single executable file with pyinstaller except for config.json"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # PyInstaller executable
    else:
        base_path = os.path.abspath(".")  # Normal execution
    return os.path.join(base_path, relative_path)

def is_a_valid_ipv4_cidr(ip:str)->bool:
    try:
        ipaddress.IPv4Network(ip, strict=False)
        parts = ip.split(sep='/')
        if len(parts) == 2:
            cidr_part = parts[1]
            if not cidr_part.isdigit() or not 0 <= int(cidr_part) <= 32:
                return False
        elif len(parts) > 2:
            return False
        
        return True
    except ValueError:
        return False

class Firewall():
    def __init__(self):
        self.import_firewall_data()

    def import_firewall_data(self)->list[dict]:
        fileName = "my_firewall_rules.json"
        player_data = pebblehostAPI.fileManager_download(fileName)
        rules = pebblehostAPI.get_firewall_rules_info()
        firewall_data = []
        for rule in rules:
            player_rule = {}
            player_data.setdefault(str(rule["priority"]), "")
            player_rule["Name"] = player_data.get(str(rule["priority"]))

            player_rule["IP Address"] = rule["ip"]
            player_rule["Port"] = rule["port"]
            player_rule["Priority"] = rule["priority"]
            player_rule["Action"] = rule["allow"]
            firewall_data.append(player_rule)
        self.rules:list[dict] = firewall_data
        return firewall_data
    
    def get_all_ip(self)->list[str]:
        ips = []
        for rule in self.rules:
            ips.append(rule["IP Address"])
        return ips
            
    def add_rule(self, name:str, ip:str, port:str, action:str):
        self.rules.append({"Name": name, "IP Address": ip, "Port": port, "Priority": self._get_max_priority()+1, "Action": action})

    def edit_rule(self, row:int, name:str, ip:str, port:str, action:str):
        self.rules[row] = {"Name": name, "IP Address": ip, "Port": port, "Priority": self.rules[row]["Priority"], "Action": action}

    def delete_rule(self, index:int):
        priority = self.rules.pop(index)["Priority"]
        for rule in self.rules:
            if rule["Priority"] > priority:
                rule["Priority"] -=1
    
    def edit_attributeRule(self, index:int, name:str=None, ip:str=None, port:str=None, priority:int=None, action:str=None):
        if name:
            self.rules[index]["Name"] = name
        if ip:
            self.rules[index]["IP Address"] = ip
        if port:
            self.rules[index]["Port"] = port
        if priority:
            self.rules[index]["Priority"] = priority
        if action is not None:
            self.rules[index]["Action"] = action

    def _get_max_priority(self):
        max_priority = 0
        for rule in self.rules:
            if rule["Priority"] > max_priority:
                max_priority = rule["Priority"]
        return max_priority

    def upload_firewall_data(self):
        pebblehostAPI.delete_firewallRule()
        pebblehostAPI.add_firewallRule(ip="0.0.0.0/0", port=25578, priority=1, allow = False)
        priority = 2
        for rule in self.rules:
            if rule["IP Address"] != "0.0.0.0/0":
                rule["Priority"] = priority
                pebblehostAPI.add_firewallRule(ip=rule["IP Address"], port=int(rule["Port"]), priority=rule["Priority"], allow = rule["Action"])
                priority+=1
        #Upload del file jason
        file_to_upload = {}
        for rule in self.rules:
            file_to_upload[rule["Priority"]] = rule["Name"]
        pebblehostAPI.fileManager_uploadData(file_to_upload)

firewall = Firewall()

def windows_dark_mode_enabled():
    """Read the registry to see if Windows has dark theme for apps"""
    if not is_windows():
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0  # 0 = dark mode attivo
    except FileNotFoundError:
        return False

def is_windows():
    return platform.system().lower() == "windows"