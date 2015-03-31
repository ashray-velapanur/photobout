from google.appengine.ext import db

class User(db.Model):
    name = db.StringProperty(indexed=False)
    password = db.StringProperty(indexed=False)

    @property
    def email(self):
        return self.key().name()
