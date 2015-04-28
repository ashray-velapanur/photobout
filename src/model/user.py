from webapp2_extras.security import generate_password_hash, check_password_hash

from google.appengine.ext import db
from google.appengine.ext import blobstore

from config import PEPPER

from search_documents.search_documents import UserDocument

class User(db.Model):
    name = db.StringProperty(indexed=False)
    first_name = db.StringProperty(indexed=False)
    last_name = db.StringProperty(indexed=False)
    password = db.StringProperty(indexed=False)
    profile_picture = db.StringProperty(indexed=False)

    @classmethod
    def create(cls, email, first_name, last_name, password=None):
        if not password:
            password = 'makethisrandom'
        password_hash = generate_password_hash(password, pepper=PEPPER)
        user = cls(key_name=email, first_name=first_name, last_name=last_name, password=password_hash)
        UserDocument().create(email, name="%s %s"%(first_name, last_name))
        user.put()
        return user

    @property
    def email(self):
        return self.key().name()

    @staticmethod
    def get_by_email(email):
        return User.all().filter('email =',email)

    def update_profile_picture(self, blob_key):
        if self.profile_picture:
            blobstore.delete(blob_key)
        self.profile_picture = blob_key
        self.put()