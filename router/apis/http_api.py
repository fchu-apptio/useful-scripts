import pprint

class HttpRequest:
  pp = pprint.PrettyPrinter(indent=2)
  debug = False

  @staticmethod
  def call(request, log_action, log_url, log_data={}, log=True, default=None):
    try:
      print('{} {}, {}'.format(log_action, log_url, log_data))
      if HttpRequest.debug and log_action != 'GET':
        response = { 
          'debug': True,
          'id':'8F8CB1FBB4884D99A052D99CF20B030C' 
          }
      else:
        response = request()
      if log:
        print("Response: ")
        HttpRequest.pp.pprint(response)
        print()
      return response
    except Exception as e:
      print('Failed to {} request to {} with exception: {}'.format(log_action, log_url, str(e)))
      return default