from lib.helpers import create_acl_from_yaml

expected_generated_acl = """hostname test
ip access-list security-access-list
  10 deny ip 10.0.0.0/8 8.8.8.8/32 None
  20 permit ip 11.36.216.176/32 11.36.216.0/24 None
  30 permit tcp any 192.168.1.1/32 1000 2500
  40 deny ip any any"""

def test_create_acl():
    generated_acl = create_acl_from_yaml('tests/example_flows.yml')
    assert expected_generated_acl == generated_acl

