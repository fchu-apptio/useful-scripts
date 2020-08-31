import logging
import json


class HttpApi:
    def __init__(self, session, log=True):
        self.session = session
        self.log = log

    def get(self, url, params=None, as_json=False):
        response = HttpApi.__log_wrapper(lambda: self.session.get(url, params=params, timeout=10),
                           "GET", url, params, self.log)
        return HttpApi.__handle_response(response, as_json)

    def post(self, url, data, as_json=False):
        response = HttpApi.__log_wrapper(lambda: self.session.post(url, data=data, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'cache-control': 'no-cache'
        }, timeout=3), "POST", url, data, self.log)
        return HttpApi.__handle_response(response, as_json)

    def put(self, url, data, as_json=False):
        response = HttpApi.__log_wrapper(lambda: self.session.put(url, data=data, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'cache-control': 'no-cache'
        }, timeout=3), "PUT", url, data, self.log)
        return HttpApi.__handle_response(response, as_json)

    def delete(self, url):
        return HttpApi.__log_wrapper(lambda: self.session.delete(url, timeout=3), "DELETE", url, None, self.log)

    @staticmethod
    def __handle_response(response, as_json):
        if as_json:
            try:
                return response.json()
            except json.JSONDecodeError:
                return None
        else:
            return response

    @staticmethod
    def __log_wrapper(request, action, url, data, log):
        logging.info("Sending {0} {1}, {2}".format(action, url, data))

        try:
            response = request()
        except Exception as e:
            print('Failed to {0} request to {1} with exception: {2}'.format(action, url, str(e)))
            return None

        if log:
            if response.content:
                try:
                    content = json.dumps(response.json(), indent=4, separators=(',', ': '))
                except json.JSONDecodeError:
                    content = response.content
                logging.info("Received Response {0}: {1}".format(response.status_code, content))
            else:
                logging.info("Received Response {0}".format(response.status_code))

        return response

    @staticmethod
    def healthy(session, address, expected_text, timeout=3, log=True):
        def is_result_healthy(health_response):
            return health_response and health_response.status_code == 200 \
                   and health_response.text and health_response.text == expected_text
        response = HttpApi.__log_wrapper(lambda: session.get(address, verify=False, timeout=timeout), "GET", address, None, log)
        return is_result_healthy(response)
