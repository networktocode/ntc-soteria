# Batfish ACL Auditor
This repo contains an ACL auditing tool based on Batfish. The goal of this tool is to help you automate the process of validating your firewall ACLs, and access. Along with providing a foundation from which you can learn more about performing network automation with Batfish.

## Audits
This tool provides the ability to perform 2 types of audits against an ACL rule base.

* **ACL Reference Comparision** - This audit takes 3 pieces of information, a single YAML file containing a set of reference flows, the configuration of your firewall, and also the ACL name in question. It then calculates the difference between your reference flows and implemented flows, to provide you with the differences. Some use cases for this include:
  * Prevent human error, during firewall changes. For example incorrect addition of ip any any.
  * Allows you to run routine scripted checks against your ACL base to ensure no ACLs are opened by bad actors.
  * As this can function as a CLI script you can add this to part of your ACL CI pipelines.
* **Unreachable ACL Entries** - This check takes a firewall configuration containing your ACL rule sets. It then reports on any lines in the specified filters that will not match any packet, either because of being shadowed by prior lines or because of its match condition being empty. The key use cases for this are:
  * Prevent human error, during firewall changes. For example, incorrect placement of an encompassing deny rule.
  * Assist in keeping your ACL rule sets minimal and free of unnecessary lines.
  * As this can function as a CLI script you can add this to part of your ACL CI pipelines.

## Supported Devices
The following platforms are supported and have been tested:
* Cisco ASA
* IOS-XE

## Docker Compose
To create the required environment in order to run this tool, along with deploy the Batfish service dependancy, a docker-compose file is provided.

Before running install Docker and Docker Compose. Once installed run the following commands:
```
git clone git@github.com:networktocode/batfish-acl-auditor.git

cd batfish-acl-auditor

docker-compose build
docker-compose up -d
docker-compose exec acl_auditor <command>
```

**Note:**

* As part of `docker-compose` the `./data` folder is created as a volume. This allows you to easily add configs or pull reports.
* You will only need to run `docker-compose build` once. Once the containers are build you can just bring your Docker Compose stack up via `docker-compose up -d`

## Usage
Below shows the various options for this tool. 

**Note:** Sample files are provided within the `./data` directory for initial testing. 

### ACL Reference Comparision
The reference comparision option takes the following inputs:
* device configuration (`-d`)
* acl name to validate from within your device configuration (`-a`)
* reference flows (`-r`)

The reference flow file strucutre is shown below:
```
---
- source_ip: <network>/<cidr>
  dest_ip: <network>/<cidr>
  proto: <protocol>
  action: <permit/deny>
  name: <description of flow>
```
**Example:**

```
./acl_auditor/auditor.py -c compare -d data/asa.cfg -r data/flows.yml -a acl-inside 
```



### Unreachable ACL Entries
The unreachable acl entry option takes the following inputs:
* device configuration (`-d`)

**Example:**
```
./acl_auditor/auditor.py -c unreachable -d data/asa.cfg
```
### HTML Report
An HTML report can be generated with the results. However, this option can only be run when running the `-c all` (check all) option.
```
./acl_auditor/auditor.py -c all -d data/asa.cfg -r data/flows.yml -a acl-inside -o html
```
Once complete a HTML report will be saved within `./data`. Below shows an example:
![alt text](https://github.com/networktocode/batfish-acl-auditor/blob/master/data/report-example.png?raw=true)
**Note:** The HTML report generated uses the following Material/Bootstrap framework: https://fezvrasta.github.io/bootstrap-material-design/.
