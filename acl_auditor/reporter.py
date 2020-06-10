import re
from jinja2 import Template
from helpers import read_file, write_file

COLUMN_NAMES = [
    "Node",
    "Filter_Name",
    "Implemented_Line_Index",
    "Implemented_Line_Content",
    "Implemented_Line_Action",
    "Reference_Line_Index",
    "Reference_Line_Content",
]


def generate_html_report(results, reference_flows):
    results.frame().columns = COLUMN_NAMES

    html_results = results.frame().to_html()
    html_results = re.sub(r"<(table|tr).*?>", r"<\g<1>>", html_results)
    html_results = re.sub(
        r"<(table).*?>", r"<\g<1> class='table table-sm'>", html_results
    )

    rendered_report = render_report(
        "./acl_auditor/report.j2", html_results, reference_flows
    )

    write_file("data/report.html", rendered_report)


def display_results(results):
    results.frame().columns = COLUMN_NAMES
    print(results.frame())


def render_report(report_template_path, html_results, reference_flows):
    report_template = read_file(report_template_path)
    template = Template(report_template)
    return template.render(
        audit_results=html_results,
        reference_flows=reference_flows
    )
