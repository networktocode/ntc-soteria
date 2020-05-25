from acl_auditor.helpers import create_acl_from_yaml, read_file, read_yaml

expected_generated_acl = """hostname test-device
ip access-list acl-example
  10 deny ip 10.0.0.0/8 8.8.8.8/32 
  20 permit ip 11.36.216.176/32 11.36.216.0/24 
  30 permit tcp 10.36.176.0/24 11.20.0.0/16 range 1000 20000
  40 deny ip any any"""


def test_create_acl():
    generated_acl = create_acl_from_yaml(
        "tests/test_flows.yml", "test-device", "acl-example"
    )
    print(generated_acl)
    assert expected_generated_acl == generated_acl


def test_read_file():
    text_file = read_file("tests/test_config.cfg")
    assert type(text_file == str)


def test_read_yaml():
    yaml_file = read_yaml("tests/test_flows.yml")
    assert (type(yaml_file) == list) or (type(yaml_file) == dict)
