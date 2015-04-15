from webapp2_extras.security import generate_password_hash, check_password_hash

from google.appengine.ext import db

from config import PEPPER

class User(db.Model):
    name = db.StringProperty(indexed=False)
    password = db.StringProperty(indexed=False)

    @classmethod
    def create(cls, email, name, password):
        password_hash = generate_password_hash(password, pepper=PEPPER)
        user = cls(key_name=email, name=name, password=password_hash)
        user.put()
        return user

    @property
    def email(self):
        return self.key().name()

    @staticmethod
    def get_by_email(email):
        return User.all().filter('email =',email)