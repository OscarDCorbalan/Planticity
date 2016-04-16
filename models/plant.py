import json
import logging
import random
from google.appengine.ext import ndb

# Load species data
# TODO put it in memcache to speed things up
PLANT_SPECIES = json.loads(open('plant_species.json', 'r').read())['species']

# Status
SEED = 'seed'
PLANTED  = 'planted'
PLANT = 'plant'
# Actions
WAIT = 'wait'
PLANT_SEED = 'plant seed'
WATER = 'water'
FUNGICIDE = 'fungicide'
# Dictionary of status:[list of possible actions for this status]
STATUS_ACTIONS = {
    SEED: [
        PLANT_SEED,
        FUNGICIDE
    ],
    PLANTED: [
        WAIT,
        WATER
    ],
    PLANT:[
        WAIT,
        WATER,
        FUNGICIDE
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
    # % amounts present
    # fungicide = ndb.IntegerProperty(required=True, default=True)
    # insecticide = ndb....
    # Infection markers
    fungi = ndb.BooleanProperty(required=True, default=False)
    # insects = ndb.StringProperty()

    @classmethod
    def new_plant(cls):
        # TODO add more species, choose randomly
        variety =  PLANT_SPECIES['Pisum Sativum']
        logging.debug(PLANT_SPECIES)
        logging.debug(variety)
        plant = Plant(name = variety['name'],
                      common_name = variety['common_name'],
                      look = "It's a %s seed" %variety['common_name'])
        plant._update_look()
        plant.put()
        logging.debug('plant', plant)
        return plant

    # Interaction with plant

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
        if action == FUNGICIDE:
            logging.debug('_interact_seed: fungicide seed')
            self._fungicide()

    def _interact_planted(self, action):
        if action == WATER:
            logging.debug('_interact_planted: water planted')
            self._water()

    def _interact_plant(self, action):
        if action == WATER:
            logging.debug('_interact_plant: water plant')
            self._water()
        if action == FUNGICIDE:
            logging.debug('_interact_plant: fungicide plant')
            self._fungicide()

    def end_day(self):
        data = PLANT_SPECIES[self.name]

        self.age += 1

        # Reduce soil moisture
        lost_water = random.randint(10, 20)
        self.moisture = max(self.moisture - lost_water, 0)

        # Advance plant stages
        if self.age == data['days']['germinate']:
            self._germinate()

        # Let the Nature do its miracle (cell mitosis)
        if self.status == PLANT:
            # Add % of growth_rate
            day_growth = 0.01 * (100-self.stress) * data['growth_rate']
            logging.debug('end_day growth: %s', day_growth)
            self.size += int(day_growth)

        # Roll fungi chance
        if self.status != SEED and not self.fungi:
            fungi_chance = data[self.status]['fungi_chance']
            dice = random.randint(0, 100)
            if fungi_chance > dice:
                self.fungi = True

        # Adjust plant stress
        if self.status == PLANT:
            moisture_diff = abs(self.moisture - data['ideal_moisture'])
            logging.debug('end_day moisture_diff: %s', moisture_diff)
            self.stress = self.stress + moisture_diff - 30
            if self.fungi:
                self.stress += 25
            self.stress = min(self.stress, 100)
            self.stress = max(self.stress, 0)
        
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
        self.stress = abs(
            self.moisture - PLANT_SPECIES[self.name]['ideal_moisture'])

    # Actions that modify the plant vars
    def _water(self):
        retained_water = random.randint(30, 70)        
        logging.debug('_water cur:%s ret:%s', self.moisture, retained_water)
        self.moisture = min(self.moisture + retained_water, 100)

    def _fungicide(self):
        logging.debug('_fungicide()')
        self.fungi = False

    def _update_look(self):
        looks = []  # Append texts and finally join them in a single string
        looks.append('Day %s' % self.age)

        if self.age == PLANT_SPECIES[self.name]['days']['germinate']:
            looks.append('The seed just germinated')

        if self.status == SEED:
            looks.append('You have a fertile seed and is time to plant it')
        elif self.status == PLANTED:
            looks.append('The seed is planted, it will germinate with patience and water')
        elif self.status == PLANT:
            looks.append('The plant is growing')

        if self.status in [PLANT]:  #, MATURE]:
            looks.append('It measures %s cm' % self.size)
            if self.fungi:
                looks.append('The plant got fungi! You should use fungicide')

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

        looks.append('Moisture: %s%%' % self.moisture)
        if self.status != SEED and self.status != PLANTED:
            looks.append('Stress: %s%%' % self.stress)

        self.look = '. '.join(looks)