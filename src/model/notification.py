import datetime

from google.appengine.ext import db

class Notification(db.Model):
    notification_type = db.StringProperty(indexed=False)
    bout = db.ReferenceProperty(indexed=False)
    from_user = db.StringProperty(indexed=False)
    viewed = db.BooleanProperty(indexed=False)
    timestamp = db.DateTimeProperty(indexed=False)

    @classmethod
    def for_(cls, user):
        return cls.all().ancestor(user).fetch(None)

    @classmethod
    def create(cls, type, user, from_user, bout):
        cls(parent=user, notification_type=type, bout=bout, from_user=from_user, viewed=False, timestamp=datetime.datetime.now()).put()
