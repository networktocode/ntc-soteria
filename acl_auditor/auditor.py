#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from pybatfish.client.commands import bf_session
from pybatfish.question import bfq
from pybatfish.question.question import load_questions
from helpers import create_acl_from_yaml, read_file, return_rc
from reporter import (
    display_compare_results,
    display_unreachable_results,
    generate_html_report,
)


logging.getLogger("pybatfish").setLevel(logging.CRITICAL)


class ACLAuditor:
    def __init__(self, config_file):
        bf_session.host = "127.0.0.1"
        load_questions()
        self.config_file = config_file

    def _create_base_snapshot(self):
        bf_session.init_snapshot_from_text(
            self.config_file, snapshot_name="base", overwrite=True
        )

    def _get_hostname(self):
        batfish_answer = bfq.nodeProperties().answer(snapshot="base").frame()
        if len(batfish_answer) != 1:
            raise RuntimeError("Could not find a hostname in the config file")
        return batfish_answer.iloc[0]["Node"]

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
        self.validate_reference_snapshot()

    def validate_reference_snapshot(self):
        batfish_issues = bfq.initIssues().answer(snapshot="reference").frame()
        if len(batfish_issues) != 0:
            print(
                "WARNING: Reference snapshot was not cleanly initialized, \
                    likely due to errors in input flow data. Context for \
                        problematic ACL lines (after conversion) \
                            is shown below.",
                file=sys.stderr,
            )
            print(batfish_issues, file=sys.stderr)
            print("\n", file=sys.stderr)

    def get_acl_differences(self, flows_file, acl_name):
        self.flows_file = flows_file
        self.acl_name = acl_name

        self._create_base_snapshot()
        self._create_reference_snapshot(self._get_hostname())

        return bfq.compareFilters().answer(
            snapshot="base", reference_snapshot="reference"
        )

    def get_unreachable_lines(self):
        self._create_base_snapshot()
        return bfq.filterLineReachability().answer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batfish ACL Auditor")
    parser.add_argument(
        "-c",
        "--check",
        help="check",
        required=True,
        choices=["compare", "unreachable", "all"],
    )
    parser.add_argument(
        "-d", "--device_config", help="device_config", required=False
    )
    parser.add_argument(
        "-r", "--reference_flows", help="reference_flows", required=False
    )
    parser.add_argument("-a", "--acl_name", help="acl_name", required=False)
    parser.add_argument("-o", "--output", help="output", choices=["html"])
    args = vars(parser.parse_args())

    config = read_file(args["device_config"])
    acl_auditor = ACLAuditor(config)
    filter_compare_results = str()
    unreachable_results = str()

    if args["check"] in ["compare", "all"] and (
        (not args["reference_flows"]) or (not args["acl_name"])
    ):
        parser.error("requires --reference_flows and --acl_name")
    elif args["check"] == "compare":
        reference_flows = args["reference_flows"]
        acl_name = args["acl_name"]

        filter_compare_results = acl_auditor.get_acl_differences(
            reference_flows, acl_name
        )

        display_compare_results(filter_compare_results)
    elif args["check"] == "unreachable":
        unreachable_results = acl_auditor.get_unreachable_lines()
        display_unreachable_results(unreachable_results)
    elif args["check"] == "all":
        reference_flows = args["reference_flows"]
        acl_name = args["acl_name"]

        filter_compare_results = acl_auditor.get_acl_differences(
            reference_flows, acl_name
        )

        unreachable_results = acl_auditor.get_unreachable_lines()
        print("-- Reference Comparision --")
        display_compare_results(filter_compare_results)
        print("-- Unreachable ACL Entries --")
        display_unreachable_results(unreachable_results)

    if args["output"] == "html" and args["check"] == "all":
        generate_html_report(
            filter_compare_results,
            unreachable_results,
            read_file(reference_flows),
        )

    return_rc([filter_compare_results, unreachable_results])
