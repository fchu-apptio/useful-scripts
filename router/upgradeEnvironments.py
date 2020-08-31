from helpers.router_helper import RouterArg
from apis.router_api import RouterApi
import argparse
import sys
import requests

parser = argparse.ArgumentParser(description='Add BFF Version')
parser.add_argument('--router', '-r', dest='router', type=RouterArg(),
                    help='(Required) One of [{}], or a custom url'.format(", ".join(RouterArg.URLS.keys())),
                    required=True)
parser.add_argument('--fqen', '-f', dest='fqen', type=str, required=False,
                    help='Fully qualified environment name to upgrade')
parser.add_argument('--new-version', '-v', dest='version', type=str, required=True,
                    help='Tag of the bff version to provision to')
parser.add_argument('--old-version', '-o', dest='old', type=str, required=False,
                    help='Tag of the bff version to provision to')
parser.add_argument('--app-name', '-a', dest='app', type=str, default='Studio Bff',
                    help='Router application to provision to')
args = parser.parse_args()
print("Running with args:")
print(args)

session = requests.session()
api = RouterApi(args.router, session)

if not args.fqen and not args.old:
    sys.exit("Either fqen or old version is required")

# Get the application, fail if does not exist 
application = api.get_application_by_name(args.app)
if not application or 'id' not in application:
    sys.exit("No Application {}".format(args.app))

version = api.get_version_by_build_and_app(args.version, application.get('id'))
if not version or 'id' not in version:
    sys.exit("New version {} is not found".format(args.version))

output = None
if args.fqen:
    environment = api.get_environment_by_fqen(args.fqen)
    if not environment or 'id' not in environment:
        sys.exit("Could not find environment by fqen {}".format(args.fqen))

    envVer = api.get_env_versions_by_env_and_app(environment.get('id'), application.get('id'))
    if not envVer or 'id' not in envVer:
        sys.exit(
            "Could not find envVer for env {} and application {}".format(environment.get('id'), application.get('id')))

    output = api.put_env_version_for_environments(args.version, [envVer.get('id')])
elif args.old:
    oldVersion = api.get_version_by_build_and_app(args.old, application.get('id'))
    if not oldVersion or 'id' not in oldVersion:
        sys.exit("Old version {} is not found".format(args.old))

    environments = map(lambda e: e.get('id'),
                       filter(lambda ev: ev.get('versionBuildNumber') and args.old == ev.get('versionBuildNumber'),
                              api.get_versions_by_app(application.get('id'))))
    output = api.put_env_version_for_environments(args.version, list(environments))

print(output)

# Clear cache
api.clear_cache()
