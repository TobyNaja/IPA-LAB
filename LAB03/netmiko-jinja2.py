from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, 'templates')

env = Environment(loader=FileSystemLoader(templates_dir))


key_path = os.path.expanduser("~/.ssh/id_rsa")


connection_profile = {
    "username": "admin",
    "use_keys": True,
    "key_file": key_path,
    "conn_timeout": 60,
    "auth_timeout": 60,
    "global_delay_factor": 2,
    "disabled_algorithms": {"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
}


devices_data = [
    {
        "name": "S1",
        "netmiko_spec": {"device_type": "cisco_ios", "host": "172.31.124.3", **connection_profile},
        "template": "s1_template.j2",
        "vars": {
            "ip_address": "10.1.3.2",
            "netmask": "255.255.255.0",
            "default_gateway": "10.1.3.1"
        }
    },
    {
        "name": "R1",
        "netmiko_spec": {"device_type": "cisco_ios", "host": "172.31.124.4", **connection_profile},
        "template": "r1_template.j2",
        "vars": {} 
    },
    {
        "name": "R2",
        "netmiko_spec": {"device_type": "cisco_ios", "host": "172.31.124.5", **connection_profile},
        "template": "r2_template.j2",
        "vars": {}
    }
]

env = Environment(loader=FileSystemLoader("templates"))

def deploy_with_jinja2():
    print("=" * 60)
    print(" Starting Refactored Netmiko-Jinja2 Deployment")
    print("=" * 60)

    for device in devices_data:
        name = device["name"]
        print(f"\n Processing configuration for {name}...")
        
        try:
            template = env.get_template(device["template"])
            rendered_config = template.render(device["vars"])
            
            config_commands = [line.strip() for line in rendered_config.splitlines() if line.strip()]
            
            print(f"    Connecting to {name} ({device['netmiko_spec']['host']})...")
            net_connect = ConnectHandler(**device["netmiko_spec"])
            print(f"    Connected via SSH")
            
            output = net_connect.send_config_set(
                config_commands,
                delay_factor=2,
                cmd_verify=True,
                exit_config_mode=False
            )
            
            print(f"    {name} configured and saved successfully with Jinja2!")
            net_connect.disconnect()
            time.sleep(2)
            
        except Exception as e:
            print(f"    Error at {name}: {type(e).__name__} -> {e}")

if __name__ == "__main__":
    deploy_with_jinja2()