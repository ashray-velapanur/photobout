import datetime

import logging

from google.appengine.ext import db, deferred

from flufl import enum

from model.user import User
from model.comment import Comment
from model.photo import Photo
from model.enum_property import EnumProperty

Permission =  enum.make("Permission", ("PUBLIC", "PRIVATE"))
BoutStatus =  enum.make("BoutStatus", ("CURRENT", "PAST"))

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    description = db.TextProperty(indexed=False)
    owner = db.ReferenceProperty(indexed=False)
    created_at = db.DateTimeProperty(indexed=False)
    period = db.IntegerProperty(indexed=False)
    permission = EnumProperty(Permission)
    status = EnumProperty(BoutStatus)

    @classmethod
    def create(cls, user, name, description, period, permission):
        bout = Bout(owner=user, name=name, description=description, period=int(period), permission=int(permission), created_at=datetime.datetime.now(), status=int(BoutStatus.CURRENT))
        bout.put()
        bout.change_status()
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

    @property
    def end_time(self):
        return self.created_at + datetime.timedelta(days=self.period)

    @property
    def time_left(self):
        return self.end_time - datetime.datetime.now()

    @property
    def time_left_string(self):
        total_hours = int(self.time_left.total_seconds())/(3600)
        hours = total_hours%24
        days = total_hours/24
        if days >= 1:
            return "%s days, %s hours left"%(days, hours)
        return "%s hours left"%hours

    def change_status(self):
        deferred.defer(change_status, self, _eta=self.end_time)

def change_status(bout):
    bout.status = BoutStatus.PAST
    bout.put()
