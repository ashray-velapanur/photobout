from google.appengine.ext import db

class Photo(db.Model):
    user = db.ReferenceProperty()
    image = db.StringProperty(indexed=False)

    @classmethod
    def create(cls, bout, user, image_blob_key):
        photo = Photo(key_name=user.email, parent=bout, image=image_blob_key, user=user)
        photo.put()
        return photo

    @classmethod
    def for_(cls, bout):
        return cls.all().ancestor(bout).fetch(None)

    @classmethod
    def for_user_(cls, user):
        return Photo.all().filter('user', user).fetch(None)

    @property
    def owner_email(self):
        return self.key().name()

    @property
    def bout(self):
        return self.parent()

    @property
    def image_url(self):
        return '/bouts/photos/get?blob_key=' + self.image
