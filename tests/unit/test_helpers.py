from acl_auditor.helpers import create_acl_from_yaml, read_file, read_yaml

expected_generated_acl_cisco_nx = """hostname test-device
ip access-list acl-example
  10 deny ip 10.0.0.0/8 8.8.8.8/32 
  20 permit ip 11.36.216.176/32 11.36.216.0/24 
  30 permit tcp 10.36.176.0/24 11.20.0.0/16 range 1000 20000
  40 deny ip any any"""


expected_generated_acl_juniper_srx = """set system host-name test-device
set firewall family inet filter acl-example term to-google-dns from source-address 10.0.0.0/8
set firewall family inet filter acl-example term to-google-dns from destination-address 8.8.8.8/32
set firewall family inet filter acl-example term to-google-dns then discard
set firewall family inet filter acl-example term from-11-36-216-176 from source-address 11.36.216.176/32
set firewall family inet filter acl-example term from-11-36-216-176 from destination-address 11.36.216.0/24
set firewall family inet filter acl-example term from-11-36-216-176 then accept
set firewall family inet filter acl-example term term3-from-10.36.176.0/24-to-11.20.0.0/16 from source-address 10.36.176.0/24
set firewall family inet filter acl-example term term3-from-10.36.176.0/24-to-11.20.0.0/16 from destination-address 11.20.0.0/16
set firewall family inet filter acl-example term term3-from-10.36.176.0/24-to-11.20.0.0/16 from protocol tcp
set firewall family inet filter acl-example term term3-from-10.36.176.0/24-to-11.20.0.0/16 from destination-port 1000-20000
set firewall family inet filter acl-example term term3-from-10.36.176.0/24-to-11.20.0.0/16 then accept
set firewall family inet filter acl-example term term4-default-deny then discard"""


def test_create_acl_cisco_nx():
    generated_acl = create_acl_from_yaml(
        "tests/test_flows.yml", "test-device", "acl-example", "cisco-nx"
    )
    print(generated_acl)
    assert expected_generated_acl_cisco_nx == generated_acl


def test_create_acl_juniper_srx():
    generated_acl = create_acl_from_yaml(
        "tests/test_flows.yml", "test-device", "acl-example", "juniper-srx"
    )
    print(generated_acl)
    assert expected_generated_acl_juniper_srx == generated_acl


def test_read_file():
    text_file = read_file("tests/test_config.cfg")
    assert type(text_file == str)


def test_read_yaml():
    yaml_file = read_yaml("tests/test_flows.yml")
    assert (type(yaml_file) == list) or (type(yaml_file) == dict)
