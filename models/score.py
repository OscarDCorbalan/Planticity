from google.appengine.ext import ndb


class Score(ndb.Model):
    """Represents a Score as an ndb Model"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    harvest = ndb.IntegerProperty(required=True)

    def to_form(self):
        """Returns a ScoreForm representation of the Score.

        Returns:
            A ScoreForm object"""
        return ScoreForm(user_name=self.user.get().name,
                         won=self.won,
                         date=str(self.date),
                         harvest=self.harvest)
