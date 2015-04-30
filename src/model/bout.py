import datetime

import logging

from google.appengine.ext import db, deferred

from search_documents.search_documents import BoutDocument

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    description = db.TextProperty(indexed=False)
    owner = db.ReferenceProperty(indexed=False)
    created_at = db.DateTimeProperty(indexed=False)
    period = db.IntegerProperty(indexed=False)
    permission = db.IntegerProperty(indexed=False)
    status = db.IntegerProperty()

    @classmethod
    def create(cls, user, name, description, period, permission):
        bout = Bout(owner=user, name=name, description=description, period=int(period), permission=int(permission), created_at=datetime.datetime.now(), status=1)
        bout.put()
        BoutDocument().create(bout.id, name=name, description=description, suggestions=name)
        return bout

    @property
    def id(self):
        return self.key().id()

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
            return "%s d, %s h left"%(days, hours)
        return "%s h left"%hours

    def change_status(self, status):
        self.status = status
        self.put()
