#!/usr/bin/env python3

import logging
import sys
import click

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
        bf_session.host = "batfish"
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


@click.command()
@click.option(
    "--check",
    "-c",
    type=click.Choice(["compare", "unreachable", "all"]),
    required=True,
    help="Audit check type.",
)
@click.option("--device_config_file", "-d", type=click.Path(), help="Network device config file.")
@click.option("--reference_file", "-r", type=click.Path(), help="Flow reference file.")
@click.option("--acl_name", "-a", help="ACL name.")
@click.option("--output", "-o", type=click.Choice(["html"]), help="Report output format.")
def main(check, device_config_file, reference_file, acl_name, output):
    """NTC-Soteria - ACL Auditor"""
    filter_compare_results = str()
    unreachable_results = str()

    config = read_file(device_config_file)
    acl_auditor = ACLAuditor(config)

    if check in ["compare", "all"]:
        print("== Differential Comparision Audit ==")
        filter_compare_results = acl_auditor.get_acl_differences(
            reference_file, acl_name
        )
        display_compare_results(filter_compare_results)
    elif check == ["unreachable", "all"]:
        print("== Unreachable Audit ==")
        unreachable_results = acl_auditor.get_unreachable_lines()
        display_unreachable_results(unreachable_results)

    if check == all and output == "html":
        generate_html_report(
            filter_compare_results,
            unreachable_results,
            read_file(reference_file),
        )

    return_rc([filter_compare_results, unreachable_results])


if __name__ == "__main__":
    main()
