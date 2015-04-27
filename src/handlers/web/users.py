import logging
import webapp2
import json
from webapp2_extras.security import generate_password_hash, check_password_hash

from gaesessions import get_current_session, set_current_session

from google.appengine.api import urlfetch, search
from google.appengine.ext.webapp import template

from model.user import User
from model.photo import Photo
from model.winner import Winner
from model.notification import Notification
from model.invited import Invited
from model.third_party_user import ThirdPartyUser
from search_documents.user_document import create_user_search_document, fetch
from util import util
from config import PEPPER

class SignupHandler(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        name = self.request.get('name')
        password = self.request.get('password')
        confirm_password = self.request.get('confirm_password')
        User.create(email, name, password)

class LoginHandler(webapp2.RequestHandler):
    def check_password(self, email, password):
        password_hash = User.get_by_key_name(email).password
        return check_password_hash(password, password_hash, pepper=PEPPER)

    def handle_custom_login(self):
        response = {}
        email = self.request.get('email')
        password = self.request.get('password')
        if self.check_password(email, password):
            util.set_session(email)
            response['email'] = email
            return response

    def handle_facebook_login(self):
        response = {}
        access_token = self.request.get('access_token')
        user_id = self.request.get('user_id')
        profile_url = 'https://graph.facebook.com/me?access_token=%s'
        profile = json.loads(urlfetch.fetch(profile_url%access_token).content)
        email = profile['email']
        name = profile['name']
        id = profile['id']
        user = User.get_by_key_name(email)
        if not user:
            user = User.create(email, name)
            create_user_search_document(user)
        ThirdPartyUser.create('FB', user, access_token, id)
        util.set_session(email)
        response['email'] = email
        return response

    def post(self, network):
        if network == 'custom':
            response = self.handle_custom_login()
        elif network == 'facebook':
            response = self.handle_facebook_login()
        self.response.write(json.dumps(response))

class CheckSessionHandler(webapp2.RequestHandler):
    @util.login_required
    def get(self):
        session = get_current_session()
        self.response.write(session['email'] if session.has_key('email') else 'no key')

class ListUsersHandler(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        util.set_session(email)

    def get(self):
        users = User.all().fetch(None)
        emails = [user.email for user in User.all()]
        current_user = util.get_user_from_session()
        template_values = {'emails': emails, 'current_user': current_user.email if current_user else None}
        path = 'templates/list_users.html'
        self.response.out.write(template.render(path, template_values))

class UsersSearchHandler(webapp2.RequestHandler):
    def post(self):
        search_string = self.request.get('search_string')
        user_docs = fetch('(suggestions:"%s" OR name:"%s")' % (search_string, search_string), None, limit=100, sort_options=search.SortOptions(expressions=[search.SortExpression(expression='name', direction=search.SortExpression.ASCENDING)]))
        self.response.write(json.dumps({'users': [{'name':user.name, 'email':user.doc_id, 'facebook_id': user.facebook_id} for user in user_docs.results]}))

class LogoutHandler(webapp2.RequestHandler):
    @util.login_required
    def post(self):
        session = get_current_session()
        session.terminate()

class UsersBoutsHandler(webapp2.RequestHandler):
    @util.login_required
    def get(self):
        user = util.get_user_from_session()
        response = [util.make_bout_dict(photo.bout, user.email) for photo in Photo.for_user_(user)]
        self.response.write(json.dumps(response))

class UsersWinsHandler(webapp2.RequestHandler):
    @util.login_required
    def get(self):
        user = util.get_user_from_session()
        response = [util.make_bout_dict(win.bout, user.email) for win in Winner.for_user(user)]
        self.response.write(json.dumps(response))

class GetNotificationsHandler(webapp2.RequestHandler):
    @util.login_required
    def get(self):
        user = util.get_user_from_session()
        facebook_user = ThirdPartyUser.for_(user, 'FB')
        notifications = Notification.for_(user)
        response = []
        for notification in notifications:
            notification_type = notification.notification_type
            bout = notification.bout
            notification_dict = {}
            notification_dict['type'] = notification_type
            notification_dict['timestamp'] = notification.timestamp.strftime('%x %X')
            if facebook_user:
                notification_dict['facebook_id'] = facebook_user.network_id
            notification_dict['bout'] = util.make_bout_dict(bout, user.email)
            if notification_type == 'invited':
                notification_dict['invited_by'] = Invited.for_(user, bout).invited_by.name
            elif notification_type == 'winner':
                notification_dict['winner'] = Winner.for_(user, bout).user.name
            response.append(notification_dict)
        self.response.write(json.dumps(response))

application = webapp2.WSGIApplication([ ('/users/signup', SignupHandler),
                                        ('/users/logout', LogoutHandler),
                                        ('/users/notifications/get', GetNotificationsHandler),
                                        ('/users/list', ListUsersHandler),
                                        ('/users/bouts', UsersBoutsHandler),
                                        ('/users/wins', UsersWinsHandler),
                                        ('/users/([^/]+)/login', LoginHandler),
                                        ('/users/checksession', CheckSessionHandler),
                                        ('/users/search', UsersSearchHandler)], debug=True)
