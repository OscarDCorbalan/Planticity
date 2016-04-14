import json
import logging
from google.appengine.ext import ndb
from protorpc import messages


# Load species data
PLANT_SPECIES = json.loads(open('plant_species.json', 'r').read())['species']


# Messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    
class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_status = messages.StringField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    harvest = messages.IntegerField(4, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    action = messages.StringField(1, required=True)

# ndb models

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Plant(ndb.Model):
    """Plant data"""
    name = ndb.StringProperty(required=True)
    common_name = ndb.StringProperty(required=True)
    age = ndb.IntegerProperty(required=True, default=0)
    size = ndb.IntegerProperty(required=True, default=0)
    status = ndb.StringProperty(required=True, default="seed")
    # place = ndb.StringProperty() # Potted or soil...
    # light = ndb.StringProperty() #Sun, semi or shadow
    # Gives hints about moisture, stress...
    look = ndb.StringProperty()
    # Internal data, user can't directly see these numbers
    moisture = ndb.IntegerProperty(required=True, default=0)
    # plague = ndb.StringProperty()
    # stress = ndb.IntegerProperty(required=True, default=0)

    @classmethod
    def new_plant(cls):
        # TODO add more species, choose randomly
        variety =  PLANT_SPECIES['pea']
        logging.debug(PLANT_SPECIES)
        logging.debug(variety)
        plant = Plant(name = variety['name'],
                      common_name = variety['common_name'],
                      look = "It's a %s seed" %variety['common_name'])
        plant.update_look()
        plant.put()
        logging.debug('plant', plant)
        return plant

    def interact(self, action):
        logging.debug(action)
        logging.debug(self.status)
        if self.status == 'seed':
            logging.debug('Status is  seed')
            if action == 'plant seed':
                self.plant_seed()
                logging.debug('Plant seed')
                # do something
            elif action == 'fungicide':
                # TODO
                logging.debug('Fungicide not implemented')
            elif action == 'insecticide':
                # TODO
                logging.debug('Insecticide not implemented')
            else:
                logging.debug('raise')
                raise NotImplementedError('Action %s not possible!' % action)
        else:
            # TODO
            raise NotImplementedError('Actions not implemented when not seed')
        self.increment_age()
        self.put()
        return self.status

    def increment_age(self):
        self.age = self.age + 1
        self.put()

    def plant_seed(self):
        if self.status != 'seed':
            raise ValueError('You have already planted your seed')
        self.status = "planted"
        self.update_look()
        self.put()

    def update_look(self):
        looks = []  # Append texts and finally join them in a single string
        if self.status == 'seed':
            looks.append('You have a fertile seed and is time to plant it')
        elif self.status == 'planted':            
            looks.append('The seed is planted, it will germinate with patience and water')

        if self.moisture == 0:
            looks.append('The soil is completely dry')
        elif self.moisture < 25:
            looks.append('The soil looks quite dry')
        elif self.moisture < 50:
            looks.append('The soil is moist')
        elif self.moisture < 75:
            looks.append('The soil is wet')
        else:
            looks.append('The soil is swamped')

        looks.append('Moisture: %s' % self.moisture)
        self.look = '. '.join(looks)


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
        logging.debug('self:', self, '------', message)
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


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    harvest = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
                         won=self.won,
                         date=str(self.date),
                         harvest=self.harvest)
