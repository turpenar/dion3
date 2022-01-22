
"""

TODO:  add container limitation
TODO:  Define dominant hand. Current default dominant hand is right hand
TODO:  Define health leveling function after 0.
TODO:  Add lie and stand action.
"""

import time as time
import textwrap as textwrap
import math as math

from app import db
from app.main import config, world, mixins, items, skills, routes


wrapper = textwrap.TextWrapper(width=config.TEXT_WRAPPER_WIDTH)
commands = {}
available_stat_points = config.AVAILABLE_STAT_POINTS
stat_bonus_denominator = config.STAT_BONUS_DENOMINATOR
experience_points_base = config.EXPERIENCE_POINTS_BASE
experience_growth = config.EXPERIENCE_POINTS_BASE
profession_stats_growth_file = config.PROFESSION_STATS_GROWTH_FILE
heritage_stats_file = config.HERITAGE_STATS_FILE
profession_skillpoint_bonus_file = config.PROFESSION_SKILLPOINT_BONUS_FILE
base_training_points = config.BASE_TRAINING_POINTS
skills_max_factors = config.SKILLS_MAX_FACTORS
all_items = mixins.all_items
all_items_categories = mixins.items
mana_regeneration_base_percentage = config.MANA_REGENERATION_BASE_PERCENTAGE


def create_character(character_name=None):
    character = Player(player_name=character_name)
    return character


