import json
import logging
import random
from google.appengine.ext import ndb

# Load species data
PLANT_SPECIES = json.loads(open('plant_species.json', 'r').read())['species']

# Status
SEED = 'seed'
PLANTED  = 'planted'
# Actions
PLANT_SEED = 'plant seed'
WATER = 'water'
# Dictionary of status:[list of possible actions for this status]
STATUS_ACTIONS = {
    SEED: [
        PLANT_SEED
    ],
    PLANTED: [
        WATER
    ]
}

RANDOM = random.seed()

class Plant(ndb.Model):
    """Plant data"""
    name = ndb.StringProperty(required=True)
    common_name = ndb.StringProperty(required=True)
    age = ndb.IntegerProperty(required=True, default=0)
    size = ndb.IntegerProperty(required=True, default=0)
    status = ndb.StringProperty(required=True, default=SEED)
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
        plant._update_look()
        plant.put()
        logging.debug('plant', plant)
        return plant

    def interact(self, action):
        logging.debug('do %s in status: %s', action, self.status)

        possible_actions = STATUS_ACTIONS[self.status]
        if not action in possible_actions:
            raise NotImplementedError('Action %s not recognized!' % action)

        if self.status == SEED:
            logging.debug('Status is seed')
            if action == PLANT_SEED:
                logging.debug('Plant seed')
                self._plant_seed()
        elif self.status == PLANTED:
            if action == WATER:
                logging.debug('Water planted seed')
                self._water()
        else:
            raise NotImplementedError('Actions not implemented when not seed')
        
        self.end_day()
        return self.status

    def end_day(self):
        self.age = self.age + 1
        self._update_look()
        self.put()

    def _plant_seed(self):
        if self.status != SEED:
            raise ValueError('You have already planted your seed')
        self.status = PLANTED

    def _water(self):
        retained_water = random.randint(20, 80)
        self.moisture = min(self.moisture + retained_water, 100)

    def _update_look(self):
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

        looks.append('Age: %s' % self.age)
        looks.append('Moisture: %s' % self.moisture)
        self.look = '. '.join(looks)