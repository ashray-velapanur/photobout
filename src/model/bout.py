from google.appengine.ext import db

class Bout(db.Model):
    name = db.StringProperty(indexed=False)
    period = db.StringProperty(indexed=False)

