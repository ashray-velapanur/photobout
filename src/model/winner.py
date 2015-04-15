from google.appengine.ext import db

class Winner(db.Model):
	@classmethod
	def create(cls, user, bout):
		cls(parent=user).put()

