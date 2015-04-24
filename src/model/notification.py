import datetime

from google.appengine.ext import db

MESSAGES = {
    'invited': "%s invited you to %s."
}

class Notification(db.Model):
    message = db.StringProperty(indexed=False)
    viewed = db.BooleanProperty(indexed=False)
    timestamp = db.DateTimeProperty(indexed=False)

    @classmethod
    def create(cls, type, user, *args):
        message = MESSAGES[type]%args
        cls(parent=user, message=message, viewed=False, timestamp=datetime.datetime.now()).put()
