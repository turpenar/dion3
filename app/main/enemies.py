
"""
This module contains enemy classes. Each enemy will operate on its own thread.

TODO:  Add ability to drop weapons and armor
"""

import time as time
import textwrap as textwrap
import random as random
import math as math
import eventlet

from app.main import mixins, actions, combat, objects, world, config, items


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

        self._right_hand_inv = self._enemy_data['right_hand']
        self._left_hand_inv = self._enemy_data['left_hand']
        
        experience_level = math.floor(experience_points_base * math.pow(self.level, experience_growth))
        experience_next_level = math.floor(experience_points_base * math.pow(self.level + 1, experience_growth))
        enemies_at_level = math.floor(enemy_level_base * math.pow(self.level,enemy_growth))
        
        self.experience = int((experience_next_level - experience_level) / enemies_at_level * random.uniform(0.9,1.1))

        self.enemy_result =  {"action_success": True,
                                "action_error": None,
                                "room_change": {
                                    "room_change_flag":  False,
                                    "leave_room_text": None,
                                    "old_room":  None,
                                    "new_room":  None,
                                    "enter_room_text":  None
                                },
                                "display_room":  {
                                    "display_room_flag":  False,
                                    "display_room_text":  None,
                                },
                                "character_output":  {
                                    "character_output_flag":  False,
                                    "character_output_text":  None
                                },
                                "room_output":  {
                                    "room_output_flag":  False,
                                    "room_output_text":  None
                                },
                                "area_output":  {
                                    "area_output_flag":  False,
                                    "area_output_text":  None
                                },
                                "status_output":  None
        }
        self.enemy_result_default = self.enemy_result.copy()   


    def update_room(self, old_room_number):
        self.enemy_result['room_change']['room_change_flag'] = True
        self.enemy_result['room_change']['leave_room_text'] = "{} left.".format(self.name)
        self.enemy_result['room_change']['old_room'] = old_room_number
        self.enemy_result['room_change']['new_room'] = self.room.room_number
        self.enemy_result['room_change']['enter_room_text'] = "{} arrived.".format(self.name)
        return

    def update_character_output(self, character_output_text):
        self.enemy_result['character_output']['character_output_flag'] = True
        self.enemy_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.enemy_result['display_room']['display_room_flag'] = True
        self.enemy_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text):
        self.enemy_result['room_output']['room_output_flag'] = True
        self.enemy_result['room_output']['room_number'] = self.room.room_number
        self.enemy_result['room_output']['room_output_text'] = room_output_text
        return
        
    def update_area_output(self, area_output_text):
        self.enemy_result['area_output']['area_output_flag'] = True
        self.enemy_result['area_output']['area_output_text'] = area_output_text
        return
    
    def update_status(self, status_text):
        self.enemy_result['status_output'] = status_text
        return

    def reset_result(self):
        self.enemy_result = self.enemy_result_default.copy()
        return 
    
    def move(self, dx, dy):
        self.room.remove_enemy(self)
        self.location_x += dx
        self.location_y += dy
        self.room = world.world_map.tile_exists(x=self.location_x, y=self.location_y, area=self.area)
        self.room.add_enemy(self)
        return

    def move_north(self, **kwargs):
        self.move(dx=0, dy=-1)
        return

    def move_south(self, **kwargs):
        self.move(dx=0, dy=1)
        return

    def move_east(self, **kwargs):
        self.move(dx=1, dy=0)
        return

    def move_west(self, **kwargs):
        self.move(dx=-1, dy=0)
        return

    def adjacent_moves(self):
        moves = []
        if world.world_map.tile_exists(x=self.location_x, y=self.location_y - 1, area=self.area):
            moves.append('north')
        if world.world_map.tile_exists(x=self.location_x, y=self.location_y + 1, area=self.area):
            moves.append('south')
        if world.world_map.tile_exists(x=self.location_x + 1, y=self.location_y, area=self.area):
            moves.append('east')
        if world.world_map.tile_exists(x=self.location_x - 1, y=self.location_y, area=self.area):
            moves.append('west')
        return moves
        
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
        non_moving_positions = [x for x in positions if x != 'standing']
        if set(self.position) & set(non_moving_positions):
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
    def text_entrance(self):
            return self._text_entrance
            
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
        actions.do_enemy_action(action_input='spawn', enemy=self)
        while self.is_alive():
                available_movement_actions = self.adjacent_moves()
                action = random.choice(available_movement_actions)
                actions.do_enemy_action(action_input=action, enemy=self)
                time.sleep(seconds=self.round_time_move)
        return

    def view_description(self):
        self.update_character_output(character_output_text=self.description)
        return self.enemy_result





