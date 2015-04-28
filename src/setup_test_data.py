import datetime

from model.user import User
from model.third_party_user import ThirdPartyUser
from model.bout import Bout
from model.photo import Photo
from model.vote import Vote
from model.comment import Comment

def setup():
	user_1 = User.create('email1', 'firstname1', 'lastname1', 'password1')
	tp_user_1 = ThirdPartyUser(key_name='FB', parent=user_1)
	tp_user_1.network_id = 'fb_id_1'
	tp_user_1.put()
	user_2 = User.create('email2', 'firstname2', 'lasstname2', 'password2')
	tp_user_2 = ThirdPartyUser(key_name='FB', parent=user_2)
	tp_user_2.network_id = 'fb_id_2'
	tp_user_2.put()
	bout_1 = Bout.create(user_1, 'bout1', 'desc1', 1, 1)
	photo_1 = Photo.create(bout_1, user_1, 'image_blob_key_1')
	photo_2 = Photo.create(bout_1, user_2, 'image_blob_key_2')
	Vote.create('email1', photo_1)
	Vote.create('email2', photo_1)
	Vote.create('email2', photo_2)
	Comment(parent=bout_1, user=user_1, message='message', timestamp=datetime.datetime.now()).put()
	