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
ACTIONS = {
    'WAIT': 'wait',
    'PLANT_SEED': 'plant seed',
    'WATER': 'water',
    'FUNGICIDE': 'fungicide',
    'FUMIGATE': 'fumigate',
    'FERTILIZE': 'fertilize'
}
# Dictionary of pairs status : [list of actions allowed]
STATUS_ACTIONS = {
    SEED: [
        ACTIONS['PLANT_SEED'],
        ACTIONS['FUNGICIDE'],
        ACTIONS['FUMIGATE'],
        ACTIONS['FERTILIZE']
    ],
    PLANTED: [
        ACTIONS['WAIT'],
        ACTIONS['WATER'],
        ACTIONS['FERTILIZE']
    ],
    PLANT:[
        ACTIONS['WAIT'],
        ACTIONS['WATER'],
        ACTIONS['FUNGICIDE'],
        ACTIONS['FUMIGATE'],
        ACTIONS['FERTILIZE']
    ]
}

class Plant(ndb.Model):
    """Plant data"""
    name = ndb.StringProperty(required=True)
    common_name = ndb.StringProperty(required=True)
    age = ndb.IntegerProperty(required=True, default=0)
    size = ndb.FloatProperty(required=True, default=0)
    status = ndb.StringProperty(required=True, default=SEED)
    # place = ndb.StringProperty() # Potted or soil...
    # light = ndb.StringProperty() #Sun, semi or shadow
    # Gives hints about moisture, stress...
    look = ndb.StringProperty()
    # Internal data, user can't directly see these numbers
    stress = ndb.IntegerProperty(required=True, default=0)
    moisture = ndb.IntegerProperty(required=True, default=0)
    # Amount of fertilizer in soil
    fertilizer = ndb.IntegerProperty(required=True, default=0)
    # Days of prevention effect left
    fungicide = ndb.IntegerProperty(required=True, default=0)
    fumigation = ndb.IntegerProperty(required=True, default=0)
    # Infection markers
    fungi = ndb.BooleanProperty(required=True, default=False)
    plague = ndb.BooleanProperty(required=True, default=False)
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
        logging.debug('executing action')
        if action == ACTIONS['WAIT']:
            logging.debug('passing')
            pass
        elif action == ACTIONS['PLANT_SEED']:
            self._plant_seed()
        elif action == ACTIONS['WATER']:
            self._water()
        elif action == ACTIONS['FUNGICIDE']:
            self._fungicide()
        elif action == ACTIONS['FUMIGATE']:
            self._fumigate()
        elif action == ACTIONS['FERTILIZE']:
            self._fertilize()

        self.end_day()
        return self.status

    def end_day(self):
        data = PLANT_SPECIES[self.name]

        self.age += 1 if self.status != SEED else 0
        self.fungicide -= 1 if self.fungicide > 0 else 0
        self.fumigation -= 1 if self.fumigation > 0 else 0
        self.fertilizer -= 1 if self.fertilizer > 0 else 0

        # Reduce soil moisture
        lost_water = random.randint(10, 20)
        self.moisture = max(self.moisture - lost_water, 0)

        # Advance plant stages
        if self.age == data['evolution']['germination']:
            self._germinate()

        # Let the Nature do its miracle (cell mitosis)
        if self.status == PLANT:
            # Add % of growth_rate
            day_growth = 0.01 * (100-self.stress) * data['growth_rate']
            # Calculate an extra growth if fertilizer is in an ok range
            ideal_fertilizer = data[self.status]['ideal_fertilizer']
            fertilizer_diff = abs(self.fertilizer - ideal_fertilizer)
            # Add up to 33% of normal growth rate if fertilizing is ok
            if fertilizer_diff < 10:
                multiplier = 0.033 * (10 - fertilizer_diff)
                extra_growth = multiplier * data['growth_rate']
                logging.debug('extra_growth: %s', extra_growth)
                day_growth += extra_growth
            logging.debug('end_day growth: %s', day_growth)
            self.size = round(self.size + day_growth, 1)

        # Roll fungi chance
        if self.status != SEED and not self.fungi and self.fungicide == 0:
            fungi_chance = data[self.status]['fungi_chance']
            dice = random.randint(0, 100)
            if fungi_chance > dice:
                self.fungi = True

        # Roll plague chance
        if self.status != SEED and not self.plague and self.fumigation == 0:
            plague_chance = data[self.status]['plague_chance']
            dice = random.randint(0, 100)
            if plague_chance > dice:
                self.plague = True

        # Adjust plant stress
        if self.status == PLANT:
            moisture_diff = abs(self.moisture - data['ideal_moisture'])
            logging.debug('end_day moisture_diff: %s', moisture_diff)
            self.stress += moisture_diff - 30  # 30 = ok moisture margin
            if self.fungi:
                self.stress += 25
            if self.plague:
                self.stress += 25
            # Add stress if fertilized +- 20% of ideal
            ideal_fertilizer = data[self.status]['ideal_fertilizer']
            fertilizer_diff = abs(self.fertilizer - ideal_fertilizer)
            if fertilizer_diff > 20:
                self.stress += fertilizer_diff - 20
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
        self.stress += abs(
            self.moisture - PLANT_SPECIES[self.name]['ideal_moisture'])

    # Actions that modify the plant vars
    def _water(self):
        retained_water = random.randint(30, 70)        
        logging.debug('_water cur:%s ret:%s', self.moisture, retained_water)
        self.moisture = min(self.moisture + retained_water, 100)

    def _fungicide(self):
        logging.debug('_fungicide()')
        self.fungi = False
        self.fungicide = 5
        self._add_stress(10)

    def _fumigate(self):
        logging.debug('_fumigate()')
        self.plague = False
        self.fumigation = 5
        self._add_stress(10)

    def _fertilize(self):
        logging.debug('_fertilize()')
        self.fertilizer = min(100, self.fertilizer + 10)

    # Helpers

    def _add_stress(self, amount):
        assert amount >= 0
        self.stress = min(self.stress + amount, 100)

    def _update_look(self):
        data = PLANT_SPECIES[self.name]

        looks = []  # Append texts and finally join them in a single string
        looks.append('Day %s' % self.age)

        if self.age == data['evolution']['germination']:
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

        if self.status in [PLANT]:  #, MATURE]:
            looks.append('It measures %s cm' % self.size)
            if self.fungi:
                looks.append('The plant got fungi! You should use fungicide')            
            if self.plague:
                looks.append('The plant got a plague! You should fumigate')

        if self.fungicide > 0:
            plural = 's' if self.fungicide > 1 else ''
            looks.append('The fungicide effect will last %s more day%s' %
                (self.fungicide, plural))

        if self.fumigation > 0:
            plural = 's' if self.fumigation > 1 else ''
            looks.append('The fumigation effect will last %s more day%s' %
                (self.fumigation, plural))

        if self.status == PLANT:
            ideal_fertilizer = data[self.status]['ideal_fertilizer']
            fertilizer_diff = self.fertilizer - ideal_fertilizer
            if fertilizer_diff < -20:
                looks.append('It seems the plant needs some extra nutrients')
            elif fertilizer_diff > 20:
                looks.append('The plant is suffering toxicity due to too much fertilizer')
            elif fertilizer_diff > -10 and fertilizer_diff < 10:
                looks.append('The fertilizer is helping the plant')

        looks.append('Moisture: %s%%' % self.moisture)
        looks.append('Fertilizer: %s%%' % self.fertilizer)
        if self.status != SEED and self.status != PLANTED:
            looks.append('Stress: %s%%' % self.stress)

        self.look = '. '.join(looks)