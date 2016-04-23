import logging
from google.appengine.ext import ndb


class Move(ndb.Model):
    """Represents a Game move made by a user"""
    date = ndb.DateTimeProperty(required=True)
    action = ndb.StringProperty(required=True)
    result = ndb.StringProperty(required=True)
