from google.appengine.ext import db

class Follower(db.Model):

    @classmethod
    def create(cls, follower_id, following):
        cls(parent=following, key_name=follower_id).put()

    @classmethod
    def for_(cls, user):
        return cls.all().ancestor(user).fetch(None)

    @property
    def email(self):
        return self.key().name()
