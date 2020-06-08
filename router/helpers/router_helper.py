from apis.router_api import RouterApi
from apis.biit_api import BiitApi
from apis.bff_api import BffApi

class RouterArg(object):
  URLS = {
    "us-prod":"http://studio-service-internal.apptio.com:7001",
    "us-dev":"http://sui-default-internal.apptio.com:7001",
    "au-prod":"http://studio-service-au-internal.apptio.com:7001",
    "eu-prod":"http://studio-service-eu-internal.apptio.com:7001",
    "local":"http://localhost:9550"
  }

  def __call__(self, value):
    if value in self.URLS.keys():
      return self.URLS[value]
    else:
      return value

class EnvironmentsHelper:
  @staticmethod
  def get_dict(environments):
    return { e.get('id') : e for e in environments }

  @staticmethod
  def get_all_info_map(application, environments, api):
    appId = application.get('id')
    versions = VersionsHelper.get_dict( api.get_versions_by_app( appId ) )
    envVersions = EnvironmentVersionsHelper.get_dict( api.get_envVersions_by_app( appId ) )
    output = []
    for e in environments:
      env = {
      'appId': appId,
      'appName': application.get('name'),
      'envId': e.get('id'),
      'fqen': e.get('fullyQualifiedEnvironmentName'),
      'customerName': e.get('customer').get('name'),
      'customerId': e.get('customerId'),
      'vanityDomain': e.get('vanityDomain')
      }
      ev = envVersions.get( "{}-{}".format( e.get('id'), appId ) )
      if ev:
        env['envVerId'] = ev.get('id')
        env['versionBuildNumber'] = ev.get('versionBuildNumber')
        ver = versions.get( ev.get('versionBuildNumber') )
        if ver:
          env['verId'] = ev.get('id')
          env['elbAddress'] = ver.get('elbAddress')

      output.append(env)
    return output
  
  @staticmethod
  def appendVersionResource(filteredEnvironments, api):
    output = []
    for e in filteredEnvironments:
      env = e
      if env.get('envVerId'): 
        res = api.get_envVersion_resources( env.get('envVerId') )
        if res:
          env['biitAddress'] = res.get('biit')
      output.append(env)
    return output

  @staticmethod
  def filterBadEnvironments(filteredEnvironments, api):
    output = []
    for e in filteredEnvironments:
      env = e
      if not env.get('envVerId') or not env.get('versionBuildNumber'): 
        env['reason_failed'] = 'Missing environment version information'
      elif not env.get('biitAddress'):
        env['reason_failed'] = 'Missing biit resource'
      elif not BiitApi.healthy(env.get('biitAddress')):
        env['reason_failed'] = 'Biit is down: {}'.format(env.get('biitAddress'))
      else:
        continue
      output.append(env)
    return output

class EnvironmentVersionsHelper:
  @staticmethod
  def get_dict(envVersions):
    return { "{}-{}".format( v.get('environmentId'), v.get('applicationId') ) : v for v in envVersions }

class VersionsHelper:
  @staticmethod
  def get_dict(versions):
    return { v.get('buildNumber') : v for v in versions }

  @staticmethod
  def get_all_info_map(application, versions, api):
    appId = application.get('id')
    envVersions = api.get_envVersions_by_app(appId)
    environments = EnvironmentsHelper.get_dict( api.get_environment_by_application(appId) )
    output = []
    for v in versions:
      ver = {
        'appId': appId,
        'appName': application.get('name'),
        'verId':v.get('id'),
        'elbAddress':v.get('elbAddress'),
        'buildNumber':v.get('buildNumber')
      }
      envs = []
      filteredEnvVersions = filter(lambda ev: ev.get('versionBuildNumber') and v.get('buildNumber') == ev.get('versionBuildNumber'), envVersions)
      for ev in filteredEnvVersions:
        env = environments.get(ev.get('environmentId'))
        if env:
          envs.append({
            'envId': env.get('id'),
            'fqen': env.get('fullyQualifiedEnvironmentName'),
            'custId': env.get('customerId')
          })
      
      ver['environments'] = envs
      output.append(ver)
    return output

  @staticmethod
  def filterBadVersions(filteredVersions, api):
    output = []
    for v in filteredVersions:
      ver = v
      if not ver.get('environments'): 
        ver['reason_failed'] = 'No environments configured for this version'
      elif not BffApi.healthy(ver.get('elbAddress')):
        ver['reason_failed'] = 'Bff is down: {}'.format(ver.get('elbAddress'))
      else:
        continue
      output.append(ver)
    return output

