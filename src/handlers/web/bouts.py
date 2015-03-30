import webapp2
import json
import logging

from gaesessions import get_current_session

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template

from model.user import User
from model.bout import Bout
from model.photo import Photo

class CreateBoutHandler(webapp2.RequestHandler):
	def post(self):
		name = self.request.get('name')
		period = self.request.get('period')
		email = self.request.get('email')
		user = User.get_by_key_name(email)
		Bout(parent=user, name=name, period=period).put()

	def get(self):
		template_values = {}
		path = 'templates/create_bout.html'
		self.response.out.write(template.render(path, template_values))

class AddPhotoHandler(webapp2.RequestHandler):
	def get(self):
		template_values = {}
		path = 'templates/add_photo.html'
		self.response.out.write(template.render(path, template_values))

	def post(self):
		#session = get_current_session()
		#email = session['email']
		email = self.request.get('email')
		bout_id = long(self.request.get('bout_id'))
		image = self.request.get('image')
		user = User.get_by_key_name(email)
		bout = Bout.get_by_id(bout_id)
		Photo(parent=bout, user=user, image=image).put()

class GetPhotoHandler(webapp2.RequestHandler):
    def get(self):
    	photo = Photo.all().get()
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(photo.image)

application = webapp2.WSGIApplication([	('/bouts/create', CreateBoutHandler),
										('/bouts/add_photo', AddPhotoHandler),
										('/bouts/get_photo', GetPhotoHandler)], debug=True)