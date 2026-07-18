import os
import re
import sys
from pprint import pprint
from netmiko import ConnectHandler


os.environ["NET_TEXTFSM"] = os.path.join(sys.prefix, "Lib", "site-packages", "ntc_templates", "templates")


key_path = os.path.expanduser("~/.ssh/id_rsa")


connection_profile = {
    "username": "admin",
    "use_keys": True,
    "key_file": key_path,
    "conn_timeout": 60,
    "auth_timeout": 60,
    "global_delay_factor": 3,
    "disabled_algorithms": {"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]}
}


devices = [
    {"name": "S1", "device_type": "cisco_ios", "host": "172.31.124.3", **connection_profile},
    {"name": "R1", "device_type": "cisco_ios", "host": "172.31.124.4", **connection_profile},
    {"name": "R2", "device_type": "cisco_ios", "host": "172.31.124.5", **connection_profile}
]


def short_port_name(port):
    if not port:
        return ""
    port = port.replace("GigabitEthernet", "G")
    port = port.replace("GigEthernet", "G")
    port = port.replace("Gig", "G")
    port = port.replace("FastEthernet", "F")
    port = port.replace("Fast", "F")
    port = port.replace("Ethernet", "E")
    return port.replace(" ", "")


def generate_description(device_name, local_port, neighbor=None):
    local_short = short_port_name(local_port)
    if device_name == "R2" and local_short == "G0/3":
        return "Connect to WAN"
    if device_name == "S1" and local_short == "G0/3":
        return "Connect to PC"
    if neighbor:
        remote_device = (
            neighbor.get("neighbor_name")
            or neighbor.get("neighbor")
            or neighbor.get("destination_host")
            or neighbor.get("device_id")
            or neighbor.get("hostname")
            or neighbor.get("host")
            or "Unknown"
        ).split(".")[0]


        remote_port = (
            neighbor.get("neighbor_interface")
            or neighbor.get("remote_port")
            or neighbor.get("port_id")
            or ""
        )


        if re.match(r"^\d+/\d+$", remote_port):
            remote_port = "G" + remote_port
        else:
            remote_port = short_port_name(remote_port)


        return f"Connect to {remote_port} of {remote_device}"
    return "Configured by Automation"


def main():
    print("🚀 Starting TextFSM & CDP Automation...")
    for device in devices:
        print(f"\n================ Connecting to {device['name']} ({device['host']}) ================")
        try:
            conn = device.copy()
            conn.pop("name")
            net_connect = ConnectHandler(**conn)


            cdp = net_connect.send_command("show cdp neighbors", use_textfsm=True)


            print("\n========== RAW TEXTFSM ==========")
            pprint(cdp)
            print("=================================\n")


            config = []


            if isinstance(cdp, list):
                for n in cdp:
                    local_port = (
                        n.get("local_interface")
                        or n.get("local_port")
                        or n.get("local_port_id")
                    )
                    if not local_port:
                        continue
                    desc = generate_description(device["name"], local_port, n)
                    print(f"📌 {local_port} -> {desc}")
                    config.extend([
                        f"interface {local_port}",
                        f"description {desc}"
                    ])


            if device["name"] == "S1":
                config.extend([
                    "interface GigabitEthernet0/2",
                    "description Connect to Ubuntu-Server-3"
                ])


            if device["name"] == "R2":
                config.extend([
                    "interface GigabitEthernet0/3",
                    "description Connect to WAN"
                ])


            if config:
                print("\nSending configuration...\n")
                print(net_connect.send_config_set(config))
                net_connect.save_config()
                print(f"\n✅ {device['name']} completed.")


            net_connect.disconnect()


        except Exception as e:
            print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
