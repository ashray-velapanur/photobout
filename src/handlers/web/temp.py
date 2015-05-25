import webapp2
import time
import logging
from PyAPNs.apns import APNs, Frame, Payload

class NotifHandler(webapp2.RequestHandler):
    def get(self):
        apns = APNs(use_sandbox=True, cert_file='PhotoboutCert.pem', key_file='PhotoboutKeyNoEnc.pem')
        logging.info('Instantiated APNs')
        token_hex = 'a79449feaa2668545a43f128e531ffa63454007942b8002888ee9bf1d739c7a5'
        payload = Payload(alert="asdasd Hello World!", sound="default", badge=1)
        apns.gateway_server.send_notification(token_hex, payload)
        logging.info('... feedback_server')
        logging.info(apns.feedback_server)
        for (token_hex, fail_time) in apns.feedback_server.items():
        	logging.info(token_hex)
        	logging.info(fail_time)
        logging.info('Sent send_notification')

application = webapp2.WSGIApplication([ ('/temp/sample_notif', NotifHandler)], debug=True)
