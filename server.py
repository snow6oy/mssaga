#!/usr/bin/python
'''
micoservices saga
'''
import bottle
from bottle import route, run, request, static_file


class sagaOrchestrator():

  def __init__(self):
    self.amount=0

  def add_funds(self, amount):
    ''' 
    top account with given amount by POST to accounts (not done yet :)
    return 201 and Location to GET /accounts/balance
    '''
    self.amount=self.amount+ float(amount)
    print self.amount

if __name__ == '__main__':
  so=sagaOrchestrator()
  server=bottle.app()

  @route('/products', method="post")
  def products():
    return request.environ.get('REMOTE_USER_STATUS')

  @route('/', method='post')
  #@cas.require would be nice to implement saga orchestration as a decorator
  def accounts():
    amount=request.forms.get('person')
    so.add_funds(amount) 
    return "Hello, %s has been added to your account." %amount

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

