import yaml


def read_file(filename):
    with open(filename, "r") as f:
        file = f.read()
    return file


def write_file(filename, data):
    with open(filename, "w") as f:
        f.write(data)


def read_yaml(filename):
    with open(filename) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def create_acl_from_yaml(filename, hostname, filter_name, platform):
    reference_flows = read_yaml(filename)
    try:
        generate_acl_syntax = globals()[f"generate_acl_syntax_{platform}"]
    except KeyError:
        raise ValueError("Unknown platform {}".format(platform))

    return generate_acl_syntax(
        reference_flows=reference_flows,
        hostname=hostname,
        filter_name=filter_name,
    )


def generate_acl_syntax_cisco_nx(reference_flows=None, hostname=None, filter_name=None):
    """
    Turns the list of reference flows into an NXOS config file with the provided hostname and filter_name.
    """
    acl_lines = [
        "hostname {}".format(hostname),
        "ip access-list {}".format(filter_name),
    ]
    seq_number = 10

    for flow in reference_flows:
        dest_port = (
            "range {}".format(" ".join(flow["dest_port"].split("-")))
            if "dest_port" in flow and "-" in flow["dest_port"]
            else flow.get("dest_port", "")
        )

        acl_lines.append(
            "  {} {} {} {} {} {}".format(
                seq_number,
                flow["action"],
                flow["proto"],
                flow["source_ip"],
                flow.get("dest_ip", ""),
                dest_port,
            )
        )
        seq_number += 10
    acl_lines.append("  {} deny ip any any".format(seq_number))
    return "\n".join(acl_lines)


def generate_acl_syntax_juniper_srx(
    reference_flows=None, hostname=None, filter_name=None
):
    """
    Turns the list of reference flows into an SRX config file with the provided hostname and filter_name.
    """
    acl_lines = [
        "set system host-name {}".format(hostname),
    ]
    term_number = 1

    for flow in reference_flows:
        acl_lines.extend(_generate_acl_term_juniper_srx(flow, filter_name, term_number))
        term_number += 1

    acl_lines.append(
        "set firewall family inet filter {} term default-deny then discard".format(
            filter_name, term_number
        )
    )
    return "\n".join(acl_lines)


def _generate_acl_term_juniper_srx(reference_flow, filter_name, term_number):
    term_lines = []
    term_name = _get_term_name(reference_flow, term_number)
    if "source_ip" in reference_flow:
        term_lines.append(
            "set firewall family inet filter {} term {} from source-address {}".format(
                filter_name, term_name, reference_flow["source_ip"]
            )
        )
    if "dest_ip" in reference_flow:
        term_lines.append(
            "set firewall family inet filter {} term {} from destination-address {}".format(
                filter_name, term_name, reference_flow["dest_ip"]
            )
        )

    if "proto" in reference_flow and reference_flow["proto"] != "ip":
        term_lines.append(
            "set firewall family inet filter {} term {} from protocol {}".format(
                filter_name, term_name, reference_flow["proto"]
            )
        )

    if "source_port" in reference_flow:
        term_lines.append(
            "set firewall family inet filter {} term {} from source-port {}".format(
                filter_name, term_name, reference_flow["source_port"]
            )
        )

    if "dest_port" in reference_flow:
        term_lines.append(
            "set firewall family inet filter {} term {} from destination-port {}".format(
                filter_name, term_name, reference_flow["dest_port"]
            )
        )

    action = (
        "accept"
        if "action" not in reference_flow or reference_flow["action"] == "permit"
        else "discard"
    )

    term_lines.append(
        "set firewall family inet filter {} term {} then {}".format(
            filter_name, term_name, action
        )
    )

    return term_lines


def _get_term_name(reference_flow, term_number):
    return '"{} ({} {} {} {} {} {})"'.format(
        reference_flow.get("name", "flow{}".format(term_number)),
        reference_flow.get("source_ip", "any"),
        reference_flow.get("source_port", "any"),
        reference_flow.get("dest_ip", "any"),
        reference_flow.get("dest_port", "any"),
        reference_flow.get("proto", "ip"),
        reference_flow.get("action", "accept"),
    )