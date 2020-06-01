import re
from helpers import read_file, write_file
from jinja2 import Template

## Reference Flows
reference_flows = read_file("data/flows.yml")


def format_table(data):
    data = re.sub(r"<(table|tr).*?>", r"<\g<1>>", data)
    data = re.sub(r"<(table).*?>", r"<\g<1> class='table table-sm'>", data)
    data = re.sub(r"<th>Line_Index</th>", r"<th>Implemented_Line_Index</th>", data)
    data = re.sub(r"<th>Line_Content</th>", r"<th>Implemented_Line_Content</th>", data)
    data = re.sub(
        r"<th>Line_Line_Action</th>", r"<th>Implemented_Line_Action</th>", data
    )
    return data


def generate_report(report_template_path, audit_results, reference_flows):
    report_template = read_file(report_template_path)
    t = Template(report_template)

    audit_results = format_table(audit_results)

    return t.render(audit_results=audit_results, reference_flows=reference_flows)


## Audit Results
audit_results = '<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th></th>\n      <th>Node</th>\n      <th>Filter_Name</th>\n      <th>Line_Index</th>\n      <th>Line_Content</th>\n      <th>Line_Action</th>\n      <th>Reference_Line_Index</th>\n      <th>Reference_Line_Content</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>0</th>\n      <td>fw1</td>\n      <td>acl-inside</td>\n      <td>0</td>\n      <td>permit udp host 10.0.2.1 host 8.8.8.8 eq ntp</td>\n      <td>PERMIT</td>\n      <td>0</td>\n      <td>"to-google-dns (10.0.0.0/8 any 8.8.8.8/32 any ip deny)"</td>\n    </tr>\n    <tr>\n      <th>1</th>\n      <td>fw1</td>\n      <td>acl-inside</td>\n      <td>1</td>\n      <td>permit udp host 10.0.2.1 host 8.8.8.8 eq domain</td>\n      <td>PERMIT</td>\n      <td>0</td>\n      <td>"to-google-dns (10.0.0.0/8 any 8.8.8.8/32 any ip deny)"</td>\n    </tr>\n    <tr>\n      <th>2</th>\n      <td>fw1</td>\n      <td>acl-inside</td>\n      <td>2</td>\n      <td>permit udp host 10.0.2.1 host 8.8.4.4 eq ntp</td>\n      <td>PERMIT</td>\n      <td>3</td>\n      <td>default-deny</td>\n    </tr>\n    <tr>\n      <th>3</th>\n      <td>fw1</td>\n      <td>acl-inside</td>\n      <td>3</td>\n      <td>permit udp host 10.0.2.1 host 8.8.4.4 eq domain</td>\n      <td>PERMIT</td>\n      <td>3</td>\n      <td>default-deny</td>\n    </tr>\n    <tr>\n      <th>4</th>\n      <td>fw1</td>\n      <td>acl-inside</td>\n      <td>4</td>\n      <td>deny ip any4 any4</td>\n      <td>DENY</td>\n      <td>1</td>\n      <td>"from-11-36-216-176 (11.36.216.176/32 any 11.36.216.0/24 any ip permit)"</td>\n    </tr>\n    <tr>\n      <th>5</th>\n      <td>fw1</td>\n      <td>acl-inside</td>\n      <td>4</td>\n      <td>deny ip any4 any4</td>\n      <td>DENY</td>\n      <td>2</td>\n      <td>"flow3 (10.36.176.0/24 any 11.20.0.0/16 1000-20000 tcp permit)"</td>\n    </tr>\n  </tbody>\n</table>'
report = generate_report("./acl_auditor/report.j2", audit_results, reference_flows)
print(report)
write_file("report.html", report)
# print(data)
# print reference acls

# flows that are permitted and show be denied.
# flows that are denied but should be permitted.
