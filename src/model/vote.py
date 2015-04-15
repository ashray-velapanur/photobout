from google.appengine.ext import db

class Vote(db.Model):
    @classmethod
    def create(cls, email, photo):
        cls(key_name=email, parent=photo).put()

    @classmethod
    def for_(cls, photo):
        return cls.all().ancestor(photo).fetch(None)

    @classmethod
    def is_voted(cls, email, photo):
        return True if cls.get_by_key_name(email, parent=photo) else False
