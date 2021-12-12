
"""
This module contains enemy classes. Each enemy will operate on its own thread.

TODO:  Add ability to drop weapons and armor
"""

import os
import random as random
import math as math
import eventlet

from app import db
from app.main import mixins, actions, combat, objects, world, config, items
from app.main.models import Room, EnemySpawn


enemy_level_base = config.ENEMY_LEVEL_BASE
enemy_growth = config.ENEMY_GROWTH
experience_points_base = config.EXPERIENCE_POINTS_BASE
experience_growth = config.EXPERIENCE_GROWTH


class Enemy(mixins.ReprMixin, mixins.DataFileMixin):
    def __init__(self, enemy_name: str, target: object, location_x: int, location_y: int, area: str, **kwargs):
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
        self._position: config.Position = config.Position[self._enemy_data['position']]
        self._stance: config.Stance = config.Stance[self._enemy_data['stance']]
        
        self._text_entrance = self._enemy_data['text']['entrance_text']
        self._text_move_in = self._enemy_data['text']['move_in_text']
        self._text_move_out = self._enemy_data['text']['move_out_text']
        self._text_engage = self._enemy_data['text']['engage_text']
        self._text_attack = self._enemy_data['text']['attack_text']
        self._text_guard_kill_room = self._enemy_data['text']['guard_kill_text_room']
        self._text_guard_kill_character = self._enemy_data['text']['guard_kill_text_character']
        self._text_death = self._enemy_data['text']['death_text']
        self._text_leave = self._enemy_data['text']['leave_text']
        
        self._round_time_engage = self._enemy_data['round_time']['engage']
        self._round_time_attack = self._enemy_data['round_time']['attack']
        self._round_time_move = self._enemy_data['round_time']['move']
        
        self._corpse = self._enemy_data['corpse']
    
        self._armor = self._enemy_data['armor']
        
        for category in self._enemy_data['armor']:
            for item in self._enemy_data['armor'][category]:
                self._armor[category] = items.create_item('armor', item_name=item)
                
        if self._enemy_data['weapon'] == "None":
                self._weapon = None 
        else:       
                self._weapon = items.create_item(item_category='weapon', item_name=self._enemy_data['weapon'])

        self._skills_bonus = {}

        for skill in self._enemy_data['skills_bonus']:
                self._skills_bonus[skill] = self._enemy_data['skills_bonus'][skill]

        self.spawn_location = self._enemy_data['spawn_location']
        self.location_x = location_x
        self.location_y = location_y
        self.area = area
        self._enemy_id = None

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
                                "status_output": {
                                        "status_output_flag": False,
                                        "status_output_text": None
                                }
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
        self.enemy_result['status_output']['status_output_flag'] = True
        self.enemy_result['status_output']['status_output_text'] = status_text
        return

    def reset_result(self):
        self.enemy_result = self.enemy_result_default.copy()
        return 

    def get_room(self):
        return world.tile_exists(x=self.location_x, y=self.location_y, area=self.area)
    
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

    def move_east(self, **kwargs):
        self.move(dx=1, dy=0)
        return

    def move_west(self, **kwargs):
        self.move(dx=-1, dy=0)
        return

    def adjacent_moves(self):
        moves = []
        if world.tile_exists(x=self.location_x, y=self.location_y - 1, area=self.area):
            moves.append('north')
        if world.tile_exists(x=self.location_x, y=self.location_y + 1, area=self.area):
            moves.append('south')
        if world.tile_exists(x=self.location_x + 1, y=self.location_y, area=self.area):
            moves.append('east')
        if world.tile_exists(x=self.location_x - 1, y=self.location_y, area=self.area):
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

    def calculate_attack_strength(self):
        return self.attack_strength_base
        
    @property
    def defense_strength_base(self):
            return self._defense_strength_base

    def calculate_defense_strength(self):
        return self.defense_strength_base
        
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
    def armor(self):
            return self._armor
        
    @armor.setter
    def armor(self, armor):
            self._armor = armor

    def get_armor_classification(self):
        if self.armor['torso']:
            return self.armor['torso'].classification
        else:
            return "None"
            
    @property
    def weapon(self):
        return self._weapon
        
    @weapon.setter
    def weapon(self, weapon):
        self._weapon = weapon

    def get_weapon_classification(self):
        if self.weapon:
                return self.weapon.classification
        return "None"

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
    def text_attack(self):
            return self._text_attack

    @property
    def text_guard_kill_room(self):
            return self._text_guard_kill_room

    @property
    def text_guard_kill_character(self):
            return self._text_guard_kill_character
            
    @property
    def text_death(self):
            return self._text_death

    @property
    def text_leave(self):
            return self._text_leave
        
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
            return
            
    @property
    def left_hand_inv(self):
            return self._left_hand_inv
            
    @left_hand_inv.setter
    def left_hand_inv(self, item):
            self._left_hand_inv = item
            return

    @property
    def enemy_id(self):
            return self._enemy_id
    @enemy_id.setter
    def enemy_id(self, enemy_id):
            self._enemy_id = enemy_id
            return

    def is_alive(self, enemy_file):
        return enemy_file.health > 0

    def is_killed(self, enemy_file):
        if enemy_file.health > 0:
            return False
        else:
            return True
        
    def replace_with_corpse(self, enemy_file):
            room_file = db.session.query(Room).filter_by(x=enemy_file.enemy.location_x, y=enemy_file.enemy.location_y, area_name=enemy_file.enemy.area).first()
            if room_file:
                try:
                    room_file.enemies.remove(enemy_file)
                    print(f"enemy {enemy_file.id} has been removed from the room.")
                    room_file.room.add_object(objects.create_object(object_category="corpse", object_name=self.corpse, room=room_file))
                except:
                    print("Game Error:  when replacing a dead enemy with a corpse, the enemy was not in mapped to the proper room")
                return
            else:
                print("Room was not found when replacing corpse.")
                return
                

    def run(self, app, enemy_id):
        with app.app_context():
                enemy_file = db.session.query(EnemySpawn).filter_by(id=enemy_id).first()
                enemy_file.health = self._enemy_data['health']
                actions.do_enemy_action(action_input='spawn')
                db.session.commit()
                eventlet.sleep(seconds=enemy_file.enemy.round_time_move)
                db.session.commit()
                enemy_file = db.session.query(EnemySpawn).filter_by(id=enemy_id).first()
                print(f"Enemy {enemy_file.id} ready to decide what to do.")
                while True:
                        if enemy_file.health <= 0:
                                break 
                        if enemy_file.stop:
                                break
                        room_file = db.session.query(Room).filter_by(x=enemy_file.enemy.location_x, y=enemy_file.enemy.location_y, area_name=enemy_file.enemy.area).first()
                        if len(room_file.characters) > 0:
                                character_to_attack = False
                                for character_file in room_file.characters:
                                        if character_file.char.health > 0:
                                                character_to_attack = True
                                                print(f"Enemy {enemy_file.id} is attacking.")
                                                actions.do_enemy_action('attack', enemy_file=enemy_file, character_file=character_file, room_file=room_file)
                                                db.session.commit()
                                                eventlet.sleep(seconds=enemy_file.enemy.round_time_attack)
                                                db.session.commit()
                                                break
                                if character_to_attack == False:
                                        actions.do_enemy_action('guard', enemy_file=enemy_file, room_file=room_file)
                                        eventlet.sleep(seconds=enemy_file.enemy.round_time_move)
                        else:
                                print(f"Enemy {enemy_file.id} is moving.")
                                available_movement_actions = []
                                available_movement_actions = enemy_file.enemy.adjacent_moves()
                                action = random.choice(available_movement_actions)
                                room_file.enemies.remove(enemy_file)
                                actions.do_enemy_action(action_input=action, enemy_file=enemy_file)
                                room_file = db.session.query(Room).filter_by(x=enemy_file.enemy.location_x, y=enemy_file.enemy.location_y, area_name=enemy_file.enemy.area).first()
                                room_file.enemies.append(enemy_file)
                                db.session.commit()
                                eventlet.sleep(seconds=enemy_file.enemy.round_time_move)
                                db.session.commit()
                                enemy_file = db.session.query(EnemySpawn).filter_by(id=enemy_id).first()
                room_file = db.session.query(Room).filter_by(x=enemy_file.enemy.location_x, y=enemy_file.enemy.location_y, area_name=enemy_file.enemy.area).first()
                db.session.delete(enemy_file)
                db.session.commit()
                print(f"enemy {enemy_file.id} has been stopped.")
        return
        
    def view_description(self):
        self.update_character_output(character_output_text=self.description)
        return self.enemy_result


