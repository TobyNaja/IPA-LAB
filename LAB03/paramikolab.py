import paramiko
import os

devices = [
    {"name": "R0", "ip": "10.30.6.112"},
    {"name": "R1", "ip": "172.31.124.4"},
    {"name": "R2", "ip": "172.31.124.5"},
    {"name": "S0", "ip": "172.31.124.2"},
    {"name": "S1", "ip": "172.31.124.3"}
]

username = "admin"

key_path = os.path.expanduser("~/.ssh/id_rsa")

private_key = paramiko.RSAKey.from_private_key_file(key_path)

for device in devices:
    print(f"Connecting to {device['name']} ({device['ip']})...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=device["ip"], 
            username=username, 
            pkey=private_key,
            look_for_keys=False,
            allow_agent=False
        )
        
        print(f" Successfully connected to {device['name']}!")

        if device["name"] == "R0":
            print("Fetching running-config from R0...")
            stdin, stdout, stderr = ssh.exec_command("show running-config")
            config_data = stdout.read().decode('utf-8')
            
            with open("R0-running-config.txt", "w", encoding="utf-8") as f:
                f.write(config_data)
            print(" Saved R0-running-config.txt successfully!")
            
        ssh.close()
        
    except Exception as e:
        print(f"Failed to connect to {device['name']}: {e}")

print("\n--- All Done! ---")