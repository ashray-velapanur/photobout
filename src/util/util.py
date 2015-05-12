import logging
import json
    
from google.appengine.ext import deferred
from gaesessions import get_current_session
from google.appengine.api import mail
from google.appengine.api import urlfetch

from model.vote import Vote
from model.photo import Photo
from model.user import User
from model.winner import Winner
from model.bout import Bout
from model.comment import Comment
from model.following import Following
from model.notification import Notification
from model.third_party_user import ThirdPartyUser

MAIL_TEMPLATES = {
    'forgot_password': {
        'subject': 'Password Reset',
        'body': "Click to reset password: {template_values[reset_link]}"
    }
}

def get_profile_picture(user):
    if user.profile_picture:
        return "/users/profile_picture/get?email=%s"%user.email
    else:
        facebook_user = ThirdPartyUser.for_(user, 'FB')
        if facebook_user:
            response = json.loads(urlfetch.fetch("http://graph.facebook.com/%s/picture?redirect=false"%facebook_user.network_id).content)
            return response['data']['url']

def fetch_with_cursor(query, limit=10, cursor=None, mapper=None):
    response = {}
    response['data'] = []
    if cursor:
        query.with_cursor(start_cursor=cursor)
    for count, result in enumerate(query):
        mapper_response = mapper(result)
        if mapper_response:
            response['data'].append(mapper_response)
            if count >= limit - 1:
                break
    response['next'] = None if len(response['data']) < limit else query.cursor()
    return response

def send_mail(to, template, **kwargs):
    subject = MAIL_TEMPLATES[template]['subject']
    body = MAIL_TEMPLATES[template]['body'].format(template_values=kwargs)
    sender = "support@b-eagles.com"
    mail.send_mail(sender=sender, to=to, subject=subject, body=body)

def make_bout_dict(bout, email):
    bout_dict = {}
    bout_dict['id'] = bout.id
    bout_dict['name'] = bout.name
    bout_dict['description'] = bout.description
    bout_dict['time_left'] = bout.time_left_string
    bout_dict['ended'] = bout.ended
    bout_dict['num_comments'] = len(Comment.for_(bout))
    bout_dict['photos'] = []
    for photo in sorted(Photo.for_(bout), key=lambda x: Vote.count(x), reverse=True):
        photo_dict = {}
        owner = User.get_by_key_name(photo.owner_email)
        photo_dict['image'] = photo.image_url
        photo_dict['owner_email'] = photo.owner_email
        photo_dict['owner_first_name'] = owner.first_name
        photo_dict['owner_last_name'] = owner.last_name
        photo_dict['num_votes'] = Vote.count(photo)
        photo_dict['is_voted'] = Vote.is_voted(email, photo)
        photo_dict['profile_picture'] = get_profile_picture(owner)
        bout_dict['photos'].append(photo_dict)
    if bout.ended:
        bout_dict['winner'] = ''
        winner = Winner.for_bout(bout)
        if winner:
            bout_dict['winner'] = winner.user.email
    return bout_dict

def schedule_end(bout):
    deferred.defer(set_winner, bout, _eta=bout.end_time)

def set_winner(bout):
    bout.change_status(2)
    participants = sorted(Photo.for_(bout), key=lambda x: Vote.count(x), reverse=True)
    if len(participants) > 0 and Vote.count(participants[0]) > 0:
        winner = User.get_by_key_name(participants[0].owner_email)
        Winner.create(winner, bout)
        Notification.create('winner', winner, winner.email, bout)

def _user_has_permission(handler):
    bout_id = long(handler.request.get('bout_id'))
    bout = Bout.get_by_id(bout_id)
    if not bout:
        logging.info('... invalid bout id')
        return False
    if bout.permission == 1:
        logging.info('... public bout')
        return True
    email = get_email_from_session()
    if bout.owner.email == email:
        logging.info('... is owner')
        return True
    if Following.for_(bout.owner, email):
        logging.info('... following')
        return True
    logging.info('... no permission')
    return False

def bout_permission_required(fn):
    def check_permission(self, *args):
        if _user_has_permission(self):
            fn(self, *args)
    return check_permission

def get_user_from_session():
    session = get_current_session()
    return User.get_by_key_name(session['email']) if 'email' in session else None

def get_email_from_session():
    session = get_current_session()
    return session['email'] if 'email' in session else None

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
