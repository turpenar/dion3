
"""


"""

import random as random
import math as math
import abc as abc

from app import db
from app.main import items, config
from app.main.models import Room

weapon_damage_factors = config.WEAPON_DAMAGE_FACTORS
weapon_attack_factors = config.WEAPON_ATTACK_FACTORS
experience_adjustment_factors = config.EXPERIENCE_ADJUSTMENT_FACTORS
position_factors = config.POSITION_FACTORS
stance_factors = config.STANCE_FACTORS


def do_combat_action(aggressor, combat_action, character_file=None, enemy_file=None, room_file=None):
    if not enemy_file:
        combat_result = {"action_success": False,
                         "action_error":  "No target loaded."
        }
        return combat_result
    return CombatAction.do_combat_action(aggressor=aggressor, combat_action=combat_action, character_file=character_file, enemy_file=enemy_file, room_file=room_file)
    

    
def calculate_position_factor_for_attack(aggressor):
    position_factor_for_attack = float(position_factors.loc[aggressor.position.name, 'attack_factor'])
    return position_factor_for_attack

def calculate_position_factor_for_defense(defender):
    position_factor_for_defense = float(position_factors.loc[defender.position.name, 'defense_factor'])
    return position_factor_for_defense

def calculate_stance_factor_for_attack(aggressor):
    stance = aggressor.stance
    stance_factor_for_attack = float(stance_factors.loc[stance.name, 'attack_factor'])
    return stance_factor_for_attack

def calculate_stance_factor_for_defense(defender):
    stance = defender.stance
    stance_factor_for_defense = float(stance_factors.loc[stance.name, 'defense_factor'])
    return stance_factor_for_defense
    
def calculate_attack_strength(aggressor):
    attack_strength = aggressor.calculate_attack_strength()
    position_factor = calculate_position_factor_for_attack(aggressor=aggressor)
    stance_factor = calculate_stance_factor_for_attack(aggressor=aggressor)
    attack_strength = int(attack_strength * position_factor * stance_factor)
    return attack_strength

def calculate_cast_strength(character):
    attack_strength = character.cast_strength_base
    return attack_strength

def calculate_defense_strength(defender):
    defense_strength = defender.calculate_defense_strength()
    position_factor = calculate_position_factor_for_defense(defender=defender)
    stance_factor = calculate_stance_factor_for_defense(defender=defender)
    defense_strength = int(defense_strength * position_factor * stance_factor)
    return defense_strength

def calculate_attack_factor_weapon(aggressor, defender):
    weapon_classification = aggressor.get_weapon_classification()
    armor_classification = defender.get_armor_classification()
    attack_factor = weapon_attack_factors.loc[weapon_classification, armor_classification]
    return int(attack_factor)

def calculate_attack_factor_spell(spell, defender):
    armor_classification = defender.get_armor_classification()
    attack_factor = weapon_attack_factors.loc[str(spell.spell_number), armor_classification]
    return int(attack_factor)

def end_roll(attack, defense, attack_factor, random):
    return int((attack - defense + attack_factor + random))

def get_damage_weapon(end_roll, aggressor, defender):
    armor_classification = defender.get_armor_classification()
    weapon_classification = aggressor.get_weapon_classification()
    damage_factor = weapon_damage_factors.loc[weapon_classification, armor_classification]
    return int(math.ceil((end_roll - 100) * damage_factor))

def get_damage_spell(end_roll, spell, armor):
    try:
        armor_classification = armor['torso'].classification
    except:
        armor_classification = "None"
    damage_factor = weapon_damage_factors.loc[str(spell.spell_number), armor_classification]
    return int(math.ceil((end_roll - 100) * damage_factor))

def get_exerience_modifier(character_level, target_level):
    level_variance = int(target_level - character_level)
    return experience_adjustment_factors.loc[level_variance, 'Adjustment_Factor']


