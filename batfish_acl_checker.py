from pybatfish.client.commands import *
from pybatfish.question.question import load_questions
from pybatfish.datamodel.flow import (HeaderConstraints,
                                                 PathConstraints)
from pybatfish.question import bfq
import argparse
import logging

logging.getLogger('pybatfish').setLevel(logging.FATAL)

NETWORK_NAME = "network"
BATFISH_SERVICE_IP = "172.29.236.139"

bf_session.host = BATFISH_SERVICE_IP
load_questions()

def read_file(filename):
    file = open(filename, "r")
    data = file.read()
    file.close()
    return data

parser = argparse.ArgumentParser(description='Batfish Shell')
parser.add_argument('-c','--config', help='config', required=True)
args = vars(parser.parse_args())

config = read_file(args['config'])


bf_set_network(NETWORK_NAME)

bf_session.init_snapshot_from_text(config, snapshot_name="implemented", overwrite=True)
bfq.nodeProperties().answer().frame()

