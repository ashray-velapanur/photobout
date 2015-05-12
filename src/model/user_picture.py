from google.appengine.ext import db
from google.appengine.ext import blobstore

class UserPicture(db.Model):
    blob_key = db.StringProperty(indexed=False)

    @classmethod
    def create(cls, email, blob_key):
        cls(key_name=email, blob_key=blob_key).put()

    @classmethod
    def update(cls, email, blob_key):
        user_picture = cls.for_(email)
        old_blob_key = user_picture.blob_key
        blobstore.delete(old_blob_key)
        user_picture.blob_key = blob_key
        user_picture.put()

    @classmethod
    def for_(cls, email):
        return cls.get_by_key_name(email)