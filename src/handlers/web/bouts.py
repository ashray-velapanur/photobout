import webapp2
import json
import logging
import datetime

from gaesessions import get_current_session

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers

from model.user import User
from model.third_party_user import ThirdPartyUser
from model.bout import Bout
from model.photo import Photo
from model.vote import Vote
from model.comment import Comment
from model.invited import Invited
from util import util
from search_documents.user_document import create_user_search_document
from search_documents.search_documents import BoutDocument

class CreateBoutHandler(webapp2.RequestHandler):
    @util.login_required
    def post(self):
        user = util.get_user_from_session()
        name = self.request.get('name')
        period = self.request.get('period')
        permission = self.request.get('permission')
        description = self.request.get('description')
        if not permission:
            permission = 1
        bout = Bout.create(user, name, description, period, permission)
        util.schedule_end(bout)
        response = {'id': bout.id}
        self.response.write(json.dumps(response))

    def get(self):
        template_values = {}
        path = 'templates/create_bout.html'
        self.response.out.write(template.render(path, template_values))

class AddPhotoHandler(blobstore_handlers.BlobstoreUploadHandler):
    @util.login_required
    @util.bout_permission_required
    def post(self):
        user = util.get_user_from_session()
        bout_id = long(self.request.get('bout_id'))
        image_blob_key = str(self.get_uploads()[0].key())
        bout = Bout.get_by_id(bout_id)
        photo = Photo.create(bout, user, image_blob_key)
        
    @util.login_required
    def get(self):
        response = {'upload_url': blobstore.create_upload_url('/bouts/photos/add')}
        self.response.write(json.dumps(response))

class AddPhotoPageHandler(webapp2.RequestHandler):
    @util.login_required
    def get(self):
        template_values = {'upload_url': blobstore.create_upload_url('/bouts/photos/add')}
        path = 'templates/add_photo.html'
        self.response.out.write(template.render(path, template_values))

class GetPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    @util.login_required
    def get(self):
        blob_key = self.request.get('blob_key')
        blob_info = blobstore.BlobInfo.get(blob_key)
        self.send_blob(blob_info)

class GetBoutsHandler(webapp2.RequestHandler):
    def _get_open_bouts(self, email):
        response = []
        for bout in Bout.all().filter('status', 1):
            if bout.permission == 2:
                if bout.owner.email != user.email:
                    continue
            response.append(util.make_bout_dict(bout, email))
        return response

    def _get_current_bouts(self, email):
        response = []
        for bout in Bout.all().filter('status', 1):
            if bout.permission == 2:
                if bout.owner.email != user.email:
                    continue
            if not Photo.get_by_key_name(email, parent=bout):
                continue
            response.append(util.make_bout_dict(bout, email))
        return response

    def _get_past_bouts(self, email):
        response = []
        for bout in Bout.all().filter('status', 2):
            if bout.permission == 2:
                if bout.owner.email != user.email:
                    continue
            response.append(util.make_bout_dict(bout, email))
        return response

    @util.login_required
    def get(self):
        user = util.get_user_from_session()
        email = user.email
        status = self.request.get('status')
        bout_id = self.request.get('bout_id')
        if bout_id and len(bout_id) > 0:
            bout = Bout.get_by_id(long(bout_id))
            response = util.make_bout_dict(bout, email)
        else:
            if status == 'current':
                response = self._get_current_bouts(email)
            elif status == 'past':
                response = self._get_past_bouts(email)
            else:
                response = self._get_open_bouts(email)
        self.response.write(json.dumps(response))

class PhotoVoteHandler(webapp2.RequestHandler):
    def create_vote(self, email, photo):
        Vote(key_name=email, parent=photo).put()

    @util.login_required
    @util.bout_permission_required
    def post(self):
        user = util.get_user_from_session()
        email = user.key().name()
        owner_email = self.request.get('owner_email')
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        photo = Photo.get_by_key_name(owner_email, parent=bout)
        self.create_vote(email, photo)

class AddCommentHandler(webapp2.RequestHandler):
    def create_comment(self, user, bout, message):
        Comment(parent=bout, user=user, message=message, timestamp=datetime.datetime.now()).put()

    @util.login_required
    @util.bout_permission_required
    def post(self):
        user = util.get_user_from_session()
        message = self.request.get('message')
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        self.create_comment(user, bout, message)

    def get(self):
        template_values = {}
        path = 'templates/add_comment.html'
        self.response.out.write(template.render(path, template_values))

class GetCommentsHandler(webapp2.RequestHandler):
    @util.login_required
    @util.bout_permission_required
    def get(self):
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        response = []
        for comment in Comment.for_(bout):
            comment_dict = {}
            comment_dict['name'] = comment.user.name
            comment_dict['message'] = comment.message
            comment_dict['timestamp'] = comment.timestamp.strftime('%x %X')
            comment_dict['facebook_id'] = ThirdPartyUser.get_by_key_name('FB', parent=comment.user).id
            response.append(comment_dict)
        self.response.write(json.dumps(response))

class LeaderboardHandler(webapp2.RequestHandler):
    @util.login_required
    @util.bout_permission_required
    def get(self):
        response = []
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        for rank, photo in enumerate(sorted(Photo.for_(bout), key=lambda x: len(Vote.for_(x)), reverse=True), start=1):
            user_dict = {}
            owner = User.get_by_key_name(photo.owner_email)
            user_dict['votes'] = len(Vote.for_(photo))
            user_dict['rank'] = rank
            user_dict['email'] = photo.owner_email
            user_dict['name'] = owner.name
            user_dict['facebook_id'] = ThirdPartyUser.get_by_key_name('FB', parent=owner).id
            response.append(user_dict)
        self.response.write(json.dumps(response))

class InviteHandler(webapp2.RequestHandler):
    @util.login_required
    @util.bout_permission_required
    def post(self):
        email = self.request.get('email')
        name = self.request.get('name')
        bout_id = self.request.get('bout_id')
        user = User.get_by_key_name(email)
        if not user:
            user = User(key_name=email, name=name)
            user.put()
            create_user_search_document(user)
        Invited(key_name=bout_id, parent=user).put()
        self.response.write(json.dumps('Invited '+email))


class TestHandler(webapp2.RequestHandler):
    @util.login_required
    @util.bout_permission_required
    def get(self):
        self.response.write('... working')

application = webapp2.WSGIApplication([ ('/bouts/create', CreateBoutHandler),
                                        ('/bouts/get', GetBoutsHandler),
                                        ('/bouts/test', TestHandler),
                                        ('/bouts/leaderboard', LeaderboardHandler),
                                        ('/bouts/photos/add', AddPhotoHandler),
                                        ('/bouts/photos/add_page', AddPhotoPageHandler),
                                        ('/bouts/photos/get', GetPhotoHandler),
                                        ('/bouts/photos/vote', PhotoVoteHandler),
                                        ('/bouts/comments/add', AddCommentHandler),
                                        ('/bouts/comments/get', GetCommentsHandler),
                                        ('/bouts/invite', InviteHandler)], debug=True)
