from google.appengine.ext import ndb


class User(ndb.Model):
    """Represents a User as an ndb Model"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
