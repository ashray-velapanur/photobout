import logging
import webapp2
import json
from webapp2_extras.security import generate_password_hash, check_password_hash

from gaesessions import get_current_session, set_current_session

from google.appengine.api import urlfetch, search
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

from model.user import User
from model.photo import Photo
from model.winner import Winner
from model.notification import Notification
from model.invited import Invited
from model.third_party_user import ThirdPartyUser
from model.follower import Follower
from model.following import Following
from search_documents.search_documents import UserDocument
from util import util
from config import PEPPER

class SignupHandler(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        password = self.request.get('password')
        confirm_password = self.request.get('confirm_password')
        if password == confirm_password:
            user = User.get_by_key_name(email)
            if user:
                response = {"success": False, "error": "Email already in use."}
            else:
                User.create(email, first_name, last_name, password)
                util.set_session(email)
                response = {"success": True}
        else:
            response = {"success": False, "error": "Passwords don't match."}
        self.response.write(json.dumps(response))

class LoginHandler(webapp2.RequestHandler):
    def check_password(self, email, password):
        password_hash = User.get_by_key_name(email).password
        return check_password_hash(password, password_hash, pepper=PEPPER)

    def handle_custom_login(self):
        email = self.request.get('email')
        password = self.request.get('password')
        user = User.get_by_key_name(email)
        if user and self.check_password(email, password):
            util.set_session(email)
            response = {"success": True, "email": email, "first_name": user.first_name, "last_name": user.last_name}
        else:
            response = {"success": False, "error": "The email or password you entered is incorrect."}
        return response

    def handle_facebook_login(self):
        access_token = self.request.get('access_token')
        user_id = self.request.get('user_id')
        profile_url = 'https://graph.facebook.com/me?access_token=%s'
        profile = json.loads(urlfetch.fetch(profile_url%access_token).content)
        id = profile['id']
        if not id == user_id:
            response = {"success": False, "error": "Facebook ids don't match."}
        else:
            email = profile['email']
            user = User.get_by_key_name(email)
            if not user:
                user = User.create(email, profile['first_name'], profile['last_name'])
            ThirdPartyUser.create('FB', user, access_token, id)
            util.set_session(email)
            response = {"success": True, "email": email, "first_name": user.first_name, "last_name": user.last_name}
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
        results = UserDocument().fetch(search_string)
        response = {}
        response['users'] = []
        for user in results:
            facebook_user = ThirdPartyUser.for_(User.get_by_key_name(user['id']), 'FB')
            user_dict = {}
            user_dict['name'] = user['fields']['name']
            user_dict['id'] = user['id']
            if facebook_user:
                user_dict['facebook_id'] = facebook_user.network_id
            response['users'].append(user_dict)
        self.response.write(json.dumps(response))

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


def make_notification_dict(notification):
    notification_type = notification.notification_type
    bout = notification.bout
    from_user = User.get_by_key_name(notification.from_user)
    from_facebook_user = ThirdPartyUser.for_(from_user, 'FB')
    notification_dict = {}
    notification_dict['type'] = notification_type
    notification_dict['timestamp'] = notification.formatted_timestamp
    if notification_type == 'winner':
        notification_dict['from_name'] = 'You'
    else:
        notification_dict['from_name'] = from_user.name
    if from_facebook_user:
        notification_dict['from_id'] = from_facebook_user.network_id
    elif from_user:
        notification_dict['from_id'] = from_user.email
    notification_dict['bout'] = util.make_bout_dict(bout, notification.user.email)
    notification_dict['message'] = notification.message
    return notification_dict

class GetNotificationsHandler(webapp2.RequestHandler):
    @util.login_required
    def get(self):
        next = self.request.get('next')
        user = util.get_user_from_session()
        response = util.fetch_with_cursor(Notification.all().ancestor(user).order("-timestamp"), limit=20, cursor=next, mapper=make_notification_dict)
        self.response.write(json.dumps(response))

class AddProfilePictureHandler(blobstore_handlers.BlobstoreUploadHandler):
    @util.login_required
    def post(self):
        email = util.get_email_from_session()
        image_blob_key = str(self.get_uploads()[0].key())
        User.update(email, profile_picture=image_blob_key)

    @util.login_required
    def get(self):
        response = {'upload_url': blobstore.create_upload_url('/users/profile_picture/add')}
        self.response.write(json.dumps(response))

class GetProfilePictureHandler(blobstore_handlers.BlobstoreDownloadHandler):
    @util.login_required
    def get(self):
        email = self.request.get('email')
        user = User.get_by_key_name(email)
        blob_key = user.profile_picture
        if blob_key:
            blob_info = blobstore.BlobInfo.get(blob_key)
            self.send_blob(blob_info)

class AddProfilePicturePageHandler(webapp2.RequestHandler):
    @util.login_required
    def get(self):
        template_values = {'upload_url': blobstore.create_upload_url('/users/profile_picture/add')}
        path = 'templates/add_profile_photo.html'
        self.response.out.write(template.render(path, template_values))

class UpdateProfileHandler(webapp2.RequestHandler):
    @util.login_required
    def post(self):
        user = util.get_user_from_session()
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        User.update(user.email, first_name=first_name, last_name=last_name)

class AddFollowerHandler(webapp2.RequestHandler):
    @util.login_required
    def post(self):
        follower = util.get_user_from_session()
        following_email = self.request.get('following')
        following = User.get_by_key_name(following_email)
        if following:
            Follower.create(follower.email, following)
            Following.create(follower, following_email)


application = webapp2.WSGIApplication([ ('/users/signup', SignupHandler),
                                        ('/users/logout', LogoutHandler),
                                        ('/users/update_profile', UpdateProfileHandler),
                                        ('/users/notifications/get', GetNotificationsHandler),
                                        ('/users/profile_picture/add', AddProfilePictureHandler),
                                        ('/users/profile_picture/get', GetProfilePictureHandler),
                                        ('/users/profile_picture/add_page', AddProfilePicturePageHandler),
                                        ('/users/followers/add', AddFollowerHandler),
                                        ('/users/list', ListUsersHandler),
                                        ('/users/bouts', UsersBoutsHandler),
                                        ('/users/wins', UsersWinsHandler),
                                        ('/users/([^/]+)/login', LoginHandler),
                                        ('/users/checksession', CheckSessionHandler),
                                        ('/users/search', UsersSearchHandler)], debug=True)
