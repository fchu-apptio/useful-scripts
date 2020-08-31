from apis.health_api import HealthApi


class RouterArg(object):
    URLS = {
        "us-prod": "http://studio-service-internal.apptio.com:7001",
        "us-dev": "http://sui-default-internal.apptio.com:7001",
        "au-prod": "http://studio-service-au-internal.apptio.com:7001",
        "eu-prod": "http://studio-service-eu-internal.apptio.com:7001",
        "local": "http://localhost:9550"
    }

    def __call__(self, value):
        if value in self.URLS.keys():
            return self.URLS[value]
        else:
            return value


class EnvironmentsHelper:
    @staticmethod
    def get_dict(environments):
        return {e.get('id'): e for e in environments}

    @staticmethod
    def get_all_info_map(application, environments, api):
        app_id = application.get('id')
        versions = VersionsHelper.get_dict(api.get_versions_by_app(app_id))
        env_versions = EnvironmentVersionsHelper.get_dict(api.get_env_versions_by_app(app_id))
        output = []
        for e in environments:
            env = {
                'appId': app_id,
                'appName': application.get('name'),
                'envId': e.get('id'),
                'fqen': e.get('fullyQualifiedEnvironmentName'),
                'customerName': e.get('customer').get('name'),
                'customerId': e.get('customerId'),
                'vanityDomain': e.get('vanityDomain')
            }
            ev = env_versions.get("{}-{}".format(e.get('id'), app_id))
            if ev:
                env['envVerId'] = ev.get('id')
                env['versionBuildNumber'] = ev.get('versionBuildNumber')
                ver = versions.get(ev.get('versionBuildNumber'))
                if ver:
                    env['verId'] = ver.get('id')
                    env['elbAddress'] = ver.get('elbAddress')

            output.append(env)
        return output

    @staticmethod
    def append_version_resource(filtered_environments, api):
        output = []
        for e in filtered_environments:
            env = e
            if env.get('envVerId'):
                res = api.get_env_version_resources(env.get('envVerId'))
                if res:
                    env['biitAddress'] = res.get('biit')
            output.append(env)
        return output

    @staticmethod
    def filter_bad_environments(filtered_environments, session, ignore):

        output = []
        for e in filtered_environments:
            env = e
            if not env.get('envVerId') or not env.get('versionBuildNumber'):
                env['reason_failed'] = 'Missing environment version information'
            elif not env.get('biitAddress'):
                env['reason_failed'] = 'Missing biit resource'
            elif env.get('biitAddress') not in (ignore or []) and not HealthApi.healthy(session, env.get('biitAddress'), 'biit/health', 'OK'):
                env['reason_failed'] = 'Biit is down: {}'.format(env.get('biitAddress'))
            else:
                continue
            output.append(env)
        return output


class EnvironmentVersionsHelper:
    @staticmethod
    def get_dict(env_versions):
        return {"{}-{}".format(v.get('environmentId'), v.get('applicationId')): v for v in env_versions}


class VersionsHelper:
    @staticmethod
    def get_dict(versions):
        return {v.get('buildNumber'): v for v in versions}

    @staticmethod
    def get_all_info_map(application, versions, api):
        app_id = application.get('id')
        env_versions = api.get_env_versions_by_app(app_id)
        environments = EnvironmentsHelper.get_dict(api.get_environment_by_application(app_id))
        output = []
        for v in versions:
            ver = {
                'appId': app_id,
                'appName': application.get('name'),
                'verId': v.get('id'),
                'elbAddress': v.get('elbAddress'),
                'buildNumber': v.get('buildNumber')
            }
            envs = []
            filtered_env_versions = filter(
                lambda ev: ev.get('versionBuildNumber') and v.get('buildNumber') == ev.get('versionBuildNumber'),
                env_versions)
            for ev in filtered_env_versions:
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
    def filter_bad_versions(filtered_versions, session):
        output = []
        for v in filtered_versions:
            ver = v
            reasons = []

            if not ver.get('environments'):
                reasons.append('No environments configured for this version')

            if not HealthApi.healthy(session, ver.get('elbAddress'), 'healthcheck', 'OK'):
                reasons.append('Bff is down: {}'.format(ver.get('elbAddress')))

            if not reasons:
                continue

            ver['reason_failed'] = ', '.join(reasons)
            output.append(ver)
        return output
