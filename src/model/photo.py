from google.appengine.ext import db

from model.vote import Vote

class Photo(db.Model):
    user = db.ReferenceProperty(indexed=False)
    image = db.StringProperty(indexed=False)

    @property
    def votes(self):
    	return Vote.all().ancestor(self).fetch(None)

    def is_voted(self, email):
        return True if Vote.get_by_key_name(email, parent=self) else False
