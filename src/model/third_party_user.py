from google.appengine.ext import db

class ThirdPartyUser(db.Model):
    access_token = db.StringProperty(indexed=False)
    id = db.StringProperty(indexed=False)

    @staticmethod
    def for_user(user):
        return ThirdPartyUser.all().ancestor(user)

    @classmethod
    def for_(cls, user, network):
    	return cls.get_by_key_name(network, parent=user)