class CombatAction:
    def __init__(self, character_file, enemy_file, room_file):
        self.character_file = character_file
        self.enemy_file = enemy_file
        self.room_file = room_file

        self.combat_result = {
                    "action_success": True,
                    "action_error": None,
                    "room_change": {
                        "room_change_flag":  False,
                        "leave_room_text": None,
                        "old_room":  None,
                        "new_room":  None,
                        "enter_room_text":  None
                    },
                    "area_change":  {
                        "area_change_flag":  False,
                        "old_area": None,
                        "new_area": None
                    },
                    "display_room":  {
                        "display_room_flag":  False,
                        "display_room_text": None
                    },
                    "character_output":  {
                        "character_output_flag":  False,
                        "character_output_text":  None
                    },
                    "room_output":  {
                        "room_output_flag":  False,
                        "room_output_text":  None,
                        "room_output_number":  None
                    },
                    "area_output":  {
                        "area_output_flag":  False,
                        "area_output_text":  None
                    },
                    "spawn_generator":  {
                        "spawn_generator_flag":  False,
                        "spawn_generator_thread":  None
                    },
                    "status_output": {
                        "status_output_flag": False,
                        "status_output_text": None
                    }
                    }

    _do_character_combat_actions = {}
    _do_enemy_combat_actions = {}

    @classmethod
    def register_character_attack_subclass(cls, combat_action):
        """Catalogues character combat actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls._do_character_combat_actions[combat_action] = subclass
            return subclass
        return decorator

    @classmethod
    def register_enemy_attack_subclass(cls, combat_action):
        """Catalogues enemy combat actions in a dictionary for reference purposes"""
        def decorator(subclass):
            cls._do_enemy_combat_actions[combat_action] = subclass
            return subclass
        return decorator

    @classmethod
    def do_combat_action(cls, aggressor, combat_action, character_file, enemy_file, room_file, **kwargs) -> dict:
        """Method used to initiate a combat action"""
        if combat_action not in cls._do_character_combat_actions or combat_action not in cls._do_enemy_combat_actions:
            cls.combat_result = {"action_success":  False,
                             "action_error":  "I am sorry, I did not understand."
            }
            return cls.combat_result
        if aggressor == 'character':
            return cls._do_character_combat_actions[combat_action](character_file=character_file, enemy_file=enemy_file, room_file=room_file, **kwargs)
        if aggressor == 'enemy':
            return cls._do_enemy_combat_actions[combat_action](enemy_file=enemy_file, character_file=character_file, room_file=room_file, **kwargs)

    def update_room(self, character, old_room_number):
        self.combat_result['room_change']['room_change_flag'] = True
        self.combat_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
        self.combat_result['room_change']['old_room'] = old_room_number
        self.combat_result['room_change']['new_room'] = character.get_room().room.room_number
        self.combat_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
        self.combat_result['display_room_flag'] = True
        return

    def update_area(self, character, old_area):
        self.combat_result['area_change']['area_change_flag'] = True
        self.combat_result['area_change']['old_area'] = old_area
        self.combat_result['area_change']['new_area'] = character.area_name
        return

    def update_character_output(self, character_output_text):
        self.combat_result['character_output']['character_output_flag'] = True
        self.combat_result['character_output']['character_output_text'] = character_output_text
        return

    def update_display_room(self, display_room_text):
        self.combat_result['display_room']['display_room_flag'] = True
        self.combat_result['display_room']['display_room_text'] = display_room_text
        return
        
    def update_room_output(self, room_output_text, room_output_number=None):
        self.combat_result['room_output']['room_output_flag'] = True
        self.combat_result['room_output']['room_output_text'] = room_output_text
        self.combat_result['room_output']['room_output_number'] = room_output_number
        return
        
    def update_area_output(self, area_output_text):
        self.combat_result['area_output']['area_output_flag'] = True
        self.combat_result['area_output']['area_output_text'] = area_output_text
        return

    def update_status(self, status_text):
        self.combat_result['status_output']['status_output_flag'] = True
        self.combat_result['status_output']['status_output_text'] = status_text
        return

    @abc.abstractmethod
    def attack():
        pass


@CombatAction.register_character_attack_subclass('melee')
class CombatMeleeActionCharacter(CombatAction):
    def __init__(
        self,
        character_file: object,
        enemy_file: object,
        room_file: object
    ):
        CombatAction.__init__(
            self,
            character_file = character_file,
            enemy_file = enemy_file,
            room_file = room_file
        )

        self.character_file = character_file
        self.enemy_file = enemy_file
        self.room_file = room_file

    def attack(self) -> dict:
        attack_strength = calculate_attack_strength(aggressor=self.character_file.char)
        defense_strength = calculate_defense_strength(defender=self.enemy_file.enemy)
        attack_factor = calculate_attack_factor_weapon(aggressor=self.character_file.char, defender=self.enemy_file.enemy)
        att_random = random.randint(0,100)
        att_end_roll = end_roll(attack=attack_strength, defense=defense_strength, attack_factor=attack_factor, random=att_random)
        round_time = self.character_file.char.set_round_time(self.character_file.char.get_round_time_base())

        try:
            weapon_name = self.character_file.char.get_dominant_hand_inv().name
        except:
            weapon_name = "a closed fist"

        if att_end_roll <= 100:
            result_character = f"""\
{self.enemy_file.enemy.name.capitalize()} evades the attack.
Round time:  {round_time} seconds\
                """
            result_room = f"""\
{self.character_file.char.first_name} swings {weapon_name} at {self.enemy_file.enemy.name} and misses.\
                """
        else:
            att_damage = get_damage_weapon(att_end_roll, aggressor=self.character_file.char, defender=self.enemy_file.enemy)
            self.enemy_file.health = self.enemy_file.health - att_damage
            if self.enemy_file.enemy.is_killed(self.enemy_file):
                death_text = self.enemy_file.enemy.text_death
                self.enemy_file.enemy.replace_with_corpse(self.enemy_file)
                self.character_file.char.experience += int(self.enemy_file.enemy.experience * get_exerience_modifier(self.character_file.char.level, self.enemy_file.enemy.level))
            else:
                death_text = ""
            result_character = f"""\
