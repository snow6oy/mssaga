#
# Bottle-CAS Client
# Written by: Kellen Fox
#
# This module aims to be a sane implementation of the CAS protocol written to be used with the bottle.py framework
#
"""
Bottle-CAS Client

CAS SSO Client for bottle applications
"""

from bottle import route, run, request, redirect, response
# for ssl
from bottle import Bottle, get, ServerAdapter
import bottle
import requests
import urlparse
from urllib import urlencode
from functools import wraps
import time
from beaker.middleware import SessionMiddleware

#  Status codes returned by function validate().
TICKET_OK      = 0        #  Valid CAS server ticket found.
TICKET_NONE    = 1        #  No CAS server ticket found.
TICKET_INVALID = 2        #  Invalid CAS server ticket found.

class CASClient():
    def __init__(self):
        import config
        self._CAS_SERVER = config.CAS_SERVER
        self._CAS_LOGOUT_URL = config.CAS_LOGOUT_URL
        self._CAS_COOKIE = config.CAS_COOKIE
        self._SECRET = config.SECRET
        self._DEBUG = config.DEBUG
        self._COOKIE_PATH = config.COOKIE_PATH
        self._SSL_SERVER = config.SSL_SERVER
        self._SSL_VERIFY = config.SSL_VERIFY

    def _do_login(self):
        url = request.urlparts
        if self._SSL_SERVER:  # bottle request should really be added to SSL wrapper ..
            newurl = (url[0]+ 's', url[1], url[2], '', url[4])
        else:
            newurl = (url[0], url[1], url[2], '', url[4])
        params = { 'service': urlparse.urlunsplit(newurl) }
        cas_url = self._CAS_SERVER + "/cas/login?" + urlencode(params)
        redirect(cas_url)

    def test_login(self, fn):
        """
        Decorator to test CAS authentication status in a bottle route

        **Note** this doesn't ensure that they are logged in, just tells you if they already are
        """

        @wraps(fn)
        def wrapper(*args, **kwargs):
            session = request.environ['beaker.session']
            if 'username' in session:
                request.environ['REMOTE_USER_STATUS'] = "VALID"
            else:
                request.environ['REMOTE_USER_STATUS'] = "INVALID"
            return fn(*args, **kwargs)
        return wrapper


    def require(self, fn):
        """
        Decorator to enable CAS authentication for a bottle route

        :Usage:
           from bottle_cas import client
           cas = client()

           @route('/foo')
           @cas.require
           def foo():
          NOTE: The require statement must be used between the route definition and the function.
                If using an additional authentication scheme (LDAP) this should be defined below the CAS require

        :returns: A wrapped route that requres CAS authentication
        :rtype: `function`
        """

        @wraps(fn)
        def wrapper(*args, **kwargs):
            #cookie = request.get_cookie(self._CAS_COOKIE, secret=self._SECRET)
            session = request.environ['beaker.session']
            ticket = request.query.ticket;
            if 'username' in session:
                if self._DEBUG:
                    print "Valid Cookie Found"
                request.environ['REMOTE_USER'] = session['username']
                return fn(*args, **kwargs)
            elif ticket:
                if self._DEBUG:
                    print "Ticket: %s recieved" % ticket
                status, user = self._validate(ticket)
                if status==TICKET_OK:
                    if self._DEBUG:
                        print "Ticket OK"
                    session['username'] = user
                    session.save()

                    # Remove the query variables from uri
                    url = request.urlparts
                    if self._SSL_SERVER:  # bottle request should know about SSL ?
                        newurl = (url[0]+ 's', url[1], url[2], '', url[4])
                    else:
                        newurl = (url[0], url[1], url[2], '', url[4])
                    redirect(urlparse.urlunsplit(newurl))
                    #return fn(*args, **kwargs)
                else:
                    raise Exception("Ticket Validation FAILED!")
            self._do_login()
        return wrapper

    def require_user(self, users=None):
        """
        Decorator to permit access only to the given list of CAS-authenticated users.

        :Usage:
           from bottle_cas import client
           cas = client()

           @route('/foo')
           @cas.require
           @cas.require_user(['longb4'])
           def foo():

        :returns: A wrapped route that requires the authenticated user to be in the given access list
        :rtype: `function`
        """
        def required_user_decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                current_user = request.environ.get('REMOTE_USER')
                valid_user = False
                if not current_user:
                    # The wrapped route probably doesn't have @cas.require above this decorator call
                    bottle.abort(403, "No user detected")
                if users:
                    if current_user in users:
                        valid_user = True
                    else:
                        message = "Permission denied: {} is not an authorized user.".format(current_user)
                if valid_user:
                    return fn(*args, **kwargs)
                else:
                    # User unauthorized
                    bottle.abort(401, message)
            return wrapper
        return required_user_decorator

    def logout(self, next = None):
        """
        Will Redirect a user to the CAS logout page

        :returns: Will not return
        :rtype: `None`
        """
        new_url = self._CAS_SERVER + self._CAS_LOGOUT_URL

        if next:
            next = '?url=' + urlencode(next)
            new_url = new_url + next
        session = request.environ['beaker.session']
        session.delete()
        #response.set_cookie(self._CAS_COOKIE, '', expires=0)
        if self._DEBUG:
            print "User logged out with request %s" %new_url
        redirect(new_url)

    # A function to grab a xml tag. This isn't the best possible implementation but it works
    # It also doesn't require an external library
    def _parse_tag(self, str,tag):
        """
        Internal Function to parse a specific xml tag

        :Usage:
            _parse_tag(foo_string, "tag")

        :returns: the text contained within the tag specified
        :returns: `string`
        """
        tag1_pos1 = str.find("<" + tag)
        #  No tag found, return empty string.
        if tag1_pos1==-1: return ""
        tag1_pos2 = str.find(">",tag1_pos1)
        if tag1_pos2==-1: return ""
        tag2_pos1 = str.find("</" + tag,tag1_pos2)
        if tag2_pos1==-1: return ""
        return str[tag1_pos2+1:tag2_pos1].strip()

    # Validate the CAS ticket using CAS version 2
    def _validate(self, ticket):
        """
        Internal function to validate a CAS ticket

        :returns: ticket_status and username
        :rtype: `int` and `string`
        """
        url = request.urlparts
        if self._SSL_SERVER:
            newurl = urlparse.urlunsplit((url[0]+ 's', url[1], url[2], '', url[4]))
        else:
            newurl = urlparse.urlunsplit((url[0],url[1],url[2],'',url[4]))
        params = { 'ticket': ticket, 'service': newurl }
        url_string = self._CAS_SERVER + "/cas/serviceValidate?" + urlencode(params)
        validate_resp = requests.get(url_string, verify=self._SSL_VERIFY)
        resp = validate_resp.text
        user = self._parse_tag(resp, "cas:user")

        if user=='':
            return TICKET_INVALID, ""
        else:
            return TICKET_OK, user

    def encrypt(self):
        if self._SSL_SERVER:
            return True
        return False

