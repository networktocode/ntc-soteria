from pybatfish.client.commands import *
from pybatfish.question.question import load_questions
import argparse
import logging

from pybatfish.client.commands import *
from pybatfish.datamodel.flow import HeaderConstraints, PathConstraints
from pybatfish.question import bfq
from pybatfish.question.question import load_questions

from helpers import read_file, create_acl_from_yaml

logging.getLogger("pybatfish").setLevel(logging.CRITICAL)


class DeviceFlows:
    def __init__(self, config_file, flows_file, acl_name, hostname, batfish_ip):
        self.init_session(batfish_ip)
        self.config_file = config_file
        self.flows_file = flows_file
        self.hostname = hostname
        self.acl_name = acl_name

    def init_session(self, batfish_ip):
        bf_session.host = batfish_ip
        load_questions()

    def _create_base_snapshot(self):
        bf_session.init_snapshot_from_text(
            self.config_file, snapshot_name="base", overwrite=True
        )

    def _create_reference_snapshot(self):
        reference_acl = create_acl_from_yaml(flows_file, self.hostname, self.acl_name)
        bf_session.init_snapshot_from_text(
            reference_acl,
            platform="cisco-nx",
            snapshot_name="reference",
            overwrite=True,
        )

    def compare_filters(self):
        self._create_base_snapshot()
        self._create_reference_snapshot()
        answer = bfq.compareFilters().answer(
            snapshot="base", reference_snapshot="reference"
        )
        print(answer.frame())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batfish Shell")
    parser.add_argument("-c", "--config", help="config", required=True)
    parser.add_argument("-f", "--flows", help="flows", required=True)
    parser.add_argument("-a", "--acl_name", help="acl_name", required=True)
    args = vars(parser.parse_args())

    config_file = read_file(args["config"])
    flows_file = args["flows"]
    acl_name = args["acl_name"]

    device_flows = DeviceFlows(
        config_file, flows_file, acl_name, "fw1", "172.29.236.139"
    )
    device_flows.compare_filters()
