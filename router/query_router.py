from helpers.router_helper import RouterArg, EnvironmentsHelper, VersionsHelper
from apis.router_api import RouterApi
import argparse
import sys
import logging
import json
import requests

functions = {}
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

functions['search_environments'] = 'Finds all environments and their details with filtering capabilities.\
  `--name` (fqen) and `--version` (buildNumber) are used to filter search.\
  `--custom bad` can search for environments without proper environment versions'


def search_environments(params):
    logging.info('Running search environments...')
    session = requests.session()
    api = RouterApi(params.router, session, False)
    application = api.get_application_by_name(params.app)
    if not application or 'id' not in application:
        sys.exit("No Application {}".format(args.app))

    environments = EnvironmentsHelper.get_all_info_map(application,
                                                       api.get_environment_by_application(application.get('id')), api)
    if params.name:
        environments = filter(lambda e: e.get('fqen') and params.name in e.get('fqen'), environments)
    if params.version:
        environments = filter(lambda e: e.get('versionBuildNumber') and params.version in e.get('versionBuildNumber'),
                              environments)

    environments = EnvironmentsHelper.append_version_resource(environments, api)
    if params.custom == 'bad':
        environments = EnvironmentsHelper.filter_bad_environments(environments, session, params.ignoreList)

    return list(environments)


functions['search_versions'] = 'Finds all versions and their details with filtering capabilities.\
  `--name` (elbaddress) and `--version` (buildNumber) is used to filter search.\
  `--custom bad` can search for versions without any environment attached'


def search_versions(params):
    logging.info('Running search version...')
    session = requests.session()
    api = RouterApi(params.router, session, False)

    application = api.get_application_by_name(params.app)
    if not application or 'id' not in application:
        sys.exit("No Application {}".format(args.app))

    versions = VersionsHelper.get_all_info_map(application, api.get_versions_by_app(application.get('id')), api)
    if params.name:
        versions = filter(lambda e: e.get('elbAddress') and params.name in e.get('elbAddress'), versions)
    if params.version:
        versions = filter(lambda e: e.get('buildNumber') and params.version in e.get('buildNumber'), versions)

    if params.custom == 'bad':
        versions = VersionsHelper.filter_bad_versions(versions, session)

    return list(versions)


def run_function(name, params):
    switch = {
        'search_environments': search_environments,
        'search_versions': search_versions
    }
    return switch.get(name, None)(params)


class FunctionArg(object):
    def __call__(self, value):
        if value in functions:
            return value
        else:
            raise KeyError('{} is not a supported action, choose from: {}'.format(value, ','.join(functions.keys())))


parser = argparse.ArgumentParser(description='Query router items')
parser.add_argument('--router', '-r', dest='router', type=RouterArg(),
                    help='(Required) One of [{}], or a custom url'.format(", ".join(RouterArg.URLS.keys())),
                    required=True)
parser.add_argument('--function', '-f', dest='function', type=FunctionArg(),
                    help='(Required) Function to run. One of [{}]'.format(functions), required=True)
parser.add_argument('--name', '-n', dest='name', type=str, required=False)
parser.add_argument('--custom', '-c', dest='custom', type=str, required=False)
parser.add_argument('--ignore', '-i', nargs='+', dest='ignoreList', required=False)
parser.add_argument('--output', '-o', dest='output', type=str, required=False, help="Output file for results")
parser.add_argument('--version', '-v', dest='version', type=str, required=False,
                    help="A build version for the application")
parser.add_argument('--app-name', '-a', dest='app', type=str, default='Studio BFF', required=False,
                    help='Router application to use')
args = parser.parse_args()

logging.info("Running with args:")
logging.info(args)

output = run_function(args.function, args)
if args.output:
    with open(args.output, 'w') as outfile:
        json.dump(output, outfile, indent=2)
else:
    logging.info(json.dumps(output, indent=2))
