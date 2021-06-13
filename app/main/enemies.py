
"""
This module contains enemy classes. Each enemy will operate on its own thread.

TODO:  Add ability to drop weapons and armor
"""

import time as time
import textwrap as textwrap
import random as random
import math as math

from app.main import mixins, combat, objects, world, config


enemy_level_base = config.enemy_level_base
enemy_growth = config.enemy_growth
experience_points_base = config.experience_points_base
experience_growth = config.experience_growth
positions = config.positions
stances = config.stances


class Enemy(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, enemy_name: str, target: object, room: object, location_x: int, location_y: int, area: str, **kwargs):
        super(Enemy, self).__init__()

        self._enemy_data = self.get_enemy_by_name(enemy_name)

        self._name = self._enemy_data['name']
        self._description = self._enemy_data['description']
        self._handle = self._enemy_data['handle']
        self._adjectives = self._enemy_data['adjectives']
        self._category = self._enemy_data['category']
        self._level = self._enemy_data['level']
        self._health = self._enemy_data['health']
        self._health_max = self._enemy_data['health_max']
        self._attack_strength_base = self._enemy_data['attack_strength_base']
        self._defense_strength_base = self._enemy_data['defense_strength_base']
        self._position = self._enemy_data['position']
        self._stance = self._enemy_data['stance']
        
        self._text_entrance = self._enemy_data['text']['entrance_text']
        self._text_move_in = self._enemy_data['text']['move_in_text']
        self._text_move_out = self._enemy_data['text']['move_out_text']
        self._text_engage = self._enemy_data['text']['engage_text']
        self._text_death = self._enemy_data['text']['death_text']
        
        self._round_time_engage = self._enemy_data['round_time']['engage']
        self._round_time_attack = self._enemy_data['round_time']['attack']
        self._round_time_move = self._enemy_data['round_time']['move']
        
        self._corpse = self._enemy_data['corpse']
    
        self._armor = {}
        
        for category in self._enemy_data['armor']:
            for item in self._enemy_data['armor'][category]:
                self._armor[category] = items.create_item('armor', item_name=item)
                
        self._weapon = self._enemy_data['weapon']

        self.spawn_location = self._enemy_data['spawn_location']
        self.location_x = location_x
        self.location_y = location_y
        self.area = area
        self.room = room

        self.target = target

        if self.room == target.room:
            for line in textwrap.wrap(self._enemy_data['entrance_text'], 80):
                events.game_event(line)

        self._right_hand_inv = self._enemy_data['right_hand']
        self._left_hand_inv = self._enemy_data['left_hand']
        
        experience_level = math.floor(experience_points_base * math.pow(self.level, experience_growth))
        experience_next_level = math.floor(experience_points_base * math.pow(self.level + 1, experience_growth))
        enemies_at_level = math.floor(enemy_level_base * math.pow(self.level,enemy_growth))
        
        self.experience = int((experience_next_level - experience_level) / enemies_at_level * random.uniform(0.9,1.1))

    def move(self, dx, dy):
        self.room.remove_enemy(self)
        if self.room == self.target.room:
            events.game_event(self.text_move_out)
        self.location_x += dx
        self.location_y += dy
        self.room = world.tile_exists(x=self.location_x, y=self.location_y, area=self.area)
        self.room.add_enemy(self)
        if self.room == self.target.room:
            events.game_event(self.text_move_in)

    def move_north(self, **kwargs):
        self.move(dx=0, dy=-1)

    def move_south(self, **kwargs):
        self.move(dx=0, dy=1)

    def move_east(self, **kwargs):
        self.move(dx=1, dy=0)

    def move_west(self, **kwargs):
        self.move(dx=-1, dy=0)
        
    @property
    def name(self):
            return self._name
        
    @property
    def description(self):
            return self._description
        
    @property
    def handle(self):
            return self._handle
        
    @property
    def adjectives(self):
            return self._adjectives
        
    @property
    def category(self):
            return self._category
        
    @property
    def level(self):
            return self._level
        
    @property
    def health(self):
            return self._health
        
    @health.setter
    def health(self, health):
            self._health =  health
    
    @property    
    def health_max(self):
            return self._health_max
        
    @property
    def attack_strength_base(self):
            return self._attack_strength_base
        
    @property
    def defense_strength_base(self):
            return self._defense_strength_base
        
    @property
    def position(self):
            return self._position[0]
    @position.setter
    def position(self, position):
            self._position = [position]
            
    def check_position_to_move(self):
        non_moving_positions = [x for x in positions if x is not 'standing']
        if set(self.position) & set(non_moving_positions):
            events.game_event('''{} struggles to move.'''.format(self.name[0]))
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
    def armor(self):
            return self._armor
        
    @armor.setter
    def armor(self, armor):
            self._armor = armor
            
    @property
    def weapon(self):
            return self._weapon
        
    @weapon.setter
    def weapon(self, weapon):
            self._weapon = weapon
            
    @property
    def text_move_in(self):
            return self._text_move_in
        
    @property
    def text_move_out(self):
            return self._text_move_out
        
    @property
    def text_engage(self):
            return self._text_engage
            
    @property
    def text_death(self):
            return self._text_death
        
    @property
    def round_time_engage(self):
            return self._round_time_engage
        
    @property
    def round_time_attack(self):
            return self._round_time_attack
        
    @property
    def round_time_move(self):
            return self._round_time_move
        
    @property
    def corpse(self):
            return self._corpse
        
    @property
    def right_hand_inv(self):
            return self.right_hand_inv
        
    @right_hand_inv.setter
    def right_hand_inv(self, item):
            self._right_hand_inv = item
            
    @property
    def left_hand_inv(self):
            return self._left_hand_inv
            
    @left_hand_inv.setter
    def left_hand_inv(self, item):
            self._left_hand_inv = item

    def is_alive(self):
        return self.health > 0

    def is_killed(self):
        if self.health > 0:
            return False
        else:
            return True
        
    def replace_with_corpse(self):
            if self in self.room.enemies:
                self.room.remove_enemy(self)
                self.room.add_object(objects.Corpse(object_name=self.corpse, room=self.room))
                self.target = None
                self.room = None
            else:
                print("Game Error:  when replacing a dead enemy with a corpse, the enemy was not in mapped to the proper room")

    def run(self):
        if self.room == self.target.room:
            events.game_event(self.text_move_in)
        while self.health > 0:
            if self.health <= 0:
                break
            elif (self.room == self.target.room) and (self.target.health > 0):
                events.game_event(self.text_engage)
                time.sleep(self.round_time_engage)
                if (self.room == self.target.room) and (self.target.health > 0) and (self.is_alive):
                    combat.melee_attack_character(self, self.target)
                    time.sleep(self.round_time_attack)
            else:
                available_actions = self.room.adjacent_moves_enemy(area=self.area)
                action = random.choice(available_actions)
                action_method = getattr(self, action.method.__name__)
                action_method()
                time.sleep(self.round_time_move)
        return

    def view_description(self):
        return (self.description)





