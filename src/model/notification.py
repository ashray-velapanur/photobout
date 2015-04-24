import datetime

from google.appengine.ext import db

class Notification(db.Model):
    notification_type = db.StringProperty(indexed=False)
    viewed = db.BooleanProperty(indexed=False)
    timestamp = db.DateTimeProperty(indexed=False)

    @classmethod
    def create(cls, type, user):
        cls(parent=user, notification_type=type, viewed=False, timestamp=datetime.datetime.now()).put()
