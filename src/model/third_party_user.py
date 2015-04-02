from google.appengine.ext import db

class ThirdPartyUser(db.Model):
    access_token = db.StringProperty(indexed=False)
    id = db.StringProperty(indexed=False)
