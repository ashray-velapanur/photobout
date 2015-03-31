from google.appengine.ext import db

class Comment(db.Model):
    user = db.ReferenceProperty(indexed=False)
    message = db.StringProperty(indexed=False)
