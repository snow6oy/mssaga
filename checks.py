#!/usr/bin/python
'''
checks microservice
'''
import bottle
from bottle import route, run, request

if __name__ == '__main__':
  #cas=CASClient()
  server=bottle.app()

  @route('/checks', method='post')
  def new_check():
    ''' 
    check if person is allowed an account
    '''
    person=request.forms.get('person')
    check=dict()
    check['results']={'person':'camilla', 'pass':True}
    return check

  run(app=server, host='0.0.0.0', port=5002)
