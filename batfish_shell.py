#!/opt/conda/bin/python -i

import os
import random
import sys

from pybatfish.client.commands import *
from pybatfish.client.session import Session
from pybatfish.datamodel.flow import HeaderConstraints, PathConstraints
from pybatfish.question.question import load_questions
from pybatfish.question import bfq

import pandas as pd
#pd.set_option("display.max_columns", 20)
pd.set_option("display.max_rows", 1000)

#from dotenv import load_dotenv
import argparse

load_dotenv('.env')

parser = argparse.ArgumentParser(description='Batfish Shell')
parser.add_argument('-p','--snapshot_path', help='snapshot_path', required=True)
parser.add_argument('-s','--snapshot_name', help='snapshot_name', required=True)
parser.add_argument('-n','--network_name', help='network_name', required=True)

args = vars(parser.parse_args())

SVC_ENDPOINT = '172.29.236.139'

bf = Session.get('bf', host=SVC_ENDPOINT)

bf.set_network(args['network_name'])
bf.init_snapshot(args['snapshot_path'], name=args['snapshot_name'], overwrite=True)


