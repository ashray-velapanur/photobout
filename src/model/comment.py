import datetime

from google.appengine.ext import db

class Comment(db.Model):
    user = db.ReferenceProperty(indexed=False)
    message = db.StringProperty(indexed=False)
    timestamp = db.DateTimeProperty(indexed=False)

    @classmethod
    def create(cls, user, bout, message):
        cls(parent=bout, user=user, message=message, timestamp=datetime.datetime.now()).put()

    @classmethod
    def for_(cls, bout):
        return cls.all().ancestor(bout).fetch(None)
