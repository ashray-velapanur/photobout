from datetime import datetime

from google.appengine.ext import db

from flufl import enum

from model.user import User
from model.comment import Comment
from model.photo import Photo
from model.enum_property import EnumProperty

Permission =  enum.make("Permission", ("PUBLIC", "PRIVATE"))

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    description = db.TextProperty(indexed=False)
    owner = db.ReferenceProperty(indexed=False)
    created_at = db.DateTimeProperty(indexed=False)
    period = db.IntegerProperty(indexed=False)
    permission = EnumProperty(Permission)

    @classmethod
    def create(cls, user, name, description, period, permission):
        bout = Bout(owner=user, name=name, description=description, period=int(period), permission=int(permission), created_at=datetime.now())
        bout.put()
        return bout

    @property
    def id(self):
        return self.key().id()

    @property
    def comments(self):
        return Comment.all().ancestor(self).fetch(None)

    @property
    def photos(self):
        return Photo.all().ancestor(self).fetch(None)

