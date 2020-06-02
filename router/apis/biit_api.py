from apis.http_api import HttpRequest
from urllib.parse import urlparse, ParseResult
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BiitApi:
  cacheResults={}

  @staticmethod
  def healthy(address, useCache=True):
    def isResultHealhty( response ):
      return response and response.status_code==200 and response.text and response.text=='OK'

    p = urlparse(address, 'http')
    netloc = p.netloc or p.path
    scheme = p.scheme or 'http'
    url = ParseResult(scheme, netloc, 'biit/health', *p[3:]).geturl()

    if url in BiitApi.cacheResults and isResultHealhty(BiitApi.cacheResults.get(url)):
      return True
    else:
      response = HttpRequest.call( request = lambda: requests.get(url, verify=False, timeout=10),
        log_action = "GET", log_url = url, log=False )
      BiitApi.cacheResults[url]=response
      return isResultHealhty(response)
  