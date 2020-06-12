import re
from jinja2 import Template
from helpers import read_file, write_file

COMPARE_COLUMN_NAMES = [
    "Node",
    "Filter_Name",
    "Implemented_Line_Index",
    "Implemented_Line_Content",
    "Implemented_Line_Action",
    "Reference_Line_Index",
    "Reference_Line_Content",
]


def generate_html_report(
    compare_results, unreachable_results, reference_flows
):
    compare_results.frame().columns = COMPARE_COLUMN_NAMES

    html_compare_results = compare_results.frame().to_html()
    html_compare_results = re.sub(
        r"<(table|tr).*?>", r"<\g<1>>", html_compare_results
    )
    html_compare_results = re.sub(
        r"<(table).*?>",
        r"<\g<1> class='table table-sm'>",
        html_compare_results,
    )

    html_unreachable_results = unreachable_results.frame().to_html()

    rendered_report = render_report(
        "./acl_auditor/report.j2",
        html_compare_results,
        html_unreachable_results,
        reference_flows,
    )

    write_file("data/report.html", rendered_report)


def display_compare_results(results):
    results.frame().columns = COMPARE_COLUMN_NAMES
    print(results.frame())


def display_unreachable_results(results):
    print(results.frame())


def render_report(
    report_template_path,
    html_compare_results,
    html_unreachable_results,
    reference_flows,
):
    report_template = read_file(report_template_path)
    template = Template(report_template)
    return template.render(
        unreachable_results=html_unreachable_results,
        compare_results=html_compare_results,
        reference_flows=reference_flows,
    )
