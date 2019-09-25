#!/usr/bin/python
'''
micoservices saga
'''
import urllib, urllib2, sys
import bottle
from bottle import route, run, request, response, static_file

server=bottle.app()
url='http://localhost:5003/accounts'

@route('/', method='post')
def accounts():
  person=request.forms.get('person')
  response.status=204 # accepted
  try:
    values={'person' : person}
    data=urllib.urlencode(values)
    req=urllib2.Request(url, data)
    rsp=urllib2.urlopen(req) # ignore response
  except urllib2.URLError, e:
    print >> sys.stderr, "cannot reach accounts, panic!"
    response.status=500 # accepted
  return "Hello, %s welcome!" % person

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
