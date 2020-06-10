from acl_auditor.helpers import create_acl_from_yaml, read_file, read_yaml

EXPECTED_GENERATED_ACL_CISCO_NX = """hostname test-device
ip access-list acl-example
  10 deny ip 10.0.0.0/8 8.8.8.8/32 
  20 permit ip 11.36.216.176/32 11.36.216.0/24 
  30 permit tcp 10.36.176.0/24 11.20.0.0/16 range 1000 20000
  40 deny ip any any""" # noqa


EXPECTED_GENERATED_ACL_JUNIPER_SRX = """set system host-name test-device
set firewall family inet filter acl-example term "to-google-dns (10.0.0.0/8 any 8.8.8.8/32 any ip deny)" from source-address 10.0.0.0/8
set firewall family inet filter acl-example term "to-google-dns (10.0.0.0/8 any 8.8.8.8/32 any ip deny)" from destination-address 8.8.8.8/32
set firewall family inet filter acl-example term "to-google-dns (10.0.0.0/8 any 8.8.8.8/32 any ip deny)" then discard
set firewall family inet filter acl-example term "from-11-36-216-176 (11.36.216.176/32 any 11.36.216.0/24 any ip permit)" from source-address 11.36.216.176/32
set firewall family inet filter acl-example term "from-11-36-216-176 (11.36.216.176/32 any 11.36.216.0/24 any ip permit)" from destination-address 11.36.216.0/24
set firewall family inet filter acl-example term "from-11-36-216-176 (11.36.216.176/32 any 11.36.216.0/24 any ip permit)" then accept
set firewall family inet filter acl-example term "flow3 (10.36.176.0/24 any 11.20.0.0/16 1000-20000 tcp permit)" from source-address 10.36.176.0/24
set firewall family inet filter acl-example term "flow3 (10.36.176.0/24 any 11.20.0.0/16 1000-20000 tcp permit)" from destination-address 11.20.0.0/16
set firewall family inet filter acl-example term "flow3 (10.36.176.0/24 any 11.20.0.0/16 1000-20000 tcp permit)" from protocol tcp
set firewall family inet filter acl-example term "flow3 (10.36.176.0/24 any 11.20.0.0/16 1000-20000 tcp permit)" from destination-port 1000-20000
set firewall family inet filter acl-example term "flow3 (10.36.176.0/24 any 11.20.0.0/16 1000-20000 tcp permit)" then accept
set firewall family inet filter acl-example term default-deny then discard""" # noqa


def test_create_acl_cisco_nx():
    generated_acl = create_acl_from_yaml(
        "tests/test_flows.yml", "test-device", "acl-example", "cisco-nx"
    )
    print(generated_acl)
    assert EXPECTED_GENERATED_ACL_CISCO_NX == generated_acl


def test_create_acl_juniper_srx():
    generated_acl = create_acl_from_yaml(
        "tests/test_flows.yml", "test-device", "acl-example", "juniper-srx"
    )
    print(generated_acl)
    assert EXPECTED_GENERATED_ACL_JUNIPER_SRX == generated_acl


def test_read_file():
    text_file = read_file("tests/test_config.cfg")
    assert isinstance(text_file, str)


def test_read_yaml():
    yaml_file = read_yaml("tests/test_flows.yml")
    assert isinstance(yaml_file, (dict, list))