You damage {self.enemy_file.enemy.name} by {att_damage}.
Round time:  {round_time} seconds
{death_text}\
                """
            result_room = f"""\
    {self.character_file.char.name} strikes {self.enemy_file.enemy.name} with {weapon_name}!
    {death_text}\
                """

        self.update_character_output(character_output_text=f"""\
You swing {weapon_name} at {self.enemy_file.enemy.name}!
STR {attack_strength} - DEF {defense_strength} + AF {attack_factor} + D100 ROLL {att_random} = {att_end_roll}
{result_character}\
    """)
        self.update_room_output(room_output_text=result_room, room_output_number=self.room_file.room.room_number)
        print(f"Character is in room {self.room_file.room.room_number}.")
        return self.combat_result


@CombatAction.register_enemy_attack_subclass('melee')
class CombatMeleeActionEnemy(CombatAction):
    def __init__(
        self,
        enemy_file: object,
        character_file: object,
        room_file: object
    ):
        CombatAction.__init__(
            self,
            enemy_file = enemy_file,
            character_file = character_file,
            room_file = room_file
        )

        self.enemy_file = enemy_file
        self.character_file = character_file
        self.room_file = room_file

    def attack(self) -> dict:
        attack_strength = calculate_attack_strength(aggressor=self.enemy_file.enemy)
        defense_strength = calculate_defense_strength(defender=self.character_file.char)
        attack_factor = calculate_attack_factor_weapon(aggressor=self.enemy_file.enemy, defender=self.character_file.char)
        att_random = random.randint(0,100)
        att_end_roll = end_roll(attack=attack_strength,defense=defense_strength, attack_factor=attack_factor, random=att_random)

        death_text = None
        if att_end_roll <= 100:
            result_character = f"""\
