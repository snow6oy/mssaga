#!/usr/bin/python
'''
micoservices saga
'''
import urllib, urllib2, sys, json
import bottle
from bottle import route, run, request, response, static_file


class restOrchestrator():

  def __init__(self):
    self.accounts=dict()

  def log_account(self, person, status):
    ''' 
    create account for given person by POST to accounts (not done yet :)
    return 201 and Location to GET /accounts/:person
    '''
    self.accounts[person]={'status':status}
    print self.accounts.items()

  def check_person(self, person):
    url='http://localhost:5002/checks'
    try:
      values={'person' : person}
      data=urllib.urlencode(values)
      req=urllib2.Request(url, data)
      rsp=urllib2.urlopen(req)
    except urllib2.URLError, e:
      print >> sys.stderr, '%s running chek' % e
      return 2
    text=rsp.read()
    if text:
      check=json.loads(text)
      print(check['results']['pass'])
      if check['results']['pass']:
        return 0
    return 1

if __name__ == '__main__':
  ro=restOrchestrator()
  server=bottle.app()

  @route('/accounts', method='post')
  def accounts():
    person=request.forms.get('person')
    status=ro.check_person(person)
    if status==0:
      ro.log_account(person, 'CREATE')
    elif status==1:
      ro.log_account(person, 'DECLINE')
    elif status==2:
      ro.log_account(person, 'PENDING')
    return None

  run(app=server, host='0.0.0.0', port=5003)
