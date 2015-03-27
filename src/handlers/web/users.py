import webapp2
from webapp2_extras.security import generate_password_hash, check_password_hash

from gaesessions import get_current_session

from model.user import User
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

class CustomLoginHandler(webapp2.RequestHandler):
    def check_password(self, email, password):
        password_hash = User.get_by_key_name(email).password
        return check_password_hash(password, password_hash, pepper=PEPPER)

    def set_session(self, email):
        pass

    def get(self):
        email = self.request.get('email')
        password = self.request.get('password')
        if self.check_password(email, password):
            self.set_session(email)


application = webapp2.WSGIApplication([('/users/signup', SignupHandler),
                                       ('/users/custom/login', CustomLoginHandler)], debug=True)