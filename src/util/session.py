from gaesessions import get_current_session

from model.user import User
def get_user_from_session():
	session = get_current_session()
	return User.get_by_key_name(session['email']) if 'email' in session else None

