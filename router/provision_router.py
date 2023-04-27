from helpers.router_helper import RouterArg
from apis.router_api import RouterApi
import argparse
import sys
import uuid
import requests
import logging

parser = argparse.ArgumentParser(description='Provision biit instance to router')
parser.add_argument('--router', '-r', dest='router', type=RouterArg(),
                    help='(Required) One of [{}], or a custom url'.format(", ".join(RouterArg.URLS.keys())),
                    required=True)
parser.add_argument('--env', '-e', dest='env', type=str, required=True, help='Environment name to provision')
parser.add_argument('--customer', '-c', dest='customer', type=str, required=True, help='Customer address to provision')
parser.add_argument('--version-id', '-i', dest='versionId', type=str, required=False,
                    help='Id of the version to provision to')
parser.add_argument('--bff-version', '-v', dest='version', type=str, required=False,
                    help='Tag of the bff version to provision to')
parser.add_argument('--vanity', '-d', dest='vanity', type=str, required=False,
                    help='vanity domain (just the name without the .apptio.com)')
parser.add_argument('--biit-address', '-b', dest='address', type=str, required=False, help='Url of the biit server')
parser.add_argument('--app-name', '-a', dest='app', type=str, default='Studio Bff',
                    help='Router application to provision to')
args = parser.parse_args()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.info("Running with args:")
logging.info(args)

session = requests.session()
api = RouterApi(args.router, session)

# Get the application, fail if does not exist 
application = api.get_application_by_name(args.app)
if not application or 'id' not in application:
    sys.exit("No Application {}".format(args.app))

# Get the version, fail if not exists
if args.versionId:
    version = api.get_version_by_id(args.versionId)
else:
    version = api.get_version_by_build_and_app(args.version, application.get('id'))
if not version or 'id' not in version:
    sys.exit("No bff version found for {}".format(args.version))

# Get the customer, create if not exists
customer = api.get_customer_by_name(args.customer)
if not customer or 'id' not in customer:
    customer = api.post_customer({"name": args.customer})
    if not customer or 'id' not in customer:
        sys.exit("Customer could not be created")

# Get the environment, create if not exists
fqen = "{}:{}".format(args.customer, args.env)
environment = api.get_environment_by_fqen(fqen)
if not environment or 'id' not in environment:
    body = {
        "fullyQualifiedEnvironmentName": fqen,
        "databaseSchema": str(uuid.uuid1()),
        "customerId": customer.get('id'),
        "environmentState": "Running",
        "upgradeGroup": "Internal"
    }
    if args.vanity:
        body['vanityDomain'] = args.vanity
    environment = api.post_environment(body)
    if not environment or 'id' not in environment:
        sys.exit("Environment could not be created")
else:
    body = {
        "id": environment.get('id'),
        "fullyQualifiedEnvironmentName": fqen
    }
    if args.vanity:
        body['vanityDomain'] = args.vanity
    environment = api.put_environment(body)

# Get the environment version, create if not exists
envVersion = api.get_env_versions_by_env_and_app(environment.get('id'), application.get('id'))
if not envVersion or 'id' not in envVersion:
    envVersion = api.post_env_version({
        "applicationId": application.get('id'),
        "environmentId": environment.get('id'),
        "versionBuildNumber": args.version
    })
    if not envVersion or 'id' not in envVersion:
        sys.exit("EnvironmentVersion could not be created")
else:
    api.put_env_version({
        "id": envVersion.get('id'),
        "versionBuildNumber": args.version
    })

# Update the environment version resources
if args.address:
    api.put_env_version_resources(envVersion.get('id'), 'biit', args.address)

# Clear cache
api.clear_cache()
