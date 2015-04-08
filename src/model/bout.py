from google.appengine.ext import db

from flufl import enum

from model.user import User
from model.comment import Comment
from model.photo import Photo
from model.enum_property import EnumProperty

Permission =  enum.make("Permission", ("PUBLIC", "PRIVATE"))

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    owner = db.ReferenceProperty(indexed=False)
    period = db.StringProperty(indexed=False)
    permission = EnumProperty(Permission)

    @classmethod
    def create(cls, user, name, period, permission):
        bout = Bout(owner=user, name=name, period=period, permission=int(permission))
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
