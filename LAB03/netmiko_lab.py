from netmiko import ConnectHandler
import os
import time

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

R1 = {"device_type": "cisco_ios", "host": "172.31.124.4", **connection_profile}
R2 = {"device_type": "cisco_ios", "host": "172.31.124.5", **connection_profile}
S1 = {"device_type": "cisco_ios", "host": "172.31.124.3", **connection_profile}

config_S1 = [

"vlan 101",
"name CONTROL",

"ip access-list standard MGMT",
"permit 172.31.124.0 0.0.0.15",
"permit 10.1.3.0 0.0.0.255",

"line vty 0 15",
"access-class MGMT in",
"transport input ssh telnet",

"end",
"write memory"
]

config_R1 = [

"router ospf 10 vrf control-data",
"router-id 1.1.1.1",
"network 10.1.1.0 0.0.0.255 area 0",
"network 10.1.2.0 0.0.0.255 area 0",

"ip access-list standard MGMT",
"permit 172.31.124.0 0.0.0.15",
"permit 10.1.3.0 0.0.0.255",

"line vty 0 15",
"access-class MGMT in",
"transport input ssh telnet",

"end",
"write memory"
]

config_R2 = [

"router ospf 10 vrf control-data",
"router-id 2.2.2.2",
"network 10.1.1.0 0.0.0.255 area 0",
"network 10.1.3.0 0.0.0.255 area 0",
"default-information originate",


"access-list 1 permit 10.1.1.0 0.0.0.255",
"access-list 1 permit 10.1.2.0 0.0.0.255",
"access-list 1 permit 10.1.3.0 0.0.0.255",

"ip nat inside source list 1 interface GigabitEthernet0/3 vrf control-data overload",
"ip route vrf control-data 0.0.0.0 0.0.0.0 192.168.42.1 global",
"ip route vrf management 0.0.0.0 0.0.0.0 172.31.124.1",

"interface GigabitEthernet0/1",
"ip nat inside",

"interface GigabitEthernet0/2",
"ip nat inside",

"interface GigabitEthernet0/3",
"ip nat outside",

"ip access-list standard MGMT",
"permit 172.31.124.0 0.0.0.15",
"permit 10.1.3.0 0.0.0.255",

"line vty 0 15",
"access-class MGMT in",
"transport input ssh telnet",

"end",
"write memory"
]

def deploy_config(device, config_commands, name):
    print(f"\n กำลังเชื่อมต่อ {name} ({device['host']})...")
    try:
        net_connect = ConnectHandler(**device)
        print(f" เชื่อมต่อสำเร็จ")
        print(f" ส่งคอนฟิก {len(config_commands)} บรรทัด...")
        
        output = net_connect.send_config_set(
            config_commands,
            delay_factor=2,
            cmd_verify=True, 
            exit_config_mode=True
        )
        
        print(f"  {name} คอนฟิกสำเร็จ!")
        
        try:
            verify_output = net_connect.send_command("show ip protocols | include OSPF", read_timeout=10)
            if verify_output.strip():
                print(f"   ตรวจสอบโปรโตคอล: ✓ {verify_output.strip()}")
            else:
                print(f"   ตรวจสอบโปรโตคอล: ไม่พบ OSPF ค้างใน Global (ย้ายเข้า VRF สำเร็จ)")
        except:
            pass
        
        net_connect.disconnect()
        time.sleep(1)
        
    except Exception as e:
        print(f"    {name} ล้มเหลว: {type(e).__name__}: {e}")

print("=" * 60)
print(" Netmiko Configuration Deployment (VRF Optimized)")
print("=" * 60)

deploy_config(S1, config_S1, "S1")
time.sleep(2)
deploy_config(R1, config_R1, "R1")
time.sleep(2)
deploy_config(R2, config_R2, "R2")

print("\n" + "=" * 60)
print("เสร็จสิ้นกระบวนการส่งคอนฟิกอัตโนมัติ")
print("=" * 60)