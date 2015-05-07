from google.appengine.ext import db

class Following(db.model):
    user = db.ReferenceProperty(indexed=False)

    @classmethod
    def create(cls, follower, following):
        cls(parent=follower, user=following).put()

    @classmethod
    def for_(cls, user):
        return cls.all().ancestor(user).fetch(None)