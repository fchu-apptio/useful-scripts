from apis.http_api import HttpApi
import urllib.parse
import json


class RouterApi(HttpApi):

    def __init__(self, address, session, log=True):
        super().__init__(session, log)
        self.address = address

    # Application
    def get_application_by_name(self, name):
        return self.get(url='{0}/sf/applications/name/{1}/'.format(self.address, urllib.parse.quote(name)), as_json=True)

    # Version
    def get_version_by_build_and_app(self, build, appId):
        return self.get(url='{0}/sf/versions/buildNumber/{1}?applicationId={2}'.format(self.address, build, appId), as_json=True)

    def get_version_by_id(self, id):
        return self.get(url='{0}/sf/versions/{1}'.format(self.address, id), as_json=True)

    def get_versions_by_app(self, appId):
        return self.get(url='{0}/sf/versions?applicationId={1}'.format(self.address, appId), as_json=True)

    def post_version(self, data):
        return self.post(url='{0}/sf/versions'.format(self.address), data=json.dumps(data), as_json=True)

    def delete_version(self, verId):
        return self.delete(url='{0}/sf/versions/{1}'.format(self.address, verId))

    # Customer
    def get_customer_by_name(self, name):
        return self.get(url='{0}/sf/customers/name/{1}/'.format(self.address, name), as_json=True)

    def post_customer(self, data):
        return self.post(url='{0}/sf/customers'.format(self.address), data=json.dumps(data), as_json=True)

    def delete_customer(self, custId):
        return self.delete(url='{0}/sf/customers/{1}'.format(self.address, custId))

    # Environment
    def get_environment_by_fqen(self, fqen):
        return self.get(url='{0}/sf/environments/fqen/{1}/'.format(self.address, fqen), as_json=True)

    def get_environment_by_application(self, appId):
        return self.get(url='{0}/sf/environments/application/{1}/'.format(self.address, appId), as_json=True)

    def get_environments_by_version(self, versionId):
        return self.get(url='{0}/sf/environments/version/{1}/'.format(self.address, versionId), as_json=True)

    def post_environment(self, data):
        return self.post(url='{0}/sf/environments'.format(self.address), data=json.dumps(data), as_json=True)

    def put_environment(self, data):
        return self.put(url='{0}/sf/environments'.format(self.address), data=json.dumps(data), as_json=True)

    def delete_environment(self, envId):
        return self.delete(url='{0}/sf/environments/{1}'.format(self.address, envId))

    # Environment Versions
    def get_env_versions_by_env_and_app(self, envId, appId):
        params = {
            'applicationId': appId,
            'environmentId': envId
        }
        return self.get(url='{0}/sf/envVersions'.format(self.address), params=params, as_json=True)

    def get_env_versions_by_app(self, appId):
        params = {
            'applicationId': appId
        }
        return self.get(url='{0}/sf/envVersions'.format(self.address), params=params, as_json=True)

    def put_env_version_for_environments(self, build, data):
        return self.put(url='{0}/sf/envVersions/versionBuildNumber/{1}'.format(self.address, build),
                        data=json.dumps(data), as_json=True)

    def post_env_version(self, data):
        return self.post(url='{0}/sf/envVersions'.format(self.address), data=json.dumps(data), as_json=True)

    def put_env_version(self, data):
        return self.put(url='{0}/sf/envVersions'.format(self.address), data=json.dumps(data), as_json=True)

    def delete_env_version(self, envVerId):
        return self.delete(url='{0}/sf/envVersions/{1}'.format(self.address, envVerId))

    # Environment Versions Resource
    def get_env_version_resources(self, envVerId):
        return self.get(url='{0}/sf/envVersions/{1}/resource'.format(self.address, envVerId), as_json=True)

    def put_env_version_resources(self, envVerId, name, resource):
        return self.put(url='{0}/sf/envVersions/{1}/resource/{2}/'.format(self.address, envVerId, name),
                        data="\"{}\"".format(resource))

    # Cache
    def clear_cache(self):
        return self.delete(url='{0}/sf/cache/routes'.format(self.address))
