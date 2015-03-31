from google.appengine.ext import db

from model.comment import Comment

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    owner = db.ReferenceProperty(indexed=False)
    period = db.StringProperty(indexed=False)

    @property
    def comments(self):
        return Comment.all().ancestor(self).fetch(None)
