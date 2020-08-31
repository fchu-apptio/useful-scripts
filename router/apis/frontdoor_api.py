from apis.http_api import HttpApi
import json


class FrontdoorApi(HttpApi):
    def __init__(self, address, session, log=True):
        super().__init__(session, log)
        self.address = address

    def login(self, username, password):
        data = {
            'ping_uname': username,
            'ping_pwd': password
        }
        return self.post(url='{0}/service/nonuilogin'.format(self.address), data=json.dumps(data))

    def get_environment(self, customer, environment):
        return self.get(url='{0}/api/environment/{1}/{2}'.format(self.address, customer, environment)).json()
