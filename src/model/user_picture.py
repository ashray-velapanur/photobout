from google.appengine.ext import db

class UserPicture(db.Model):
    blob_key = db.StringProperty(indexed=False)

    @classmethod
    def create(cls, email, blob_key):
    	cls(key_name=email, blob_key=blob_key).put()