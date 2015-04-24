from google.appengine.ext import db

class Winner(db.Model):
    bout = db.ReferenceProperty(indexed=False)

    @classmethod
    def create(cls, user, bout):
        cls(key_name=str(bout.id), parent=user, bout=bout).put()

    @classmethod
    def for_user(cls, user):
        return cls.all().ancestor(user).fetch(None)

    @classmethod
    def for_(cls, user, bout):
        return cls.get_by_key_name(str(bout.id), parent=user)

    @property
    def user(self):
        return self.parent()
