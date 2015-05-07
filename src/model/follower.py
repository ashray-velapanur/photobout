from google.appengine.ext import db

class Follower(db.model):
    user = db.ReferenceProperty(indexed=False)

    @classmethod
    def create(cls, follower, following):
        cls(parent=following, user=follower).put()

    @classmethod
    def for_(cls, user):
        return cls.all().ancestor(user).fetch(None)