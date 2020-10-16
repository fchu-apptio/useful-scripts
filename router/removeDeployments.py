# coding: utf-8

from helpers.file_helper import FileArg
import argparse
import json
import os
import re
import subprocess
import logging

# gets current directory
cwd = os.getcwd()

parser = argparse.ArgumentParser(description='Remove deployments')
parser.add_argument('--input-file', '-i', dest='input', type=FileArg(), required=True,
                    help='Input file with items to delete')
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.info("Running with args:")
logging.info(args)

def grep_r (pattern, dir):
  try:
    p = subprocess.check_output(['grep', '-r', pattern, dir], universal_newlines=True, stderr=subprocess.STDOUT)
    return p.split(":")[0]
  except subprocess.CalledProcessError as e:
    logging.error(e)

with open(args.input) as json_file:
  data = json.load(json_file)
  for item in data:
    if 'elbAddress' in item:
      address = item.get('elbAddress')
      logging.info('Removing address: ' + address)
      filename = grep_r( address, cwd)
      if filename:
        logging.info('Removing file: ' + filename)
        os.remove(filename)

