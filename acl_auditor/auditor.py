import argparse
import logging
import os

from dotenv import load_dotenv
from helpers import create_acl_from_yaml, read_file
from pybatfish.client.commands import *
from pybatfish.datamodel.flow import HeaderConstraints, PathConstraints
from pybatfish.question import bfq
from pybatfish.question.question import load_questions

load_dotenv()

logging.getLogger("pybatfish").setLevel(logging.CRITICAL)


class DeviceFlows:
    def __init__(self, config_file, flows_file, acl_name, hostname, batfish_host):
        self.init_session(batfish_host)
        self.config_file = config_file
        self.flows_file = flows_file
        self.hostname = hostname
        self.acl_name = acl_name

    def init_session(self, batfish_host):
        bf_session.host = batfish_host
        load_questions()

    def _create_base_snapshot(self):
        bf_session.init_snapshot_from_text(
            self.config_file, snapshot_name="base", overwrite=True
        )

    def _create_reference_snapshot(self):
        platform = "juniper-srx"
        reference_acl = create_acl_from_yaml(flows_file, self.hostname, self.acl_name, platform)
        bf_session.init_snapshot_from_text(
            reference_acl,
            platform=platform,
            snapshot_name="reference",
            overwrite=True,
        )

    def compare_filters(self):
        self._create_base_snapshot()
        self._create_reference_snapshot()
        self.answer = bfq.compareFilters().answer(
            snapshot="base", reference_snapshot="reference"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batfish Shell")
    parser.add_argument("-c", "--config", help="config", required=True)
    parser.add_argument("-f", "--flows", help="flows", required=True)
    parser.add_argument("-a", "--acl_name", help="acl_name", required=True)
    args = vars(parser.parse_args())

    config_file = read_file(args["config"])
    flows_file = args["flows"]
    acl_name = args["acl_name"]

    batfish_host = os.getenv("BATFISH_SERVICE_HOST")

    device_flows = DeviceFlows(config_file, flows_file, acl_name, "fw1", batfish_host)
    device_flows.compare_filters()
    print(device_flows.answer.frame())
