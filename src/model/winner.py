from google.appengine.ext import db

class Winner(db.Model):
    user = db.ReferenceProperty()

    @classmethod
    def create(cls, user, bout):
        cls(parent=bout, key_name=user.email ,user=user).put()

    @classmethod
    def for_user(cls, user):
        return cls.all().filter('user', user).fetch(None)

    @classmethod
    def for_bout(cls, bout):
        return cls.all().ancestor(bout).fetch(None)

    @property
    def bout(self):
        return self.parent()

    @property
    def email(self):
        return self.key().name()