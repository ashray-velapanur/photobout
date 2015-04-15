from google.appengine.ext import db

class Photo(db.Model):
    user = db.ReferenceProperty(indexed=False)
    image = db.StringProperty(indexed=False)

    @classmethod
    def create(cls, bout, email, image_blob_key):
        photo = Photo(key_name=email, parent=bout, image=image_blob_key)
        photo.put()
        return photo

    @classmethod
    def for_(cls, bout):
        return cls.all().ancestor(bout).fetch(None)

    @property
    def owner_email(self):
        return self.key().name()

    @property
    def image_url(self):
        return '/bouts/photos/get?blob_key=' + self.image
