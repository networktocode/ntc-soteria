import re
from jinja2 import Template
from helpers import read_file, write_file
from tabulate import tabulate

COMPARE_RESULTS_COLUMN_NAMES = [
    "Implemented Node",
    "Implemented Filter Name",
    "Implemented Flow Index",
    "Implemented Flow Content",
    "Implemented Flow Action",
    "Reference Flow Index",
    "Reference Flow Content",
]

COMPARE_RESULTS_COLUMN_ORDER = [
    "Reference Flow Index",
    "Reference Flow Content",
    "Implemented Flow Action",
    "Implemented Flow Index",
    "Implemented Flow Content",
    "Implemented Node",
    "Implemented Filter Name",
]

COMPARE_RESULTS_COLUMN_NAMES = [
    "Sources",
    "Unreachable Line",
    "Unreachable Line Action",
    "Blocking Lines",
    "Different Action",
    "Reason",
    "Additional Info"
]

def format_html_table(html):
    formatted_html = re.sub(r"<(table|tr).*?>", r"<\g<1>>", html)
    return re.sub(
        r"<(table).*?>", r"<\g<1> class='table table-sm'>", formatted_html,
    )


def add_html_errors_pd_frame(df):
    warning_html = """<span class="material-icons" style="color:red;font-size: 20px;">\
        error_outline\
            </span>"""
    df.insert(0, "", "")
    df[""] = warning_html


def format_df(df, column_names, column_order, sort_by_column):
    # replace string value
    df = df.replace(["End of ACL"], "No Match")
    # rename columns
    df.columns = column_names
    # reorder columns
    df = df[column_order]
    # sort by column
    return df.sort_values(sort_by_column)


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

def generate_html_report(
    compare_results, unreachable_results, reference_flows
):
    # compare_results.frame().columns = COMPARE_RESULTS_COLUMN_NAMES
    compare_results = format_df(
        compare_results.frame(),
        COMPARE_RESULTS_COLUMN_NAMES,
        COMPARE_RESULTS_COLUMN_ORDER,
        "Reference Flow Index",
    )
    add_html_errors_pd_frame(compare_results)
    add_html_errors_pd_frame(unreachable_results.frame())

    html_compare_results = format_html_table(
        compare_results.to_html(index=False, escape=False)
    )
    html_unreachable_results = format_html_table(
        unreachable_results.frame().to_html(index=False, escape=False)
    )

    rendered_report = render_report(
        "./acl_auditor/report.j2",
        html_compare_results,
        html_unreachable_results,
        reference_flows,
    )

    write_file("data/report.html", rendered_report)


def display_compare_results(results):
    results = format_df(
        results.frame(),
        COMPARE_RESULTS_COLUMN_NAMES,
        COMPARE_RESULTS_COLUMN_ORDER,
        "Reference Flow Index",
    )
    print(tabulate(results, headers="keys", tablefmt="psql", showindex=False))


def display_unreachable_results(results):
    print(
        tabulate(
            results.frame(), headers="keys", tablefmt="psql", showindex=False
        )
    )



