import json
import logging
import random
from google.appengine.ext import ndb

# Load species data
# TODO put it in memcache to speed things up
PLANT_SPECIES = json.loads(open('models/plant_species.json', 'r').read())['species']
TEXTS = json.loads(open('models/plant_texts.json', 'r').read())['texts']

# Status
SEED = 'seed'
PLANTED  = 'planted'  # Seed in soil
PLANT = 'plant'       # Growing plant
MATURE = 'mature'     # Mature plant = flowering
YIELD = 'yield'       # Game ended

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
    PLANT: [
        ACTIONS['WAIT'],
        ACTIONS['WATER'],
        ACTIONS['FUNGICIDE'],
        ACTIONS['FUMIGATE'],
        ACTIONS['FERTILIZE']
    ],
    MATURE: [
        ACTIONS['WAIT'],
        ACTIONS['WATER'],
        ACTIONS['FUNGICIDE'],
        ACTIONS['FUMIGATE'],
        ACTIONS['FERTILIZE']
    ],
    YIELD: []
}

class Plant(ndb.Model):
    """Plant data"""
    name = ndb.StringProperty(required=True)
    common_name = ndb.StringProperty(required=True)
    age = ndb.IntegerProperty(required=True, default=0)
    size = ndb.FloatProperty(required=True, default=0)
    status = ndb.StringProperty(required=True, default=SEED)
    stress = ndb.IntegerProperty(required=True, default=0)
    moisture = ndb.IntegerProperty(required=True, default=0)
    flowers = ndb.IntegerProperty(required=True, default=0)
    # Gives hints about moisture, stress...
    look = ndb.StringProperty()
    # Amount of fertilizer in soil
    fertilizer = ndb.IntegerProperty(required=True, default=0)
    # Days of preventive effect left
    fungicide = ndb.IntegerProperty(required=True, default=0)
    fumigation = ndb.IntegerProperty(required=True, default=0)
    # Infection markers
    fungi = ndb.BooleanProperty(required=True, default=False)
    plague = ndb.BooleanProperty(required=True, default=False)
    dead = ndb.BooleanProperty(required=True, default=False)
    # Ideas for game extension
    # place = ndb.StringProperty() # Potted, soil...
    # light = ndb.StringProperty() # Sun, semi or shadow

    @classmethod
    def new_plant(cls):
        # TODO add more species, choose randomly
        variety =  PLANT_SPECIES['Tester Plantum']
        plant = Plant(name = variety['name'],
                      common_name = variety['common_name'],
                      look = "It's a %s seed" %variety['common_name'])
        plant._update_look()
        plant.put()
        logging.debug('plant', plant)
        return plant

    def yielded(self):
        return self.status == YIELD

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

        self._end_day()
        return self.status

    def _end_day(self):
        data = PLANT_SPECIES[self.name]

        if self.status != SEED:
            self.age += 1
            self.fungicide -= 1 if self.fungicide > 0 else 0
            self.fumigation -= 1 if self.fumigation > 0 else 0
            self.fertilizer -= 1 if self.fertilizer > 0 else 0

        # Advances plant stages
        self._evolve(data)

        # Reduce soil moisture
        self._consume_water()

        # Let the Nature do its miracle (cell mitosis)
        if self.status == PLANT:
            self._grow(data)

        # Let flowers grow!
        if self.status == MATURE:
            self._blossom(data)

        
        if self.status in [PLANT, MATURE]:
            # Roll against fungi and plague chances
            self._roll_fungi(data)
            self._roll_plague(data)
            # Adjust plant stress
            self._calc_plant_stress(data)
        
        self._update_look()

    def _evolve(self, data):
        if self.age == data['evolution']['germination']:
            self._germinate()
        elif self.age == data['evolution']['maturity']:
            self._mature()
        elif self.age == data['evolution']['yield']:
            self._yield()

    def _consume_water(self):
        lost_water = random.randint(10, 20)
        self.moisture = max(self.moisture - lost_water, 0)

    def _grow(self, data):
        # Add % of growth_rate
        day_growth = 0.01 * (100-self.stress) * data['growth_rate']
        # Add up to 33% of normal growth rate if fertilizing is ok
        fertilizer_diff = abs(self._get_fertilizer_diff(data))
        if fertilizer_diff < 10:
            multiplier = 0.033 * (10 - fertilizer_diff)
            extra_growth = multiplier * data['growth_rate']
            logging.debug('extra_growth: %s', extra_growth)
            day_growth += extra_growth
        logging.debug('end_day growth: %s', day_growth)
        self.size = round(self.size + day_growth, 1)

    def _blossom(self, data):
        fertilizer_diff = abs(self._get_fertilizer_diff(data))
        if fertilizer_diff < 20:
            fertilizer_diff = fertilizer_diff * 0.05 
        else:
            fertilizer_diff = 0.4
        fertile_factor = 1.2 - fertilizer_diff
        growth_factor = self.size / data['adult_size']
        stress_factor = 1 - 0.01 * self.stress            
        random_factor = 0.01 * random.randint(90, 110)
        flower_factor = growth_factor * stress_factor * random_factor
        logging.debug('flower factors %s*%s*%s*%s=%s', fertile_factor, growth_factor, stress_factor, random_factor, flower_factor)

        daily_flowers = data[self.status]['flowers_day']            
        fertile_flowers = flower_factor * daily_flowers

        self.flowers += int(fertile_flowers)

    def _roll_fungi(self, data):
        if not self.fungi and self.fungicide == 0:
            fungi_chance = data[self.status]['fungi_chance']
            dice = random.randint(0, 100)
            if fungi_chance > dice:
                self.fungi = True

    def _roll_plague(self, data):
        if not self.plague and self.fumigation == 0:
            plague_chance = data[self.status]['plague_chance']
            dice = random.randint(0, 100)
            if plague_chance > dice:
                self.plague = True

    def _calc_plant_stress(self, data):
        moisture_diff = abs(self._get_moisture_diff(data))
        self.stress += moisture_diff - 30  # 30 = ok moisture margin
        if self.fungi:
            self.stress += 25
        if self.plague:
            self.stress += 25
        # Add stress if fertilized +- 20% of ideal
        fertilizer_diff = abs(self._get_fertilizer_diff(data))
        if fertilizer_diff > 20:
            self.stress += fertilizer_diff - 20
        self.stress = min(self.stress, 100)
        self.stress = max(self.stress, 0)

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

    def _mature(self):
        if not self.status == PLANT:
            raise ValueError(
                'Error! To mature and start flowering, status should be plant')
        self.status = MATURE

    def _yield(self):
        if not self.status == MATURE:
            raise ValueError(
                'Error! To yield, the status should be mature')
        self.status = YIELD
        self.dead = True

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

    def _get_fertilizer_diff(self, data):
        ideal_fertilizer = data[self.status]['ideal_fertilizer']
        return self.fertilizer - ideal_fertilizer

    def _get_moisture_diff(self, data):
        return self.moisture - data['ideal_moisture']

    def _add_stress(self, amount):
        assert amount >= 0
        self.stress = min(self.stress + amount, 100)

    def _update_look(self):
        data = PLANT_SPECIES[self.name]

        if self.status == YIELD:
            self.look = 'Game completed! Final yield %s' % self.flowers
            return

        looks = []  # Append texts and finally join them in a single string
        looks.append('Day %s' % self.age)

        if self.age == data['evolution']['germination']:
            looks.append(TEXTS['germinated'])

        looks.append(TEXTS['status'][self.status])

        if self.status in [PLANT, MATURE]:
            looks.append(TEXTS['plant_size'] % self.size)
            if self.fungi:
                looks.append(TEXTS['conditions']['fungi'])
            if self.plague:
                looks.append(TEXTS['conditions']['plague'])

        if self.status == MATURE:
            plural = 's' if self.flowers > 1 else ''
            looks.append(TEXTS['fertilized_flowers'] % (self.flowers, plural))

        looks.append(self._get_moisture_text())

        if self.fungicide > 0:
            looks.append(self._get_effect_text('fungicide', self.fungicide))

        if self.fumigation > 0:
            looks.append(self._get_effect_text('fumigation', self.fumigation))

        if self.status in [PLANT, MATURE]:
            fertilizer_diff = self._get_fertilizer_diff(data)
            if fertilizer_diff < -20:
                looks.append(TEXTS['fertilization']['lack'])
            elif fertilizer_diff > 20:
                looks.append(TEXTS['fertilization']['toxic'])
            elif fertilizer_diff > -10 and fertilizer_diff < 10:
                looks.append(TEXTS['fertilization']['ok'])

        looks.append('Moisture: %s%%' % self.moisture)
        looks.append('Fertilizer: %s%%' % self.fertilizer)
        if self.status not in [SEED, PLANTED]:
            looks.append('Stress: %s%%' % self.stress)

        self.look = '. '.join(looks)

    def _get_moisture_text(self):
        moisture_index = '0'
        if self.moisture == 0:
            moisture_index = '1'
        elif self.moisture < 25:
            moisture_index = '2'
        elif self.moisture < 50:
            moisture_index = '3'
        elif self.moisture < 75:
            moisture_index = '4'
        else:
            moisture_index = '5'
        return TEXTS['moisture'][moisture_index]

    def _get_effect_text(self, text, num):
        plural = 's' if num > 1 else ''
        return TEXTS['effect_days'] % (text, num, plural)
