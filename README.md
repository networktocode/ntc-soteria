# Batfish ACL Auditor

NOTE: WORK IN PROGRESS

This repo provides a Batfish based ACL auditing tool.

## Installation
```
git clone git@github.com:networktocode/batfish-acl-auditor.git
poetry add env python3.6
poetry install
poetry shell
```

## Usage
ACLs are audited against a set of flows for a given devices configuration. The audit reults then provide:
* Permitted - Any flows that are permitted outside of the defined reference flows.
* Denied - Any flows that are denied that should be permitted based on the defined reference flows.

## Usage
Below shows an execution example. Once complete a HTML report will also be saved within `./data`.
```
export BATFISH_SERVICE_HOST=localhost
python acl_auditor/auditor.py -c data/asa.cfg -f data/flows.yml -a acl-inside
```
Note: The HTML report uses the following framework https://fezvrasta.github.io/bootstrap-material-design/.