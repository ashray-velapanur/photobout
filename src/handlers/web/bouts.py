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

class CreateBoutHandler(webapp2.RequestHandler):
    def create_bout(self, user, name, period):
        Bout(owner=user, name=name, period=period).put()

    def post(self):
        name = self.request.get('name')
        period = self.request.get('period')
        email = self.request.get('email')
        user = User.get_by_key_name(email)
        self.create_bout(user, name, period)

    def get(self):
        template_values = {}
        path = 'templates/create_bout.html'
        self.response.out.write(template.render(path, template_values))

class AddPhotoHandler(blobstore_handlers.BlobstoreUploadHandler):
    def create_photo(self, bout, email, image_blob_key):
        Photo(key_name=email, parent=bout, image=image_blob_key).put()

    def post(self):
        email = self.request.get('email')
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
    def is_voted(self, photo, email):
        return True if Vote.get_by_key_name(email, parent=photo) else False

    def get(self):
        email = self.request.get('email')
        response = []
        bouts = Bout.all()
        for bout in bouts:
            bout_json = {}
            bout_json['id'] = bout.key().id()
            bout_json['name'] = bout.name
            bout_json['time_left'] = bout.period
            bout_json['photos'] = []
            photos = Photo.all().ancestor(bout)
            for photo in photos:
                photo_json = {}
                photo_json['image'] = '/bouts/photos/get?blob_key=' + photo.image
                photo_json['owner'] = photo.parent().name
                photo_json['is_voted'] = self.is_voted(photo, email)
                bout_json['photos'].append(photo_json)
            response.append(bout_json)
        self.response.write(json.dumps(response))

class PhotoVoteHandler(webapp2.RequestHandler):
    def create_vote(self, email, photo):
        Vote(key_name=email, parent=photo).put()

    def post(self):
        email = self.request.get('email')
        bout_id = long(self.request.get('bout_id'))
        bout = Bout.get_by_id(bout_id)
        photo = Photo.get_by_key_name(email, parent=bout)
        self.create_vote(email, photo)

application = webapp2.WSGIApplication([ ('/bouts/create', CreateBoutHandler),
                                        ('/bouts/get', GetBoutsHandler),
                                        ('/bouts/photos/add', AddPhotoHandler),
                                        ('/bouts/photos/get', GetPhotoHandler),
                                        ('/bouts/photos/vote', PhotoVoteHandler)], debug=True)