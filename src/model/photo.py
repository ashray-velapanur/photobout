from google.appengine.ext import db

from model.vote import Vote
from model.user import User

class Photo(db.Model):
    user = db.ReferenceProperty(indexed=False)
    image = db.StringProperty(indexed=False)

    @property
    def votes(self):
        return Vote.all().ancestor(self).fetch(None)

    @property
    def owner_email(self):
        return self.key().name()

    @property
    def owner(self):
        return User.get_by_key_name(self.owner_email)

    @property
    def image_url(self):
        return '/bouts/photos/get?blob_key=' + self.image

    def is_voted(self, email):
        return True if Vote.get_by_key_name(email, parent=self) else False
