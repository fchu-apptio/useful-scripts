from helpers.router_helper import RouterArg
from apis.router_api import RouterApi
import argparse
import sys
import uuid

parser = argparse.ArgumentParser(description='Add Application')
parser.add_argument('--router', '-r', dest='router', type=RouterArg(), 
  help='(Required) One of [{}], or a custom url'.format( ", ".join( RouterArg.URLS.keys()) ), required=True)
parser.add_argument('--bff-address', '-b', dest='address', type=str, required=True, help='Url to the biit instance')
parser.add_argument('--bff-version', '-v', dest='version', type=str, required=True, help='Tag of the bff version to provision to')
parser.add_argument('--primary', '-p', dest='primary', type=bool, default=False, help='Is the version primary')
parser.add_argument('--app-name', '-a', dest='app', type=str, default='Studio Bff', help='Router application to provision to')
args = parser.parse_args()
print("Running with args:")
print(args)

api = RouterApi(args.router)
