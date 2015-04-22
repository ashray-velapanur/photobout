from google.appengine.ext import db

class Invited(db.Model):
    timestamp = db.DateTimeProperty(indexed=False)
    invited_by = db.ReferenceProperty(indexed=False)

    @classmethod
    def for_(cls, user):
        return cls.all().ancestor(user).fetch(None)