You evade the attack.\
                """
            result_room = f"""\
{self.character_file.char.first_name} evades the attack.\
            """
        else:
            att_damage = get_damage_weapon(att_end_roll, aggressor=self.enemy_file.enemy, defender=self.character_file.char)
            self.character_file.char.health = self.character_file.char.health - att_damage
            death_text = self.character_file.char.is_killed()
            result_character = f"""\
{self.enemy_file.enemy.name.capitalize()} damages you by {att_damage}.
{death_text}\
                """
            result_room = f"""\
{self.enemy_file.enemy.name.capitalize()} hits {self.character_file.char.first_name} with a {self.enemy_file.enemy.weapon}\
            """

        self.update_character_output(character_output_text=f"""\
{self.enemy_file.enemy.name.capitalize()} {self.enemy_file.enemy.text_attack} you!
STR {attack_strength} - DEF {defense_strength} + AF {attack_factor} + D100 ROLL {att_random} = {att_end_roll}
{result_character}\
        """)
        self.update_room_output(room_output_text=f"""\
{self.enemy_file.enemy.name.capitalize()} {self.enemy_file.enemy.text_attack} at {self.character_file.char.first_name}
{result_room}\
        """,
                                room_output_number=self.room_file.room.room_number)
        print(self.room_file.room.room_number)
        return self.combat_result


@CombatAction.register_character_attack_subclass('bolt')
class CombatBoltActionCharacter(CombatAction):
    def __init__(
        self,
        character_file: object,
        enemy_file: object,
        room_file: object
    ):
        CombatAction.__init__(
            self,
            character_file = character_file,
            enemy_file = enemy_file,
            room_file = room_file
        )

        self.character_file = character_file
        self.enemy_file = enemy_file
        self.room_file = room_file

    def attach(self):
        attack_strength = calculate_cast_strength(character=self.character_file.char)
        defense_strength = calculate_defense_strength(character=self.enemy_file.enemy, weapon=self.enemy_file.enemy.weapon)
        attack_factor = calculate_attack_factor_spell(spell=self.character_file.char.active_spell, defender=self.enemy_file.enemy)
        att_random = random.randint(0,100)
        att_end_roll = end_roll(attack=attack_strength, defense=defense_strength, attack_factor=attack_factor, random=att_random)
        round_time = self.character_file.char.set_round_time(self.character_file.char.active_spell.cast_round_time)

        if att_end_roll <= 100:
            result_character = f"""\
{self.enemy_file.enemy.name.capitalize()} evades the attack.
Round time:  {round_time} seconds\
                """
            result_room = f"""\
{self.character_file.char.first_name} {self.character_file.char.active_spell.text_cast_room} at {self.enemy_file.enemy.name} and misses.\
                """
        else:
            att_damage = get_damage_spell(att_end_roll, self.character_file.char.active_spell, self.enemy_file.enemy.armor)
            self.enemy_file.health = self.enemy_file.health - att_damage
            if self.enemy_file.enemy.is_killed(self.enemy_file):
                death_text = self.enemy_file.enemy.text_death
                self.enemy_file.enemy.replace_with_corpse(self.enemy_file)
                self.character_file.char.experience += int(self.enemy_file.enemy.experience * get_exerience_modifier(self.character_file.char.level, self.enemy_file.enemy.level))
            else:
                death_text = ""
            result_character = f"""\
You damage {self.enemy_file.enemy.name} by {att_damage}.
Round time:  {round_time} seconds
{death_text}\
                """
            result_room = f"""\
{self.character_file.char.name} {self.character_file.char.active_spell.text_cast_room} at {self.enemy_file.enemy.name}!
{death_text}\
                """

        self.update_character_output(character_output_text=f"""\
You {self.character_file.char.active_spell.text_cast_character} at {self.enemy_file.enemy.name}!
STR {attack_strength} - DEF {defense_strength} + AF {attack_factor} + D100 ROLL {att_random} = {att_end_roll}
{result_character}\
    """)
        self.update_room_output(room_output_text=result_room, room_output_number=self.room_file.room.room_number)
        return self.combat_result

