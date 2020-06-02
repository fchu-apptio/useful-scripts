from helpers.router_helper import RouterArg
from apis.router_api import RouterApi
import argparse
import sys
import uuid

parser = argparse.ArgumentParser(description='Provision biit instance to router')
parser.add_argument('--router', '-r', dest='router', type=RouterArg(), 
  help='(Required) One of [{}], or a custom url'.format( ", ".join( RouterArg.URLS.keys()) ), required=True)
parser.add_argument('--env', '-e', dest='env', type=str, required=True, help='Environment name to provision')
parser.add_argument('--customer', '-c', dest='customer', type=str, required=True, help='Customer address to provision')
parser.add_argument('--bff-version', '-v', dest='version', type=str, required=True, help='Tag of the bff version to provision to')
parser.add_argument('--biit-address', '-b', dest='address', type=str, required=True, help='Url of the biit server')
parser.add_argument('--app-name', '-a', dest='app', type=str, default='Studio Bff', help='Router application to provision to')
args = parser.parse_args()
print("Running with args:")
print(args)

api = RouterApi(args.router)

# Get the application, fail if does not exist 
application = api.get_application_by_name(args.app)
if not application or 'id' not in application:
  sys.exit("No Application {}".format(args.app))

# Get the version, fail if not exists
version = api.get_version_by_build_and_app(args.version, application.get('id'))
if not version or 'id' not in version:
  sys.exit("No bff version found for {}".format(args.version))

# Get the customer, create if not exists
customer = api.get_customer_by_name(args.customer)
if not customer or 'id' not in customer:
  customer = api.post_customer({ "name" : args.customer })
  if not customer or 'id' not in customer:
    sys.exit("Customer could not be created")

# Get the environment, create if not exists
fqen = "{}:{}".format(args.customer, args.env)
environment = api.get_environment_by_fqen(fqen)
if not environment or 'id' not in environment:
  environment = api.post_environment({
    "fullyQualifiedEnvironmentName" : fqen, 
    "databaseSchema" : str(uuid.uuid1()), 
    "customerId" : customer.get('id'), 
    "environmentState" : "Running", 
    "upgradeGroup" : "Internal"
  })
  if not environment or 'id' not in environment:
    sys.exit("Environment could not be created")

# Get the environment version, create if not exists
envVersion = api.get_envVersions_by_env_and_app(environment.get('id'), application.get('id'))
if not envVersion or 'id' not in envVersion:
  envVersion = api.post_envVersion({
    "applicationId" : application.get('id'), 
    "environmentId" : environment.get('id'),
    "versionBuildNumber" : args.version
  })
  if not envVersion or 'id' not in envVersion:
    sys.exit("EnvironmentVersion could not be created")
else:
  api.put_envVersion({
    "id" : envVersion.get('id'),
    "versionBuildNumber" : args.version
  })

# Update the environment version resources
api.put_envVersion_resources( envVersion.get('id'), 'biit', args.address )

# Clear cache
api.clearCache()