import datetime

from google.appengine.ext import db

class Comment(db.Model):
    user = db.ReferenceProperty(indexed=False)
    message = db.StringProperty(indexed=False)
    timestamp = db.DateTimeProperty(indexed=True)

    @classmethod
    def create(cls, user, bout, message):
        cls(parent=bout, user=user, message=message, timestamp=datetime.datetime.now()).put()

    @classmethod
    def for_(cls, bout):
        return cls.all().ancestor(bout).fetch(None)

    @property
    def formatted_timestamp(self):
        posted_time_string = ""
        total_hours = int(abs((datetime.datetime.now() - self.timestamp).total_seconds()))/(3600)
        hours = total_hours%24
        days = total_hours/24
        if days >= 1:
            posted_time_string += "%s d, %s h ago"%(days, hours)
        else:
            posted_time_string += "%s h ago"%hours
        return posted_time_string
