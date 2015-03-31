import webapp2
import json
import logging

from gaesessions import get_current_session

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers

from model.user import User
from model.bout import Bout
from model.photo import Photo
from model.vote import Vote
from model.comment import Comment
from util import session

class CreateBoutHandler(webapp2.RequestHandler):
    def create_bout(self, user, name, period):
        Bout(owner=user, name=name, period=period).put()

    def post(self):
        user = session.get_user_from_session()
        if not user:
            return
        name = self.request.get('name')
        period = self.request.get('period')
        self.create_bout(user, name, period)

    def get(self):
        template_values = {}
        path = 'templates/create_bout.html'
        self.response.out.write(template.render(path, template_values))

class AddPhotoHandler(blobstore_handlers.BlobstoreUploadHandler):
    def create_photo(self, bout, email, image_blob_key):
        Photo(key_name=email, parent=bout, image=image_blob_key).put()

    def post(self):
        user = session.get_user_from_session()
        if not user:
            return
        email = user.key().name()
        bout_id = long(self.request.get('bout_id'))
        image_blob_key = str(self.get_uploads('image')[0].key())
        bout = Bout.get_by_id(bout_id)
        self.create_photo(bout, email, image_blob_key)

    def get(self):
        upload_url = blobstore.create_upload_url('/bouts/photos/add')
        template_values = {'upload_url': upload_url}
        path = 'templates/add_photo.html'
        self.response.out.write(template.render(path, template_values))


class GetPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        blob_key = self.request.get('blob_key')
        blob_info = blobstore.BlobInfo.get(blob_key)
        self.send_blob(blob_info)

class GetBoutsHandler(webapp2.RequestHandler):
    def get(self):
        user = session.get_user_from_session()
        if not user:
            return
        email = user.key().name()
        response = []
        bouts = Bout.all()
        for bout in bouts:
            bout_json = {}
            bout_json['id'] = bout.key().id()
            bout_json['name'] = bout.name
            bout_json['time_left'] = bout.period
            bout_json['num_comments'] = len(bout.comments)
            bout_json['photos'] = []
            photos = Photo.all().ancestor(bout)
            for photo in photos:
                owner = User.get_by_key_name(photo.key().name())
                photo_json = {}
                photo_json['image'] = '/bouts/photos/get?blob_key=' + photo.image
                photo_json['owner_email'] = owner.email
                photo_json['owner_name'] = owner.name
                photo_json['is_voted'] = photo.is_voted(email)
                bout_json['photos'].append(photo_json)
            response.append(bout_json)
        self.response.write(json.dumps(response))

class PhotoVoteHandler(webapp2.RequestHandler):
    def create_vote(self, email, photo):
        Vote(key_name=email, parent=photo).put()

    def post(self):
        user = session.get_user_from_session()
        if not user:
            return
        email = user.key().name()
        owner_email = self.request.get('owner_email')
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        photo = Photo.get_by_key_name(owner_email, parent=bout)
        self.create_vote(email, photo)

class AddCommentHandler(webapp2.RequestHandler):
    def create_comment(self, user, bout, message):
        Comment(parent=bout, user=user, message=message).put()

    def post(self):
        user = session.get_user_from_session()
        if not user:
            return
        message = self.request.get('message')
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        self.create_comment(user, bout, message)

    def get(self):
        template_values = {}
        path = 'templates/add_comment.html'
        self.response.out.write(template.render(path, template_values))

class LeaderboardHandler(webapp2.RequestHandler):
    def get(self):
        response = []
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        photos = bout.photos
        for photo in photos:
            user_dict = {}
            user_dict['votes_count'] = len(photo.votes)
            user_dict['email'] = photo.key().name()
            response.append(user_dict)
        self.response.write(response)


application = webapp2.WSGIApplication([ ('/bouts/create', CreateBoutHandler),
                                        ('/bouts/get', GetBoutsHandler),
                                        ('/bouts/leaderboard', LeaderboardHandler),
                                        ('/bouts/photos/add', AddPhotoHandler),
                                        ('/bouts/photos/get', GetPhotoHandler),
                                        ('/bouts/photos/vote', PhotoVoteHandler),
                                        ('/bouts/comments/add', AddCommentHandler)], debug=True)