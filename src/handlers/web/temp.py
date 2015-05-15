import webapp2
import time
import logging
from PyAPNs.apns import APNs, Frame, Payload

class NotifHandler(webapp2.RequestHandler):
    def get(self):
        apns = APNs(use_sandbox=True, cert_file='PhotoboutCert.pem', key_file='PhotoboutKeyNoEnc.pem')
        logging.info('Instantiated APNs')
        token_hex = '879825c6931847225caf5f015e9605b415d7c3688c7b4c548a77cb6ad65e2f94'
        payload = Payload(alert="Hello World!", sound="default", badge=1)
        apns.gateway_server.send_notification(token_hex, payload)
        logging.info('Sent send_notification')

application = webapp2.WSGIApplication([ ('/temp/sample_notif', NotifHandler)], debug=True)
