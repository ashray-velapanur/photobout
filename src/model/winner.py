from google.appengine.ext import db

class Winner(db.Model):
	bout = db.ReferenceProperty(indexed=False)

	@classmethod
	def create(cls, user, bout):
		cls(key_name=str(bout.id), parent=user, bout=bout).put()

	@classmethod
	def for_(cls, user):
		return cls.all().ancestor(user).fetch(None)
