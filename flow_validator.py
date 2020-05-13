from pybatfish.client.commands import *
from pybatfish.question.question import load_questions
from pybatfish.datamodel.flow import (HeaderConstraints,
                                                 PathConstraints)
from pybatfish.question import bfq
import random
import sys
import pprint

NETWORK_NAME = "network1"
BATFISH_SERVICE_IP = "172.29.236.139"

bf_session.host = BATFISH_SERVICE_IP
load_questions()

print("[*] Initializing BASE_SNAPSHOT")

bf_set_network(NETWORK_NAME)
#bf_init_snapshot(SNAPSHOT_PATH, name=BASE_SNAPSHOT_NAME, overwrite=True)


def make_acl(reference_flows, hostname, filter_name):
    """
    Turns the list of reference flows into an NXOS config file with the provided hostname and filter_name.
    """
    acl_lines = ["hostname {}".format(hostname), 
                 "ip access-list {}".format(filter_name)]
    seq_number = 10
    for flow in reference_flows:
        acl_lines.append("  {} {}".format(seq_number, flow))
        seq_number += 10
    acl_lines.append("  {} deny ip any any".format(seq_number))
    return "\n".join(acl_lines)


reference_flows = [
   "deny ip 10.0.0.0/8 8.8.8.8/32",
   "permit ip 11.36.216.176/32 11.36.216.0/24",
   "permit ip 11.36.216.176/32 11.20.0.0/16",
   "permit ip 10.0.0.0/8 8.8.8.8/32",
   "permit tcp any 192.168.1.1/32 range 1000 2000",
]

implemented_flows = [
    "permit ip 10.0.1.0/24 8.8.8.8/32", 
    "permit ip 11.36.216.176/32 11.36.216.10/30",
    "permit ip 11.36.216.176/32 11.36.19.0/24",
    "permit tcp any 192.168.1.1/32 range 1000 2001",
]

nxos_acl_base = make_acl(implemented_flows, "rtr-with-acl", "acl_in")
bf_session.init_snapshot_from_text(nxos_acl_base, platform="cisco-nx", snapshot_name="base", overwrite=True)
print("== base flows ===")
pprint.pprint(nxos_acl_base)

print("===========")
nxos_acl_reference = make_acl(reference_flows, "rtr-with-acl", "acl_in")
bf_session.init_snapshot_from_text(nxos_acl_reference, platform="cisco-nx", snapshot_name="reference", overwrite=True)
print("=== reference flows ===")
pprint.pprint(nxos_acl_reference)

print("== results ==")
answer = bfq.compareFilters().answer(snapshot="base", reference_snapshot="reference")
print(answer.frame())
print("=============")
print("====  reference  ====  ")
pprint.pprint(nxos_acl_reference)
print("==== implemented ===")
pprint.pprint(nxos_acl_base)

