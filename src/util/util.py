import logging

from google.appengine.ext import deferred
from gaesessions import get_current_session

from model.vote import Vote
from model.photo import Photo
from model.user import User
from model.winner import Winner
from model.bout import Bout
from model.comment import Comment
from model.third_party_user import ThirdPartyUser

def make_bout_dict(bout, email):
    bout_dict = {}
    bout_dict['id'] = bout.id
    bout_dict['name'] = bout.name
    bout_dict['description'] = bout.description
    bout_dict['time_left'] = bout.time_left_string
    bout_dict['num_comments'] = len(Comment.for_(bout))
    bout_dict['photos'] = []
    for photo in Photo.for_(bout):
        photo_dict = {}
        owner = User.get_by_key_name(photo.owner_email)
        photo_dict['image'] = photo.image_url
        photo_dict['owner_email'] = photo.owner_email
        photo_dict['owner_name'] = owner.name
        photo_dict['num_votes'] = len(Vote.for_(photo))
        photo_dict['is_voted'] = Vote.is_voted(email, photo)
        photo_dict['facebook_id'] = ThirdPartyUser.get_by_key_name('FB', parent=owner).network_id
        bout_dict['photos'].append(photo_dict)
    return bout_dict

def schedule_end(bout):
    deferred.defer(set_winner, bout, _eta=bout.end_time)

def set_winner(bout):
    winner = User.get_by_key_name(sorted(Photo.for_(bout), key=lambda x: len(Vote.for_(x)), reverse=True)[0].owner_email)
    Winner.create(winner, bout)
    bout.change_status(2)

def _user_has_permission(handler):
	bout_id = long(handler.request.get('bout_id'))
	bout = Bout.get_by_id(bout_id)
	if not bout:
		logging.info('... invalid bout id')
		return False
	if bout.permission == 1:
		logging.info('... public bout')
		return True
	user = session.get_user_from_session()
	if bout.owner.email == user.email:
		logging.info('... is owner')
		return True
	if Photo.get_by_key_name(user.email, parent=bout):
		logging.info('... is participant')
		return True
	return False

def bout_permission_required(fn):
    def check_permission(self, *args):
        if _user_has_permission(self):
            fn(self, *args)
    return check_permission

def get_user_from_session():
	session = get_current_session()
	return User.get_by_key_name(session['email']) if 'email' in session else None

def set_session(email):
    session = get_current_session()
    session['email'] = email

def _user_logged_in(handler):
    session = get_current_session()
    if session.is_active() and 'email' in session:
        if User.get_by_key_name(session['email']):
	        return True
        session.terminate()
    return False

def login_required(fn):
    def check_login(self, *args):
        if _user_logged_in(self):
            fn(self, *args)
    return check_login
