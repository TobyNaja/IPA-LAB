import pytest
from textfsmlab import short_port_name, generate_description

# ---------- short_port_name() ----------

def test_short_gigabit():
    assert short_port_name("GigabitEthernet0/1") == "G0/1"

def test_short_gig():
    assert short_port_name("Gig 0/2") == "G0/2"

def test_short_fast():
    assert short_port_name("FastEthernet0/3") == "F0/3"

def test_short_ethernet():
    assert short_port_name("Ethernet1") == "E1"

def test_short_none():
    assert short_port_name(None) == ""

def test_short_empty():
    assert short_port_name("") == ""

# ---------- generate_description() ----------

def test_r2_wan():
    assert generate_description("R2", "Gig 0/3") == "Connect to WAN"

def test_s1_pc():
    assert generate_description("S1", "Gig 0/3") == "Connect to PC"

def test_neighbor_numeric_port():
    neighbor = {
        "neighbor_name": "R2-P.lab.local",
        "neighbor_interface": "0/2"
    }

    assert generate_description(
        "S1",
        "Gig 0/1",
        neighbor
    ) == "Connect to G0/2 of R2-P"

def test_neighbor_full_interface():
    neighbor = {
        "neighbor_name": "R1-P.lab.local",
        "neighbor_interface": "GigabitEthernet0/1"
    }

    assert generate_description(
        "R2",
        "Gig 0/1",
        neighbor
    ) == "Connect to G0/1 of R1-P"

def test_neighbor_destination_host():
    neighbor = {
        "destination_host": "S1.lab.local",
        "neighbor_interface": "0/1"
    }

    assert generate_description(
        "R1",
        "Gig 0/0",
        neighbor
    ) == "Connect to G0/1 of S1"

def test_neighbor_device_id():
    neighbor = {
        "device_id": "CORE.lab.local",
        "neighbor_interface": "Gig0/0"
    }

    assert generate_description(
        "R1",
        "Gig 0/0",
        neighbor
    ) == "Connect to G0/0 of CORE"

def test_neighbor_hostname():
    neighbor = {
        "hostname": "EDGE.lab.local",
        "neighbor_interface": "Gig0/2"
    }

    assert generate_description(
        "R1",
        "Gig 0/0",
        neighbor
    ) == "Connect to G0/2 of EDGE"

def test_neighbor_host():
    neighbor = {
        "host": "SW1.lab.local",
        "neighbor_interface": "Gig0/5"
    }

    assert generate_description(
        "R1",
        "Gig 0/0",
        neighbor
    ) == "Connect to G0/5 of SW1"

def test_unknown_neighbor():
    neighbor = {}

    assert generate_description(
        "R1",
        "Gig 0/0",
        neighbor
    ) == "Configured by Automation"

def test_neighbor_unknown_name():
    neighbor = {
        "neighbor_interface": "0/0"
    }

    assert generate_description(
        "R1",
        "Gig 0/0",
        neighbor
    ) == "Connect to G0/0 of Unknown"

def test_no_neighbor():
    assert generate_description(
        "R1",
        "Gig 0/0"
    ) == "Configured by Automation"