class Player(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, player_name: str, **kwargs):

        self._player_data = self.get_player_by_name(name=player_name)

        self._name: str = None
        self._first_name: str = None
        self._last_name: str = None
        self._gender: config.Gender = None
        self._profession : config.Profession = None
        self._heritage: config.Heritage = None
        self._object_pronoun: str = None
        self._possessive_pronoun: str = None
        self._position: config.Position =  None
        self._stance: config.Stance = None
        
        self._level = self._player_data['level']
        self._experience = self._player_data['experience']

        self._stats = self._player_data['stats']
        self._stats_bonus = self._player_data['stats_bonus']
        self._stats_base = self._player_data['stats_base']

        self._training_points = self._player_data['training']

        self._physical_training_points = self._player_data['training']['physical_points']
        self._mental_training_points = self._player_data['training']['mental_points']

        self._skills = self._player_data['skills']
        self._skills_max = self._player_data['skills_max']
        self._skills_bonus = self._player_data['skills_bonus']

        self._spells = self._player_data['spells']
        self._active_spell = None
        
        self._health = self._player_data['health']
        self._health_max = self._player_data['health_max']
        self._depart = False

        self._attack_strength_base = 0
        self._cast_strength_base = 0

        self._defense_strength_evade_base = 0
        self._defense_strength_block_base = 0
        self._defense_strength_parry_base = 0
        
        self._mana_base = self._player_data['mana']
        self._mana = self._player_data['mana']
        self._mana_max = 0

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

        self.dominance = "right"
        self.non_dominance = "left"

        self.location_x, self.location_y = world.starting_position
        self.area_name = world.starting_area

        self._in_shop = False
        self._shop_item_selected = None

        self.target = None
        self._rt_base = 5
        self._rt_start = 0
        self._rt_end = 0
        self._cast_rt_start = 0
        self._cast_rt_end = 0
    
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
            if gender == config.Gender.Female:
                self._object_pronoun = "she"
                self._possessive_pronoun = "her"
            if gender == config.Gender.Male:
                self._object_pronoun = "he"
                self._possessive_pronoun = "him"
                
    @property
    def heritage(self):
            return self._heritage
    @heritage.setter
    def heritage(self, heritage):
        self._heritage = heritage

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
            return self._position
    @position.setter
    def position(self, position):
            self._position = position
            
    def check_position_to_move(self):
        if self.position == config.Position.standing:
            return True
        else:
            return False

    @property
    def stance(self):
            return self._stance
    @stance.setter
    def stance(self, stance):
            self._stance = stance
    
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
    def skills_max(self):
            return self._skills_max
    @skills_max.setter    
    def skills_max(self):
            self._skills_max

    @property
    def spells(self):
            return self._spells
    @spells.setter
    def spells(self):
        self._spells

    @property
    def active_spell(self):
        return self._active_spell
    @active_spell.setter
    def active_spell(self, active_spell):
        self._active_spell = active_spell
        
    @property
    def health(self):
            return self._health
    @health.setter
    def health(self, health):
            self._health = health

    @property
    def depart(self):
            return self._depart
    @depart.setter
    def depart(self, depart):
            self._depart = depart
            
    @property
    def health_max(self):
            return self._health_max
    @health_max.setter
    def health_max(self, health_max):
            self._health_max = health_max

    def regenerate_health(self):
        if self.health_max - self.health < 2:
            self.health = self.health_max
        elif self.health < self.health_max:
            self.health += 2
        return
            
    @property
    def attack_strength_base(self):
            return self._attack_strength_base
    @attack_strength_base.setter
    def attack_strength_base(self, attack_strength_base):
            self._attack_strength_base = attack_strength_base

    def calculate_attack_strength(self):
        attack_strength = self.attack_strength_base
        if self.get_dominant_hand_inv():
            if self.get_dominant_hand_inv().category == 'weapon':
                weapon_bonus = self.skills_bonus[self.get_dominant_hand_inv().sub_category] 
                attack_strength += weapon_bonus
        return attack_strength

    @property
    def cast_strength_base(self):
        return self._cast_strength_base
    @cast_strength_base.setter
    def cast_strength_base(self, cast_strength_base):
        self._cast_strength_base = cast_strength_base
        
    @property
    def defense_strength_evade_base(self):
            return self._defense_strength_evade_base
    @defense_strength_evade_base.setter
    def defense_strength_evade_base(self, defense_strength_evade_base):
            self._defense_strength_evade_base = defense_strength_evade_base

    def calculate_defense_strength_evade(self):
        return int(self.defense_strength_evade_base + self.skills['dodging'])

    def calculate_defense_strength_block(self):
        return int(self.defense_strength_evade_base + self.skills['shield'])

    def calculate_defense_strength_parry(self):
        defense_strength_parry = int(self.defense_strength_evade_base + self.skills['dodging'])
        if self.get_dominant_hand_inv():
            if self.get_dominant_hand_inv().category == 'weapon':
                weapon_ranks = self.skills[self.get_dominant_hand_inv().sub_category]
                defense_strength_parry += int(weapon_ranks)
        return defense_strength_parry

    def calculate_defense_strength(self):
        return self.calculate_defense_strength_evade() + self.calculate_defense_strength_block() + self.calculate_defense_strength_parry()
            
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

    @property
    def mana_base(self):
        return self._mana_base
    @mana_base.setter
    def mana_base(self, mana_base):
        self._mana_base = mana_base

    @property
    def mana(self):
        return self._mana
    @mana.setter
    def mana(self, mana):
        self._mana = mana

    @property
    def mana_max(self):
        return self._mana_max
    @mana_max.setter
    def mana_max(self, mana_max):
        self._mana_max = mana_max

    def regenerate_mana(self):
        if self.mana_max - self.mana < int(self.mana_max * mana_regeneration_base_percentage):
            self.mana = self.mana_max
        elif self.mana < self.mana_max:
            self.mana += int(self.mana_max * mana_regeneration_base_percentage)
        return

    def pulse_attributes(self):
        self.regenerate_health()
        self.regenerate_mana()
        return

            
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
            self.stats[stat] = self.stats[stat] + 1 / (self.stats[stat] / int(profession_stats_growth_file.loc[self.profession.name][stat]))
            if self.stats[stat] > 100:
                self.stats[stat] = 100
        
            self.stats_bonus[stat] = int((self.stats[stat] - stat_bonus_denominator) / 2 + int(heritage_stats_file.loc[self.heritage.name][stat]))
        
        skills.level_up_skill_points(character=self)

        self.health = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        self.health_max = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))

        self.attack_strength_base = int(round(self.stats_bonus['strength'],0))
        self.cast_strength_base = int(round(self.stats_bonus['dexterity'],0))
        self.defense_strength_evade_base = int(round(self.stats_bonus['agility'] + self.stats_bonus['intellect'] / 4 + self.skills['dodging'],0))
        self.defense_strength_block_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] /4,0))
        self.defense_strength_parry_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] / 4,0))
        
        routes.character_announcement(f"Ding! You are now level {self.level}!") 

    def set_character_attributes(self):
        for stat in self.stats:
            self.stats_bonus[stat] = int((self.stats[stat] - stat_bonus_denominator) / 2 + int(heritage_stats_file.loc[self.heritage.name][stat]))

        self.health = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        self.health_max = int(math.floor((self.stats['strength'] + self.stats['constitution']) / 10))
        
        self.attack_strength_base = int(round(self.stats_bonus['strength'],0))
        self.cast_strength_base = int(round(self.stats_bonus['dexterity']))
        self.defense_strength_evade_base = int(round(self.stats_bonus['agility'] + self.stats_bonus['intellect'] / 4 + self.skills['dodging'],0))
        self.defense_strength_block_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] /4,0))
        self.defense_strength_parry_base = int(round(self.stats_bonus['strength'] / 4 + self.stats_bonus['dexterity'] / 4,0))
 
        if self.stats_bonus['intellect'] + self.stats_bonus['wisdom'] > 0:
            self.mana_base = int((self.stats_bonus['intellect'] + self.stats_bonus['wisdom']) / 4)
            self.mana = int((self.stats_bonus['intellect'] + self.stats_bonus['wisdom']) / 4)
            self.mana_max = int((self.stats_bonus['intellect'] + self.stats_bonus['wisdom']) / 4)

    def check_spells_forget(self, spell_base, spell_numbers):
        spells_forget = list(set(self.spells[spell_base.lower()]) - set(spell_numbers))
        if len(spells_forget) > 0:
            spell_data_file = config.get_spell_data_file()
            spell_output = ""
            for spell in spells_forget:
                spell_output = spell_output + f"""\
    {spell} - {spell_data_file[spell_base.lower()][str(spell)]["name"]}\
                    """
            return spell_output
        else:
            return None

    def check_spells_learned(self, spell_base, spell_numbers):
        spells_learned = list(set(spell_numbers) - set(self.spells[spell_base.lower()]))
        if len(spells_learned) > 0:
            spell_data_file = config.get_spell_data_file()
            spell_output = ""
            for spell in spells_learned:
                spell_output = spell_output + f"""\
    {spell} - {spell_data_file[spell_base.lower()][str(spell)]["name"]}\
                    """
            return spell_output
        else:
            return None

    def learn_spells(self, spell_base, spell_numbers):
        self.spells[spell_base.lower()] = spell_numbers
        return

    def get_spell_output(self):
        spell_data_file = config.get_spell_data_file()
        spell_output = ""
        for category in self.spells:
            for spell in self.spells[category]:
                spell_output = spell_output + f"""\
{spell} - {spell_data_file[category][str(spell)]["name"]}\
                """
        return spell_output
                
    def add_money(self, amount):
            self.money += amount
    
    def subtract_money(self, amount):
            self.money -= amount

    def is_dead(self):
        if self.health > 0:
            return False
        else:
            return True
        
    def is_killed(self):
        if self.health > 0:
            return ""
        else:
            self.position = config.Position.lying
            return "Your body falls to the ground with a *slump*. You are dead."

    @property
    def rt_base(self):
        return self._rt_base
    @rt_base.setter
    def rt_base(self, rt_base):
        self._rt_base = rt_base

    @property
    def rt_start(self):
        return self._rt_start
    @rt_start.setter
    def rt_start(self, rt_start):
        self._rt_start = rt_start

    @property
    def rt_end(self):
        return self._rt_end
    @rt_end.setter
    def rt_end(self, rt_end):
        self._rt_end = rt_end

    @property
    def cast_rt_start(self):
        return self._cast_rt_start
    @cast_rt_start.setter
    def cast_rt_start(self, cast_rt_start):
        self._cast_rt_start = cast_rt_start

    @property
    def cast_rt_end(self):
        return self._cast_rt_end
    @cast_rt_end.setter
    def cast_rt_end(self, cast_rt_end):
        self._cast_rt_end = cast_rt_end

    def get_round_time_base(self):
        return self.rt_base

    def check_round_time(self):
        round_time = False
        if time.time() < self.rt_end:
            round_time = True
        return round_time

    def get_round_time(self):
            return int(self.rt_end - time.time())

    def set_round_time(self, seconds):
        self.rt_start = time.time()
        self.rt_end = self.rt_start + seconds
        return seconds

    def check_cast_round_time(self):
        round_time = False
        if time.time() < self.cast_rt_end:
            round_time = True
        return round_time

    def get_cast_round_time(self):
            return int(self.cast_rt_end - time.time())

    def set_cast_round_time(self, seconds):
        self.cast_rt_start = time.time()
        self.cast_rt_end = self.cast_rt_start + seconds
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
        if self.dominance == 'right':
            return self.right_hand_inv
        if self.dominance == 'left':
            return self.left_hand_inv
        
    def get_non_dominant_hand_inv(self):
        if self.dominance == 'right':
            return self.left_hand_inv
        if self.dominance == 'left':
            return self.right_hand_inv
            
    def set_dominant_hand_inv(self, item):
        if self.dominance == 'right':
            self.right_hand_inv = item
        if self.dominance == 'left':
            self.left_hand_inv = item
            
    def set_non_dominant_hand_inv(self, item):
        if self.dominance == 'right':
            self.left_hand_inv = item
        if self.dominance == 'left':
            self.right_hand_inv = item

    def get_weapon_classification(self):
        if self.get_dominant_hand_inv():
            if self.get_dominant_hand_inv().category == 'weapon':
                return self.get_dominant_hand_inv().classification
        return "None"        
            
    @property
    def armor(self):
        return self._armor
    @armor.setter
    def armor(self, armor):
        self._armor = armor

    def get_armor_classification(self):
        if self.armor['torso']:
            return self.armor['torso'].classification
        return "None"

    @property
    def in_shop(self):
        return self._in_shop
    @in_shop.setter
    def in_shop(self, in_shop):
        self._in_shop = in_shop

    @property
    def shop_item_selected(self):
        return self._shop_item_selected
    @shop_item_selected.setter
    def shop_item_selected(self, shop_item_selected):
        self._shop_item_selected = shop_item_selected
        
    def move(self, dx, dy):
        self.location_x += dx
        self.location_y += dy
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

    def join_room(self):
        return

    def leave_room(self):
        return

    def get_room(self):
        return world.tile_exists(x=self.location_x, 
                                 y=self.location_y, 
                                 area=self.area_name)

    def change_room(self, x, y, area):
        self.location_x = x
        self.location_y = y
        self.area_name = area
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
        
        return [f"Right Hand:  {right_hand_status}",
                f"Left Hand:   {left_hand_status}",
                f"Stance:      {self.stance.name}",
                f"Position:    {self.position.name}",
                f"Health:      {self.health}",
                f"Mana:        {self.mana}"]








