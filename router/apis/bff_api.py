from apis.http_api import HttpRequest
from urllib.parse import urlparse, ParseResult
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BffApi:
  cacheResults={}

  @staticmethod
  def healthy(address, useCache=True):
    def isResultHealhty( response ):
      return response and response.status_code==200 and response.text and response.text=='OK'

    p = urlparse(address, 'http')
    netloc = p.netloc or p.path
    scheme = p.scheme or 'http'
    url = ParseResult(scheme, netloc, 'healthcheck', *p[3:]).geturl()

    if url in BffApi.cacheResults and isResultHealhty(BffApi.cacheResults.get(url)):
      return True
    else:
      response = HttpRequest.call( request = lambda: requests.get(url, verify=False, timeout=3),
        log_action = "GET", log_url = url, log=False )
      BffApi.cacheResults[url]=response
      return isResultHealhty(response)
  