from google.appengine.ext import db

class Following(db.model):

    @classmethod
    def create(cls, follower, following_id):
        cls(parent=follower, key_name=following_id).put()

    @classmethod
    def for_(cls, user):
        return cls.all().ancestor(user).fetch(None)