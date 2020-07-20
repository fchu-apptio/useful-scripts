from apis.http_api import HttpRequest
import pprint
import requests
import urllib.parse

class HttpRouter:
  postHeaders = {
    'Accept':'application/json',
    'Content-Type':'application/json',
    'cache-control':'no-cache'
  }

  def __init__(self, url, log=True):
    self.url = url
    self.log = log

  def get(self, path, params = {}):
    url = '{}/sf/{}'.format(self.url, path)
    return HttpRequest.call( request = lambda: requests.get(url, params=params, timeout=10).json(),
      log_action = "GET", log_data = params, log_url = url, log=self.log )

  def post(self, path, data):
    url = '{}/sf/{}'.format(self.url, path)
    return HttpRequest.call( request = lambda: requests.post(url, json = data, headers = self.postHeaders, timeout = 3).json(),
      log_action = "POST", log_data = data, log_url = url, log=self.log )

  def put(self, path, data):
    url = '{}/sf/{}'.format(self.url, path)
    return HttpRequest.call( request = lambda:  requests.put(url, json = data, headers = self.postHeaders, timeout = 3).json(),
      log_action = "PUT", log_data = data, log_url = url, log=self.log )

  def put_str(self, path, string):
    url = '{}/sf/{}'.format(self.url, path)
    return HttpRequest.call( request = lambda:  requests.put(url, data = string, headers = self.postHeaders, timeout = 3),
      log_action = "PUT_STR", log_data = string, log_url = url, log=self.log )

  def delete(self, path):
    url = '{}/sf/{}'.format(self.url, path)
    return HttpRequest.call( request = lambda: requests.delete(url, timeout = 3),
    log_action = "DELETE", log_url = url, log=self.log )

class RouterApi:
  def __init__(self, url, log=True):
    self.http = HttpRouter(url, log)

  # Application
  def get_application_by_name(self, name):
    return self.http.get(path = 'applications/name/{}/'.format(urllib.parse.quote(name)))

  # Version
  def get_version_by_build_and_app(self, build, appId):
    return self.http.get(path = 'versions/buildNumber/{}?applicationId={}'.format(build, appId))

  def get_versions_by_app(self, appId):
    return self.http.get(path = 'versions?applicationId={}'.format(appId))

  def post_version(self, data):
    return self.http.post(path = 'versions', data = data)

  def delete_version(self, verId):
    return self.http.delete(path = 'versions/{}'.format(verId))

  # Customer
  def get_customer_by_name(self, name):
    return self.http.get(path = 'customers/name/{}/'.format(name))

  def post_customer(self, data):
    return self.http.post(path = 'customers', data = data)

  def delete_customer(self, custId):
    return self.http.delete(path = 'customers/{}'.format(custId))
  
  # Environment
  def get_environment_by_fqen(self, fqen):
    return self.http.get(path = 'environments/fqen/{}/'.format(fqen))

  def get_environment_by_application(self, appId):
    return self.http.get(path = 'environments/application/{}/'.format(appId))

  def get_environments_by_version(self, versionId):
    return self.http.get(path = 'environments/version/{}/'.format(versionId))

  def post_environment(self, data):
    return self.http.post(path = 'environments', data = data)

  def put_environment(self, data):
    return self.http.put(path = 'environments', data = data)

  def delete_environment(self, envId):
    return self.http.delete(path = 'environments/{}'.format(envId))

  # Environment Versions
  def get_envVersions_by_env_and_app(self, envId, appId):
    params = {
      'applicationId':appId,
      'environmentId':envId
    }
    return self.http.get(path = 'envVersions', params = params)

  def get_envVersions_by_app(self, appId):
    params = {
      'applicationId':appId
    }
    return self.http.get(path = 'envVersions', params = params)

  def put_envVersion_for_environments(self, build, environments):
    return self.http.put(path = 'envVersions/versionBuildNumber/{}'.format(build), data = environments)

  def post_envVersion(self, data):
    return self.http.post(path = 'envVersions', data = data)

  def put_envVersion(self, data):
    return self.http.put(path = 'envVersions', data = data)

  def delete_envVersion(self, envVerId):
    return self.http.delete(path = 'envVersions/{}'.format(envVerId))

  # Environment Versions Resource
  def get_envVersion_resources(self, envVerId):
    return self.http.get(path = 'envVersions/{}/resource'.format(envVerId))
    
  def put_envVersion_resources(self, envVerId, name, resource):
    return self.http.put_str(path = 'envVersions/{}/resource/{}/'.format(envVerId, name), string = "\"{}\"".format(resource))

  # Cache
  def clearCache(self):
    return self.http.delete(path = 'cache/routes')