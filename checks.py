#!/usr/bin/python
'''
checks microservice
'''
import bottle
from bottle import route, run, request, response, abort

class accountChecker():

  def new_check(self, person):
    ''' 
    check if person is allowed an account
    '''
    self.check=dict()
    if person=='camilla':
      self.check['results']={'person':'camilla', 'pass':True}
    elif person=='graham':
      self.check['results']={'person':'graham', 'pass':False}


if __name__ == '__main__':
  ac=accountChecker()
  server=bottle.app()

  @route('/checks', method='post')
  def checks():
    '''
    location header is set but GET /checks/:person is not implemented
    '''
    person=request.forms.get('person')
    ac.new_check(person)
    if 'results' in ac.check:
      response.set_header('Location', "/checks/%s" % person)
    else:
      abort(404, "No such person %s" % person)
    return ac.check

  run(app=server, host='0.0.0.0', port=5002)
