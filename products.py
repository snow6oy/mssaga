#!/usr/bin/python
'''
micoservices saga
'''
import bottle
from bottle import route, run, request, static_file

if __name__ == '__main__':
  #cas=CASClient()
  server=bottle.app()

  @route('/products', method="post")
  def products():
    return request.environ.get('REMOTE_USER_STATUS')

  @route('/', method='post')
  #@cas.require
  def accounts():
    ''' 
    top account with given amount by POST to /accounts
    return 201 and Location to GET /accounts/balance
    '''
    user = request.forms.get('person')
    return "Hello, %s. This is a CAS client written in bottle\n <a href='logout'>Logout</a>" %user

  # serve static content
  @route('/')
  def index():
    return static_file('index.html', root='.')

  @route('/js/<filename:path>')
  def send_static(filename):
    return static_file(filename, root='js/')

  @route('/favicon.ico')
  def get_favicon():
    return server_static('favicon.ico')

  run(app=server, host='0.0.0.0', port=5001)

