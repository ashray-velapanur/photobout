from google.appengine.ext import db

class ThirdPartyUser(db.Model):
    access_token = db.StringProperty(indexed=False)
    id = db.StringProperty(indexed=False)
    network_id = db.StringProperty(indexed=True)

    @staticmethod
    def for_user(user):
        return ThirdPartyUser.all().ancestor(user)

    # This method currently only returns for Facebook(FB) ids
    @staticmethod
    def for_network_id(network_id):
        return ThirdPartyUser.all().filter('network_id =', network_id).get()

    @classmethod
    def for_(cls, user, network):
    	return cls.get_by_key_name(network, parent=user)

    @property
    def user(self):
        return self.parent()
