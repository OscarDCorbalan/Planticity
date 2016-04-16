import logging
from google.appengine.ext import ndb
from messages import GameForm
from plant import Plant

class Game(ndb.Model):
    """Game object"""
    # TODO: history = ndb.????
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    plant = ndb.KeyProperty(required=True, kind='Plant')

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""

        game = Game(user=user,
                    plant = Plant.new_plant().key,
                    game_over=False)
        game.put()
        logging.debug('game:', game)
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        logging.debug('self: %s -- %s', self, message)
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_status = self.plant.get().look
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user,
                      date=date.today(),
                      won=won,
                      harvest=self.plant.get().harvested)
        score.put()