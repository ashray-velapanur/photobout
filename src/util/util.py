import logging

from google.appengine.ext import deferred
from gaesessions import get_current_session

from model.vote import Vote
from model.photo import Photo
from model.user import User
from model.winner import Winner
from model.bout import Bout

def schedule_end(bout):
    deferred.defer(set_winner, bout, _eta=bout.end_time)

def set_winner(bout):
    winner = User.get_by_key_name(sorted(Photo.for_(bout), key=lambda x: len(Vote.for_(x)), reverse=True)[0].owner_email)
    Winner.create(winner, bout)

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
