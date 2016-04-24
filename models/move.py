from google.appengine.ext import ndb
from messages.messages import MoveForm


class Move(ndb.Model):
    """Represents a Game move made by a user"""
    date = ndb.DateTimeProperty(required=True)
    action = ndb.StringProperty(required=True)
    result = ndb.StringProperty(required=True)

    def to_form(self):
        return MoveForm(date=str(self.date),
                        action=self.action,
                        result=self.result)
