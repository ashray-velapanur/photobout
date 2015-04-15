from google.appengine.ext import db

class Winner(db.Model):
	@classmethod
	def create(cls, user, bout):
		cls(key_name=str(bout.id), parent=user).put()

