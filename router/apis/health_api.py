from urllib.parse import urlparse, ParseResult
from apis.http_api import HttpApi
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HealthApi:
    cacheResults = {}

    @staticmethod
    def healthy(session, address, path, expected_text):

        p = urlparse(address, 'http')
        netloc = p.netloc or p.path
        scheme = p.scheme or 'http'
        url = ParseResult(scheme, netloc, path, *p[3:]).geturl()

        if url in HealthApi.cacheResults:
            return HealthApi.cacheResults.get(url)
        else:
            response = HttpApi.healthy(session, url, expected_text, timeout=10)
            HealthApi.cacheResults[url] = response
            return response
