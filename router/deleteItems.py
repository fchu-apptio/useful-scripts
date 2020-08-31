from apis.router_api import RouterApi
from apis.health_api import HealthApi
from helpers.router_helper import RouterArg
from helpers.file_helper import FileArg
import argparse
import json
import requests
import logging

deletableFields = ['customer', 'environment', 'envVersion', 'version']

parser = argparse.ArgumentParser(description='Provision biit instance to router')
parser.add_argument('--router', '-r', dest='router', type=RouterArg(),
                    help='(Required) One of [{}], or a custom url'.format(", ".join(RouterArg.URLS.keys())),
                    required=True)
parser.add_argument('--input-file', '-i', dest='input', type=FileArg(), required=True,
                    help='Input file with items to delete')
parser.add_argument('--list', '-l', nargs='+', dest='list', required=True,
                    help='Fields to delete. Can be multiple of {}'.format(deletableFields))
parser.add_argument('--verify', dest='verify', default=False, action='store_true',
                    help='Revalidate (only applies for environment biit addresses) ')
args = parser.parse_args()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.info("Running with args:")
logging.info(args)

for x in args.list:
    if x not in deletableFields:
        raise KeyError("{} is not within deletableFields {}".format(x, deletableFields))

session = requests.session()
api = RouterApi(args.router, session)

with open(args.input) as json_file:
    data = json.load(json_file)

    for item in data:
        if 'envVersion' in args.list and 'envVerId' in item:
            api.delete_env_version(item.get('envVerId'))

        if 'environment' in args.list and 'envId' in item:
            if not args.verify or not item.get('biitAddress') or not \
                    HealthApi.healthy(session, item.get('biitAddress'), "biit/health", "OK"):
                api.delete_environment(item.get('envId'))
            else:
                logging.info('Skipping environment {} because biit instance was deemed healthy'.format(item.get('envId')))

        if 'customer' in args.list and 'customerId' in item:
            api.delete_environment(item.get('customerId'))

        if 'version' in args.list and 'verId' in item and not item.get('environments'):
            api.delete_version(item.get('verId'))
