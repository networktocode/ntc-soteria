import yaml


def read_file(filename):
    with open(filename, "r") as f:
        file = f.read()
    return file


def read_yaml(filename):
    with open(filename) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def create_acl_from_yaml(filename, hostname, filter_name):
    reference_flows = read_yaml(filename)
    return generate_acl_syntax(
        reference_flows=reference_flows, hostname=hostname, filter_name=filter_name
    )


def generate_acl_syntax(reference_flows=None, hostname=None, filter_name=None):
    """
    Turns the list of reference flows into an NXOS config file with the provided hostname and filter_name.
    """
    acl_lines = [
        "hostname {}".format(hostname),
        "ip access-list {}".format(filter_name),
    ]
    seq_number = 10

    for flow in reference_flows:
        acl_lines.append(
            "  {} {} {} {} {} {}".format(
                seq_number,
                flow["action"],
                flow["proto"],
                flow["source_ip"],
                flow.get("dest_ip", ""),
                flow.get("dest_port", ""),
            )
        )
        seq_number += 10
    acl_lines.append("  {} deny ip any any".format(seq_number))
    return "\n".join(acl_lines)
