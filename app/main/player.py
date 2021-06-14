
"""

TODO:  add container limitation
TODO:  Define dominant hand. Current default dominant hand is right hand
TODO:  Define health leveling function after 0.
TODO:  Add lie and stand action.
"""

import random as random
import time as time
import textwrap as textwrap
import pathlib as pathlib
import pickle as pickle
import math as math

from app.main import config, world, mixins, items


wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)
commands = {}
global character
character = None
global terminal_output
available_stat_points = config.available_stat_points
experience_points_base = config.experience_points_base
experience_growth = config.experience_growth
profession_stats_growth_file = config.PROFESSION_STATS_GROWTH_FILE
race_stats_file = config.RACE_STATS_FILE
profession_skillpoint_bonus_file = config.PROFESSION_SKILLPOINT_BONUS_FILE
base_training_points = config.base_training_points
positions = config.positions
stances = config.stances
all_items = mixins.all_items
all_items_categories = mixins.items


def create_character(character_name=None):
    character = Player(player_name=character_name)
    return character


class Player(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, player_name: str, **kwargs):

        self._player_data = self.get_player_by_name(name=player_name)

        self._name = self._player_data['first_name']    
        self._first_name = self._player_data['first_name']
        self._last_name = self._player_data['last_name']
        self._gender = self._player_data['gender']
        self._object_pronoun = None
        self._possessive_pronoun = None
        self._race = self._player_data['race']
        self._profession = self._player_data['profession']
        self._category = self._player_data['category']
        self._position = self._player_data['position']
        self._stance = self._player_data['stance']
        
        self._level = self._player_data['level']
        self._experience = self._player_data['experience']

        self._stats = self._player_data['stats']
        self._stats_bonus = self._player_data['stats_bonus']
        self._stats_base = self._player_data['stats_base']

        self._training_points = self._player_data['training']

        self._physical_training_points = self._player_data['training']['physical_points']
        self._mental_training_points = self._player_data['training']['mental_points']

        self._skills = self._player_data['skills']
        self._skills_base = self._player_data['skills_base']
        self._skills_bonus = self._player_data['skills_bonus']
        
        self._health = self._player_data['health']
        self._health_max = self._player_data['health_max']

        self._attack_strength_base = 0

        self._defense_strength_evade_base = 0
        self._defense_strength_block_base = 0
        self._defense_strength_parry_base = 0
        
        self.mana = self._player_data['mana']

        self.money = self._player_data['money']
        
        self._armor = {}
        
        for category in self._player_data['armor']:
            for item in self._player_data['armor'][category]:
                self._armor[category] = items.create_item('armor', item_name=item)

        self._inventory = []

        for category in self._player_data['inventory']:
            for item in self._player_data['inventory'][category]:
                self._inventory.append(items.create_item(item_category=category, item_name=item))

        self._right_hand_inv = None
        if len(self._player_data['right_hand']['item_name']) != 0:
            self._right_hand_inv.append(items.create_item(item_category=self._player_data['right_hand']['item_category'], item_name=self._player_data['right_hand']['item_name']))

        self._left_hand_inv = None
        if len(self._player_data['left_hand']['item_name']) != 0:
            self._left_hand_inv.append(items.create_item(item_category=self._player_data['left_hand']['item_category'], item_name=self._player_data['left_hand']['item_name']))

        self.dominance = "right_hand"
        self.non_dominance = "left_hand"

        self.location_x, self.location_y = world.world_map.starting_position
        self.room = world.world_map.tile_exists(x=self.location_x, y=self.location_y, area='Field')
        self.area = 'Field'

        self.target = None
        self.rt_start = 0
        self.rt_end = 0
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
    
    @property        
    def first_name(self):
        return self._first_name 
    @first_name.setter
    def first_name(self, first_name):
        self._first_name = first_name
    
    @property
    def last_name(self):
        return self._last_name
    @last_name.setter
    def last_name(self, last_name):
            self._last_name = last_name
    
    @property 
    def gender(self):
            return self._gender
    @gender.setter
    def gender(self, gender):
            self._gender = gender

    @property
    def object_pronoun(self):
            return self._object_pronoun
    
    @property
    def possessive_pronoun(self):
            return self._possessive_pronoun
    def set_gender(self, gender):
            if gender.lower() == "female":
                self._object_pronoun = "she"
                self._possessive_pronoun = "her"
            if gender.lower() == "male":
                self._object_pronoun = "she"
                self._possessive_pronoun = "his"
                
    @property
    def race(self):
            return self._race

    @property            
    def profession(self):
            return self._profession
    @profession.setter
    def profession(self, profession):
            self._profession = profession
            
    @property
    def category(self):
            return self._category

    @property
    def position(self):
            return self._position[0]
    @position.setter
    def position(self, position):
            self._position = [position]
            
    def check_position_to_move(self):
        non_moving_positions = [x for x in positions if x is not 'standing']
        if set([self.position]) & set(non_moving_positions):
            return False
        else:
            return True
        
    @property
    def stance(self):
            return self._stance[0]
    @stance.setter
    def stance(self, stance):
            self._stance = [stance]
    
    @property
    def level(self):
            return self._level
    @level.setter
    def level(self, value):
            self._level = value
            
    @property
    def experience(self):
            return self._experience
    @experience.setter
    def experience(self, experience):
            self._experience = experience
        
    @property
    def stats(self):
            return self._stats  
    @stats.setter
    def set_stats(self):
            self._stats
       
    @property 
    def stats_bonus(self):
            return self._stats_bonus
    @stats_bonus.setter
    def stats_bonus(self):
            self._stats_bonus
            
    @property
    def stats_base(self):
            return self._stats_base
    @stats_base.setter
    def stats_base(self):
            self._stats_base
            
    @property
    def training_points(self):
            return self._training_points
    @training_points.setter
    def training_points(self, value):
            self._training_points = value
        
    @property
    def physical_training_points(self):
            return self._physical_training_points
    @physical_training_points.setter
    def physical_training_points(self, value):
            self._physical_training_points = value
    
    @property
    def mental_training_points(self):
            return self._mental_training_points
    @mental_training_points.setter
    def mental_training_points(self, value):
            self._mental_training_points = value
            
    @property
    def skills(self):
            return self._skills
    @skills.setter
    def skill(self):
            self._skills
    
    @property        
    def skills_bonus(self):
            return self._skills_bonus 
    @skills_bonus.setter
    def skills_bonus(self):
            self._skills_bonus
        
    @property
    def skills_base(self):
            return self._skills_base
    @skills_base.setter    
    def skills_base(self):
            self._skills_base
        
    @property
    def health(self):
            return self._health
    @health.setter
    def health(self, health):
            self._health = health
            
    @property
    def health_max(self):
            return self._health_max
    @health_max.setter
    def health_max(self, health_max):
            self._health_max = health_max
            
    @property
    def attack_strength_base(self):
            return self._attack_strength_base
    @attack_strength_base.setter
    def attack_strength_base(self, attack_strength_base):
            self._attack_strength_base = attack_strength_base
        
    @property
    def defense_strength_evade_base(self):
            return self._defense_strength_evade_base
    @defense_strength_evade_base.setter
    def defense_strength_evade_base(self, defense_strength_evade_base):
            self._defense_strength_evade_base = defense_strength_evade_base
            
    @property        
    def defense_strength_block_base(self):
            return self._defense_strength_block_base
    @defense_strength_block_base.setter
    def defense_strength_block_base(self, defense_strength_block_base):
            self._defense_strength_block_base = defense_strength_block_base
        
    @property
    def defense_strength_parry_base(self):
            return self._defense_strength_parry_base
    @defense_strength_parry_base.setter
    def defense_strength_parry_base(self, defense_strength_parry_base):
            self._defense_strength_parry_base = defense_strength_parry_base
            
    def check_level_up(self):
        experience_next_level = int(math.floor(experience_points_base * math.pow(self.level + 1, experience_growth)))
        if self.experience >= experience_next_level:
            self.level_up()
            return
        else:
            return
        
    def level_up(self):
        self.level += 1
        
        for stat in self.stats:
            self.stats[stat] = self.stats[stat] + 1 / (self.stats[stat] / int(profession_stats_growth_file.loc[self.profession][stat]))
            if self.stats[stat] > 100:
                self.stats[stat] = 100
        
            self.stats_bonus[stat] = ((self.stats[stat] - available_stat_points / 8) / 2 + int(race_stats_file.loc[self.race][stat]))
        
        skills.level_up_skill_points()
        
        self.health = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        self.health_max = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        
        self.attack_strength_base = int(round(self.stats_bonus['strength'],0))
        self.defense_strength_evade_base = int(round(self.stats_bonus['agility'] + self.stats_bonus['intellect'] / 4 + self.skills['dodging'],0))
        self.defense_strength_block_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] /4,0))
        self.defense_strength_parry_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] / 4,0))
        
        events.game_event("Ding! You are now level {}!".format(self.level)) 

    def set_character_attributes(self):
        for stat in self.stats:
            self.stats_bonus[stat] = ((self.stats[stat] - 50 / 8) / 2 + int(race_stats_file.loc[self.race][stat]))

        self.health = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        self.health_max = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        
        self.attack_strength_base = int(round(self.stats_bonus['strength'],0))
        self.defense_strength_evade_base = int(round(self.stats_bonus['agility'] + self.stats_bonus['intellect'] / 4 + self.skills['dodging'],0))
        self.defense_strength_block_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] /4,0))
        self.defense_strength_parry_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] / 4,0))

    def level_up_skill_points(self):
        stat_value = {}
        for stat in self.stats:
            stat_value[stat] = int(round(float(self.stats[stat]))) * int(profession_skillpoint_bonus_file.loc[self.profession, stat])
        added_physical_points = base_training_points + ((stat_value['strength']
                                                        + stat_value['constitution']
                                                        + stat_value['dexterity']
                                                        + stat_value['agility']) / 20)
        added_mental_points = base_training_points + ((stat_value['intellect']
                                                       + stat_value['wisdom']
                                                       + stat_value['logic']
                                                       + stat_value['spirit']) / 20)
        self.physical_training_points = self.physical_training_points + added_physical_points
        self.mental_training_points = self.mental_training_points + added_mental_points
        for skill in self.skills:
            self.skills_base[skill] = self.skills[skill]
    
    
    def add_money(self, amount):
            self.money += amount
    
    def subtract_money(self, amount):
            self.money -= amount

    def is_dead(self):
        if self.health > 0:
            return False
        else:
            events.game_event("You're dead! You will need to restart from your last saved point.")
            return True
        
    def is_killed(self):
        if self.health > 0:
            return ""
        else:
            return "Your body falls to the ground with a *slump*. You are dead."

    def check_round_time(self):
        round_time = False
        if time.time() < self.rt_end:
            round_time = True
        return round_time

    def get_round_time(self):
            return self.rt_end - time.time()

    def set_round_time(self, seconds):
        self.rt_start = time.time()
        self.rt_end = self.rt_start + seconds
        return seconds
    
    @property
    def inventory(self):
            return self._inventory
    @inventory.setter
    def inventory(self):
            self._inventory

    def check_inventory_for_item(self, item):
        for inv_item in self.inventory:
            if inv_item == item:
                return True
            if inv_item.container == True:
                for sub_inv_item in inv_item.items:
                    if sub_inv_item == item:
                        return True
        if len(self.right_hand_inv) == 1:
            if item == self.get_right_hand_inv():
                return True
        if len(self.left_hand_inv) == 1:
            if item == self.get_left_hand_inv():
                return True
        return False

    def all_inventory_handles(self):
        all_inventory_handles = []
        for item in self.inventory:
            all_inventory_handles.append(item.handle)
            if item.container == True:
                for sub_item in item.items:
                    all_inventory_handles.append(sub_item.handle)
        return all_inventory_handles
        
    @property
    def right_hand_inv(self):
        if self._right_hand_inv:
            return self._right_hand_inv
        else: return None
    @right_hand_inv.setter
    def right_hand_inv(self, item):
            self._right_hand_inv = item
    
    @property
    def left_hand_inv(self):
            if self._left_hand_inv:
                return self._left_hand_inv
            else: return None
    @left_hand_inv.setter
    def left_hand_inv(self, item):
            self._left_hand_inv = item
          
    def get_dominant_hand_inv(self):
        if self.dominance == 'right_hand':
            return self.right_hand_inv
        if self.dominance == 'left_hand':
            return self.left_hand_inv
        
    def get_non_dominant_hand_inv(self):
        if self.dominance == 'right_hand':
            return self.left_hand_inv
        if self.dominance == 'left_hand':
            return self.right_hand_inv
            
    def set_dominant_hand_inv(self, item):
        if self.dominance == 'right_hand':
            self.right_hand_inv = item
        if self.dominance == 'left_hand':
            self.left_hand_inv = item
            
    def set_non_dominant_hand_inv(self, item):
        if self.dominance == 'right_hand':
            self.left_hand_inv = item
        if self.dominance == 'left_hand':
            self.right_hand_inv = item
            
    @property
    def armor(self):
            return self._armor
    @armor.setter
    def armor(self):
            self._armor
            
    def __getstate__(self):
        """Copy the object's state from self.__dict__ which contains all our instance attributes. Always use the
        dict.copy() method to avoid modifying the original state."""
        state = self.__dict__.copy()
        del state['room']
        return state

    def __setstate__(self, state):
        """Set the object's state in self.__dict__ which contains all our instance attributes."""
        self.__dict__.update(state)
        
    def move(self, dx, dy):
        self.location_x += dx
        self.location_y += dy
        self.room = world.world_map.tile_exists(x=self.location_x, y=self.location_y, area=self.area)
        self.room.fill_room(character=self)
        return

    def move_north(self, **kwargs):
        self.move(dx=0, dy=-1)
        return

    def move_south(self, **kwargs):
        self.move(dx=0, dy=1)
        return

    def move_east(self,**kwargs):
        self.move(dx=1, dy=0)
        return

    def move_west(self, **kwargs):
        self.move(dx=-1, dy=0)
        return
    
    def get_status(self, **kwargs):
        if self.right_hand_inv is None:
            right_hand_status = "empty"
        else:
            right_hand_status = self.right_hand_inv.name
        
        if self.left_hand_inv is None:
            left_hand_status = "empty"
        else:
            left_hand_status = self.left_hand_inv.name
        
        return ["Right Hand:  {}".format(right_hand_status),
                "Left Hand:   {}".format(left_hand_status),
                "Stance:      {}".format(self.stance),
                "Position:    {}".format(self.position)]
    
    def save(self,):
        save_data = self.__getstate__()
        character_name = "{}_{}.p".format(self.first_name, self.last_name)
        path_save = pathlib.Path.cwd() / 'Profiles' / character_name
        pickle.dump(save_data, open(file=path_save.absolute().as_posix(), mode='wb'))
        events.game_event(game_event_text="Progress saved.")
        return








