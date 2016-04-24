#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging
import webapp2
from google.appengine.api import mail, app_identity
from models.game import Game
from models.user import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User that has unfinished games.
        Called every hour using a cron job"""
        logging.info('[Cron job] Started: SendReminderEmail')

        app_id = app_identity.get_application_id()
        num_sent = 0
        for user in User.query(User.email != None):
            games = Game.query(Game.game_over == False,
                               Game.user == user.key)
            urlsafes = [game.key.urlsafe() for game in games]
            if len(urlsafes) > 0:
                self._send_email(app_id, user, urlsafes)
                num_sent += 1
        logging.info('[Cron job] Finished: SendReminderEmail. Sent %s emails',
                     num_sent)

    def _send_email(self, app_id, user, urlsafes):
        str_urlafes = ', '.join(urlsafe for urlsafe in urlsafes)

        subject = 'Planticity reminder!'
        body = "Hey {}, you've got {} unfinished games! " \
               "Your game keys are: {}." \
               .format(user.name, len(urlsafes), str_urlafes)
        # This will send emails, the arguments to send_mail are:
        # from, to, subject, body
        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       user.email,
                       subject,
                       body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)
], debug=True)
