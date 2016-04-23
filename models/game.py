import logging
from datetime import date
from google.appengine.ext import ndb
from messages.messages import GameForm
from models.score import Score
from plant import Plant

class Game(ndb.Model):
    """Represents a Game object as an ndb Model"""
    # TODO: history = ndb.????
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    plant = ndb.KeyProperty(required=True, kind='Plant')

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game.

        Args:
            user: User Model that owns (parent of) the game.

        Returns:
            A new game Model."""

        game = Game(user = user,
                    plant = Plant.new_plant().key,
                    game_over = False)
        game.put()
        logging.debug('new_game:', game)
        return game

    def take_action(self, action):
        """Modifies the game state by performing an action.

        Args:
            action: String representing the action performed by the user.

        Returns:
            A string explaining the result of the action."""

        plant_ref = self.plant.get()
        try:
            action_result = plant_ref.interact(action)
            plant_ref.put()
            if plant_ref.dead:
                self.end_game(plant_ref.yielded())
        except NotImplementedError as e:
            raise e

        return action_result

    def to_form(self, message=None):
        """Returns a GameForm representation of the Game,

        Args:
            message: Game info to append on the returned
            GameForm object.

        Returns:
            A GameForm object which contains the message parameter in its
            .message field"""
        # logging.debug('self: %s -- %s', self, message)
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_status = self.plant.get().look
        form.game_over = self.game_over
        if not self.game_over and message:
            form.message = message
        elif not self.game_over and not message:
            form.message = 'Your turn!'
        elif self.game_over:
            form.message = 'Game already over!'
        return form

    def end_game(self, won=False):
        """Ends the game.

        Args:
            won: if won is True, the player won, else the player lost."""
        self.game_over = True

        user = self.user.get()
        if won:
            user.games_won += 1

        # Add the game to the score 'board'
        score = Score(user=self.user,
                      date=date.today(),
                      won=won,
                      harvest=self.plant.get().flowers)
        
        score.put()
        user.put()
        self.put()