class CASMiddleware(SessionMiddleware):
    def __init__(self, app):
        SessionMiddleware.__init__(self, app, self.get_beaker_opts())

    def get_beaker_opts(self):
        import config
        return  {
            'session.type': 'memory',
            'session.cookie_expires': True,
            'session.secure': not config.ALLOW_HTTP,
            'session.timeout': config.TIMEOUT,
            'session.validate_key': config.CAS_COOKIE + config.SECRET,
            'session.encrypt_key': config.SECRET,
            }

# from bottle-ssl
# https://github.com/mfm24/miscpython/blob/master/bottle_ssl.py
# copied from bottle. Only changes are to import ssl and wrap the socket
class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl

        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
            srv.socket,
            certfile='server.pem',  # path to certificate
            server_side=True)

        startup = """Bottle server starting up (using SSLWSGIRefServer())...
Listening on https://%s:%s/
Hit Ctrl-C to quit.
"""
        print startup  % (self.host, self.port)        
        srv.serve_forever()

if __name__ == '__main__':
    cas = CASClient()
    app = bottle.app()
    from beaker.middleware import SessionMiddleware
    from ProxyMiddleware.ProxyMiddleware import ReverseProxied
    application = ReverseProxied(CASMiddleware(app))

    @route('/')
    def index():
        user = request.environ.get('REMOTE_USER') or 'default'
        resp =  """
            <a href="/app">Login</a> | <a href="#register">Register</a>
            """
        return resp

    @route('/test')
    @cas.test_login
    def test():
        return request.environ.get('REMOTE_USER_STATUS')

    @route('/app')
    @cas.require
    def login():
        user = request.environ.get('REMOTE_USER')
        return "Hello, %s. This is a CAS client written in bottle\n <a href='logout'>Logout</a>" %user

    @route('/logout')
    def log_out():
        cas.logout()

    if cas.encrypt():
        ssl_server=SSLWSGIRefServer(host="0.0.0.0", port=7443)
        run(app=application, server=ssl_server, quiet=True) # stay quiet to hide startup message
    else:
        run(app=application, host='0.0.0.0', port=7000)
