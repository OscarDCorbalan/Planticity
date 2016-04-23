from google.appengine.ext import ndb
from messages.messages import RankingForm
import logging

class User(ndb.Model):
    """Represents a User as an ndb Model"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    games_won = ndb.IntegerProperty(required=True, default=0)

    def get_ranking(self):
        sf = RankingForm()
        setattr(sf, 'user_name', self.name)
        setattr(sf, 'games_won', self.games_won)
        return sf
