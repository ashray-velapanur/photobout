from google.appengine.ext import db

from model.user import User

class Photo(db.Model):
    user = db.ReferenceProperty(indexed=False)
    image = db.StringProperty(indexed=False)

