import os
import re
from netmiko import ConnectHandler

key_path = os.path.expanduser("~/.ssh/id_rsa")

devices = [
    {
        "device_type": "cisco_ios",
        "host": "172.31.124.4",  
        "username": "admin",
        "use_keys": True,
        "key_file": key_path,
        "conn_timeout": 60,
        "auth_timeout": 60,
        "fast_cli": False,
        "global_delay_factor": 3,  
        "disabled_algorithms": {"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]} 
    },
    {
        "device_type": "cisco_ios",
        "host": "172.31.124.5", 
        "username": "admin",
        "use_keys": True,
        "key_file": key_path,
        "conn_timeout": 60,
        "auth_timeout": 60,
        "fast_cli": False,
        "global_delay_factor": 3,
        "disabled_algorithms": {"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]} 
    }
]

for device in devices:
    try:
        print(f"\n================ Connecting to {device['host']} ================")
        net_connect = ConnectHandler(**device)
        hostname = net_connect.find_prompt().replace("#", "")
        
        show_ver = net_connect.send_command("show version")
        
        uptime_pattern = r"(?:uptime is\s+)(.+)"
        uptime_match = re.search(uptime_pattern, show_ver)
        uptime = uptime_match.group(1).strip() if uptime_match else "Unknown"
        
        print(f"Device: {hostname}")
        print(f"Uptime: {uptime}")
        print("-" * 50)
        
        show_ip_brief = net_connect.send_command("show ip interface brief")
        
        active_interface_pattern = r"^([A-Za-z0-9./]+)\s+([0-9.]+)\s+\w+\s+\w+\s+up\s+up"
        
        print("Active Interfaces:")
        print(f"{'Interface':<20} {'IP Address':<15}")
        print(f"{'---------':<20} {'----------':<15}")
        
        for line in show_ip_brief.splitlines():
            match = re.search(active_interface_pattern, line)
            if match:
                interface_name = match.group(1)
                ip_address = match.group(2)
                print(f"{interface_name:<20} {ip_address:<15}")
                
        net_connect.disconnect()
        
    except Exception as e:
        print(f" Failed to connect or process {device['host']}: {e}")

print("\n--- Process Completed! ---")