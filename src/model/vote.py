from google.appengine.ext import db

import logging

class Vote(db.Model):
    photo = db.ReferenceProperty()

    @classmethod
    def create(cls, email, photo):
        cls(key_name=email, parent=photo.bout, photo=photo).put()

    @classmethod
    def for_(cls, email, bout):
        return cls.get_by_key_name(email, parent=bout)

    @classmethod
    def count(cls, photo):
        return cls.all().ancestor(photo.bout).filter('photo', photo).count()

    @classmethod
    def is_voted(cls, email, photo):
        vote = cls.get_by_key_name(email, parent=photo.bout)
        if vote and vote.photo.owner_email == photo.owner_email:
            return True
        return False
