import argparse
import logging
import os
import sys

from dotenv import load_dotenv
from pybatfish.client.commands import bf_session
from pybatfish.question import bfq
from pybatfish.question.question import load_questions
from helpers import create_acl_from_yaml, read_file
from reporter import display_results, generate_html_report

load_dotenv()

logging.getLogger("pybatfish").setLevel(logging.CRITICAL)


class FlowAuditor:
    def __init__(self, config_file, flows_file, acl_name, batfish_host):
        self.init_session(batfish_host)
        self.config_file = config_file
        self.flows_file = flows_file
        self.acl_name = acl_name

    def init_session(self, batfish_host):
        bf_session.host = batfish_host
        load_questions()

    def _create_base_snapshot(self):
        bf_session.init_snapshot_from_text(
            self.config_file, snapshot_name="base", overwrite=True
        )

    def _get_hostname(self):
        batfish = bfq.nodeProperties().answer(snapshot="base").frame()
        if len(batfish) != 1:
            raise RuntimeError("Could not find a hostname in the config file")
        return batfish.iloc[0]["Node"]

    def _create_reference_snapshot(self, hostname):
        platform = "juniper_srx"
        reference_acl = create_acl_from_yaml(
            self.flows_file, hostname, self.acl_name, platform
        )
        bf_session.init_snapshot_from_text(
            reference_acl,
            platform=platform,
            snapshot_name="reference",
            overwrite=True,
        )
        batfish = bfq.initIssues().answer(snapshot="reference").frame()
        if len(batfish) != 0:
            print(
                "WARNING: Reference snapshot was not cleanly initialized, \
                    likely due to errors in input flow data. Context for \
                        problematic ACL lines (after conversion) \
                            is show below.",
                file=sys.stderr,
            )
            print(batfish, file=sys.stderr)
            print("\n", file=sys.stderr)

    def compare_filters(self):
        self._create_base_snapshot()
        hostname = self._get_hostname()
        self._create_reference_snapshot(hostname)
        return bfq.compareFilters().answer(
            snapshot="base", reference_snapshot="reference"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batfish Shell")
    parser.add_argument("-c", "--config", help="config", required=True)
    parser.add_argument("-f", "--flows", help="flows", required=True)
    parser.add_argument("-a", "--acl_name", help="acl_name", required=True)

    args = vars(parser.parse_args())

    config = read_file(args["config"])
    flows = args["flows"]
    acl = args["acl_name"]

    batfish_host = os.getenv("BATFISH_SERVICE_HOST")

    device_flows = FlowAuditor(config, flows, acl, batfish_host)
    results = device_flows.compare_filters()
    display_results(results)
    generate_html_report(results, read_file(flows))
