import webapp2
import json
from webapp2_extras.security import generate_password_hash, check_password_hash

from gaesessions import get_current_session, set_current_session

from google.appengine.api import urlfetch

from model.user import User
from model.third_party_user import ThirdPartyUser
from config import PEPPER

class SignupHandler(webapp2.RequestHandler):
    def create_user(self, email, name, password):
        password_hash = generate_password_hash(password, pepper=PEPPER)
        User(key_name=email, name=name, password=password_hash).put()

    def get(self):
        email = self.request.get('email')
        name = self.request.get('name')
        password = self.request.get('password')
        confirm_password = self.request.get('confirm_password')
        self.create_user(email, name, password)

class LoginHandler(webapp2.RequestHandler):
    def check_password(self, email, password):
        password_hash = User.get_by_key_name(email).password
        return check_password_hash(password, password_hash, pepper=PEPPER)

    def set_session(self, email):
        session = get_current_session()
        session['email'] = email

    def handle_custom_login(self):
        email = self.request.get('email')
        password = self.request.get('password')
        if self.check_password(email, password):
            self.set_session(email)

    def handle_facebook_login(self):
        access_token = self.request.get('access_token')
        user_id = self.request.get('user_id')
        profile_url = 'https://graph.facebook.com/me?access_token=%s'
        response = json.loads(urlfetch.fetch(profile_url%access_token).content)
        self.response.write(response)

    def get(self, network):
        if network == 'custom':
            self.handle_custom_login()
        elif network == 'facebook':
            self.handle_facebook_login()

class CheckSessionHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        self.response.write(session['email'] if session.has_key('email') else 'no key')

application = webapp2.WSGIApplication([('/users/signup', SignupHandler),
                                       #('/users/custom/login', CustomLoginHandler),
                                       ('/users/([^/]+)/login', LoginHandler),
                                       ('/users/checksession', CheckSessionHandler)], debug=True)