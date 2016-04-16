import json
import logging
import random
from google.appengine.ext import ndb

# Load species data
PLANT_SPECIES = json.loads(open('plant_species.json', 'r').read())['species']

# Status
SEED = 'seed'
PLANTED  = 'planted'
PLANT = 'plant'
# Actions
WAIT = 'wait'
PLANT_SEED = 'plant seed'
WATER = 'water'
# Dictionary of status:[list of possible actions for this status]
STATUS_ACTIONS = {
    SEED: [
        WAIT,
        PLANT_SEED
    ],
    PLANTED: [
        WAIT,
        WATER
    ],
    PLANT:[
        WAIT,
        WATER
    ]
}

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
    stress = ndb.IntegerProperty()
    moisture = ndb.IntegerProperty(required=True, default=0)
    # plague = ndb.StringProperty()
    # stress = ndb.IntegerProperty(required=True, default=0)
    days_germinate = ndb.IntegerProperty(required=True)
    ideal_moisture = ndb.IntegerProperty(required=True)

    @classmethod
    def new_plant(cls):
        # TODO add more species, choose randomly
        variety =  PLANT_SPECIES['pea']
        logging.debug(PLANT_SPECIES)
        logging.debug(variety)
        plant = Plant(name = variety['name'],
                      common_name = variety['common_name'],
                      look = "It's a %s seed" %variety['common_name'],
                      days_germinate = variety['days']['germinate'],
                      ideal_moisture = variety['ideal']['moisture'])
        plant._update_look()
        plant.put()
        logging.debug('plant', plant)
        return plant

    def interact(self, action):
        logging.debug('do %s in status: %s', action, self.status)

        possible_actions = STATUS_ACTIONS[self.status]
        if not possible_actions:
            raise NotImplementedError('Status not recognized.')
        if not action in possible_actions:
            raise NotImplementedError('Action %s not recognized!' % action)

        # At this point it's secure to proceed without more checks
        if action != WAIT:
            if self.status == SEED:
                self._interact_seed(action)
            elif self.status == PLANTED:
                self._interact_planted(action)
            elif self.status == PLANT:
                self._interact_plant(action)
        
        self.end_day()
        return self.status

    def _interact_seed(self, action):
        if action == PLANT_SEED:
            logging.debug('_interact_seed: plant seed')
            self._plant_seed()

    def _interact_planted(self, action):
        if action == WATER:
            logging.debug('_interact_planted: water planted')
            self._water()

    def _interact_plant(self, action):
        if action == WATER:
            logging.debug('_interact_plant: water plant')
            self._water()

    def end_day(self):
        self.age = self.age + 1
        lost_water = random.randint(10, 30)
        self.moisture = max(self.moisture - lost_water, 0)
        if self.age == self.days_germinate:
            self._germinate()        
        self._update_look()
        self.put()

    # Methods that progress the status of the plant
    def _plant_seed(self):
        if self.status != SEED:
            raise ValueError('You have already planted your seed')
        self.status = PLANTED

    def _germinate(self):
        if not self.status == PLANTED:
            raise ValueError('Error! To germinate, status should be planted')
        self.status = PLANT
        self.stress = abs(self.moisture - self.ideal_moisture)

    # Actions that modify the plant vars
    def _water(self):
        retained_water = random.randint(20, 80)        
        logging.debug('_water cur:%s ret:%s', self.moisture, retained_water)
        self.moisture = min(self.moisture + retained_water, 100)

    def _update_look(self):
        looks = []  # Append texts and finally join them in a single string
        looks.append('Day %s' % self.age)

        if self.age == self.days_germinate:
            looks.append('The seed just germinated')

        if self.status == SEED:
            looks.append('You have a fertile seed and is time to plant it')
        elif self.status == PLANTED:
            looks.append('The seed is planted, it will germinate with patience and water')
        elif self.status == PLANT:
            looks.append('The plant is growing')

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