from google.appengine.ext import db

from model.comment import Comment
from model.photo import Photo

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    owner = db.ReferenceProperty(indexed=False)
    period = db.StringProperty(indexed=False)

    @property
    def comments(self):
        return Comment.all().ancestor(self).fetch(None)

    @property
    def photos(self):
    	return Photo.all().ancestor(self).fetch(None)
