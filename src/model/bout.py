from google.appengine.ext import db

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    owner = db.ReferenceProperty(indexed=False)
    period = db.StringProperty(indexed=False)

