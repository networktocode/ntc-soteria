import re
from jinja2 import Template
from helpers import read_file, write_file
from tabulate import tabulate

COMPARE_RESULTS_COLUMN_NAMES = [
    "Node",
    "Filter_Name",
    "Implemented_Line_Index",
    "Implemented_Line_Content",
    "Implemented_Line_Action",
    "Reference_Line_Index",
    "Reference_Line_Content",
]


def format_html_table(html):
    formatted_html = re.sub(r"<(table|tr).*?>", r"<\g<1>>", html)
    return re.sub(
        r"<(table).*?>", r"<\g<1> class='table table-sm'>", formatted_html,
    )


def format_pd_frame(df):
    warning_html = """<span class="material-icons" style="color:red;font-size: 20px;">\
        error_outline\
            </span>"""
    df.insert(0, "", "")
    df[""] = warning_html


def generate_html_report(
    compare_results, unreachable_results, reference_flows
):
    compare_results.frame().columns = COMPARE_RESULTS_COLUMN_NAMES
    format_pd_frame(compare_results.frame())
    format_pd_frame(unreachable_results.frame())

    html_compare_results = format_html_table(
        compare_results.frame().to_html(index=False,escape=False)
    )
    html_unreachable_results = format_html_table(
        unreachable_results.frame().to_html(index=False,escape=False)
    )

    rendered_report = render_report(
        "./acl_auditor/report.j2",
        html_compare_results,
        html_unreachable_results,
        reference_flows,
    )

    write_file("data/report.html", rendered_report)


def display_compare_results(results):
    results.frame().columns = COMPARE_RESULTS_COLUMN_NAMES
    print(
        tabulate(
            results.frame(), headers="keys", tablefmt="psql", showindex=False
        )
    )


def display_unreachable_results(results):
    print(
        tabulate(
            results.frame(), headers="keys", tablefmt="psql", showindex=False
        )
    )


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
