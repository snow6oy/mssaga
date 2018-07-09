#!/usr/bin/python
'''
micoservices saga
'''
import bottle
from bottle import route, run, request, static_file


class sagaOrchestrator():

  def __init__(self):
    self.accounts=dict()

  def new_account(self, person):
    ''' 
    create account for given person by POST to accounts (not done yet :)
    return 201 and Location to GET /accounts/:person
    '''
    self.accounts[person]={'created':True}
    print self.accounts.items()

if __name__ == '__main__':
  so=sagaOrchestrator()
  server=bottle.app()

  @route('/products', method="post")
  def products():
    return request.environ.get('REMOTE_USER_STATUS')

  @route('/', method='post')
  #@cas.require would be nice to implement saga orchestration as a decorator
  def accounts():
    person=request.forms.get('person')
    so.new_account(person) 
    return "Hello, %s welcome to your new account." %person

  # serve static content
  @route('/')
  def index():
    return static_file('index.html', root='.')

  @route('/js/<filename:path>')
  def send_static(filename):
    return static_file(filename, root='js/')

  @route('/favicon.ico')
  def get_favicon():
    return static_file('favicon.ico', root='js/')

  run(app=server, host='0.0.0.0', port=5001)

