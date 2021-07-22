
"""


"""

import random as random

from app import db
from app.main import items, config
from app.main.models import Room

weapon_damage_factors = config.WEAPON_DAMAGE_FACTORS
weapon_attack_factors = config.WEAPON_ATTACK_FACTORS
experience_adjustment_factors = config.EXPERIENCE_ADJUSTMENT_FACTORS
position_factors = config.POSITION_FACTORS
stance_factors = config.STANCE_FACTORS

combat_result = {
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
                "room_output_text":  None
            },
            "area_output":  {
                "area_output_flag":  False,
                "area_output_text":  None
            },
            "spawn_generator":  {
                "spawn_generator_flag":  False,
                "spawn_generator_thread":  None
            },
            "status_output":  None
            }

combat_result_default = combat_result.copy()

def update_room(character, old_room_number):
    global combat_result
    combat_result['room_change']['room_change_flag'] = True
    combat_result['room_change']['leave_room_text'] = "{} left.".format(character.first_name)
    combat_result['room_change']['old_room'] = old_room_number
    combat_result['room_change']['new_room'] = character.get_room().room.room_number
    combat_result['room_change']['enter_room_text'] = "{} arrived.".format(character.first_name)
    combat_result['display_room_flag'] = True
    return

def update_area(character, old_area):
    global combat_result
    combat_result['area_change']['area_change_flag'] = True
    combat_result['area_change']['old_area'] = old_area
    combat_result['area_change']['new_area'] = character.area_name
    return

def update_character_output(character_output_text):
    global combat_result
    combat_result['character_output']['character_output_flag'] = True
    combat_result['character_output']['character_output_text'] = character_output_text
    return

def update_display_room(display_room_text):
    global combat_result
    combat_result['display_room']['display_room_flag'] = True
    combat_result['display_room']['display_room_text'] = display_room_text
    return
    
def update_room_output(room_output_text, room_output_number=None):
    global combat_result
    combat_result['room_output']['room_output_flag'] = True
    combat_result['room_output']['room_output_text'] = room_output_text
    combat_result['room_output']['room_output_number'] = room_output_number
    return
    
def update_area_output(area_output_text):
    global combat_result
    combat_result['area_output']['area_output_flag'] = True
    combat_result['area_output']['area_output_text'] = area_output_text
    return

def update_status(status_text):
    global combat_result
    combat_result['status_output'] = status_text
    return

def reset_result():
    global combat_result
    global combat_result_default
    combat_result = combat_result_default.copy()
    return

    
def calculate_position_factor_for_attack(character):
    position = character.position
    position_factor_for_attack = float(position_factors.loc[position, 'attack_factor'])
    return position_factor_for_attack

def calculate_position_factor_for_defense(character):
    position = character.position
    position_factor_for_defense = float(position_factors.loc[position, 'defense_factor'])
    return position_factor_for_defense

def calculate_stance_factor_for_attack(character):
    stance = character.stance
    stance_factor_for_attack = float(stance_factors.loc[stance, 'attack_factor'])
    return stance_factor_for_attack

def calculate_stance_factor_for_defense(character):
    stance = character.stance
    stance_factor_for_defense = float(stance_factors.loc[stance, 'defense_factor'])
    return stance_factor_for_defense
    
def calculate_attack_strength(character, weapon):
    attack_strength = character.attack_strength_base
    if character.category == "player":
        if weapon:
            if weapon.category == 'weapon':
                attack_strength += character.skills_bonus[weapon.sub_category] 
    attack_strength = int(attack_strength * calculate_position_factor_for_attack(character) * calculate_stance_factor_for_attack(character))
    return attack_strength

def calculate_cast_strength(character):
    attack_strength = character.cast_strength_base
    attack_strength += int(character.skills_bonus['magic_harnessing'])
    return attack_strength
    
def calculate_defense_strength_evade(character):
    defense_strength_evade = int(character.defense_strength_evade_base + character.skills['dodging'])
    return defense_strength_evade
    
def calculate_defense_strength_block(character):
    defense_strength_block = int(character.defense_strength_block_base) + character.skills['shield']
    return defense_strength_block
        
def calculate_defense_strength_parry(character, weapon):
    defense_strength_parry = int(character.defense_strength_parry_base + character.skills['dodging'])      
    if weapon:
        if weapon.category == 'weapon':
            weapon_ranks = character.skills[character.get_dominant_hand_inv().sub_category]
            defense_strength_parry += int(weapon_ranks)
    return defense_strength_parry

def calculate_defense_strength(character, weapon):
    defense_strength = 0
    if character.category == "player":
        defense_strength_evade = calculate_defense_strength_evade(character=character)
        defense_strength_block = calculate_defense_strength_block(character=character)
        defense_strength_parry = calculate_defense_strength_parry(character=character, weapon=weapon)  
        defense_strength =  defense_strength_evade + defense_strength_block + defense_strength_parry
    else:
        defense_strength = character.defense_strength_base
    defense_strength = int(defense_strength * calculate_position_factor_for_defense(character) * calculate_stance_factor_for_defense(character))
    return defense_strength

def calculate_attack_factor_weapon(weapon, armor):
    try:
        armor_classification = armor['torso'].classification
    except:
        armor_classification = "None"
    try:
        if weapon.category == 'weapon':
            weapon_classification = weapon.classification
        else:
            weapon_classification = "None"
    except:
        weapon_classification = "None"
    attack_factor = weapon_attack_factors.loc[weapon_classification, armor_classification]
    return int(attack_factor)

def calculate_attack_factor_spell(spell, armor):
    try:
        armor_classification = armor['torso'].classification
    except:
        armor_classification = "None"
    attack_factor = weapon_attack_factors.loc[str(spell.spell_number), armor_classification]
    return int(attack_factor)

def end_roll(attack, defense, attack_factor, random):
    return int((attack - defense + attack_factor + random))

def get_damage_weapon(end_roll, weapon, armor):
    try:
        armor_classification = armor['torso'].classification
    except:
        armor_classification = "None"
    try:
        if weapon.category == 'weapon':
            weapon_classification = weapon.classification
        else:
            weapon_classification = "None"
    except:
        weapon_classification = "None"
        
    damage_factor = weapon_damage_factors.loc[weapon_classification, armor_classification]
    return int(round((end_roll - 100) * damage_factor))

def get_damage_spell(end_roll, spell, armor):
    try:
        armor_classification = armor['torso'].classification
    except:
        armor_classification = "None"
    damage_factor = weapon_damage_factors.loc[str(spell.spell_number), armor_classification]
    return int(round((end_roll - 100) * damage_factor))

def get_exerience_modifier(character_level, target_level):
    level_variance = int(target_level - character_level)
    return experience_adjustment_factors.loc[level_variance, 'Adjustment_Factor']

def melee_attack_enemy(character_file, target_file):
    global combat_result
    reset_result()
    attack_strength = calculate_attack_strength(character_file.char, character_file.char.get_dominant_hand_inv())
    defense_strength = calculate_defense_strength(character=target_file.enemy, weapon=target_file.enemy.weapon)
    attack_factor = calculate_attack_factor_weapon(character_file.char.get_dominant_hand_inv(), target_file.enemy.armor)
    att_random = random.randint(0,100)
    att_end_roll = end_roll(attack=attack_strength, defense=defense_strength, attack_factor=attack_factor, random=att_random)
    round_time = character_file.char.set_round_time()
    
    result = None
    if att_end_roll <= 100:
        result_character = f"""\
{target_file.enemy.name} evades the attack.
Round time:  {round_time} seconds\
            """
        result_room = f"""\
{character_file.char.first_name} swings {character_file.char.get_dominant_hand_inv().name} at {target_file.enemy.name} and misses.\
            """
    else:
        att_damage = get_damage_weapon(att_end_roll, character_file.char.get_dominant_hand_inv(), target_file.enemy.armor)
        target_file.health = target_file.health - att_damage
        if target_file.enemy.is_killed(target_file):
            death_text = target_file.enemy.text_death
            target_file.enemy.replace_with_corpse(target_file)
            character_file.char.experience += int(target_file.enemy.experience * get_exerience_modifier(character_file.char.level, target_file.enemy.level))
        else:
            death_text = ""
        result_character = f"""\
You damage {target_file.enemy.name} by {att_damage}.
Round time:  {round_time} seconds
{death_text}\
            """
        result_room = f"""\
{character_file.char.name} strikes {target_file.enemy.name} with {character_file.char.get_dominant_hand_inv().name}!
{death_text}\
            """

    update_character_output(character_output_text=f"""\
You swing {character_file.char.get_dominant_hand_inv().name} at {target_file.enemy.name}!
STR {attack_strength} - DEF {defense_strength} + AF {attack_factor} + D100 ROLL {att_random} = {att_end_roll}
{result_character}\
    """)
    update_room_output(room_output_text=result_room)
    return combat_result

def melee_attack_character(enemy_file, character_file, room_file):
    global combat_result
    reset_result()
    attack_strength = calculate_attack_strength(enemy_file.enemy, enemy_file.enemy.weapon)
    defense_strength = calculate_defense_strength(character=character_file.char, weapon=character_file.char.get_dominant_hand_inv())
    attack_factor = calculate_attack_factor_weapon(enemy_file.enemy.weapon, character_file.char.armor)
    att_random = random.randint(0,100)
    att_end_roll = end_roll(attack=attack_strength,defense=defense_strength, attack_factor=attack_factor, random=att_random)

    result = None
    death_text = None
    if att_end_roll <= 100:
        result_character = f"""\
You evade the attack.\
            """
        result_room = f"""\
{character_file.char.first_name} evades the attack.\
        """
    else:
        att_damage = get_damage_weapon(att_end_roll, enemy_file.enemy.weapon, character_file.char.armor)
        character_file.char.health = character_file.char.health - att_damage
        death_text = character_file.char.is_killed()
        result_character = f"""\
{enemy_file.enemy.name} damages you by {att_damage}.
{death_text}\
            """
        result_room = f"""\
{enemy_file.enemy.name} hits {character_file.char.first_name} with a {enemy_file.enemy.weapon}\
        """

    update_character_output(character_output_text=f"""\
{enemy_file.enemy.name} {enemy_file.enemy.text_attack} you!
STR {attack_strength} - DEF {defense_strength} + AF {attack_factor} + D100 ROLL {att_random} = {att_end_roll}
{result_character}\
    """)
    update_room_output(room_output_text=f"""\
{enemy_file.enemy.name.capitalize()} swing {enemy_file.enemy.weapon} at {character_file.char.first_name}
{result_room}\
    """,
                       room_output_number=room_file.room_number)

    return combat_result


def bolt_attack_enemy(target_file, character_file, room_file):
    global combat_result
    reset_result()
    attack_strength = calculate_cast_strength(character=character_file.char)
    defense_strength = calculate_defense_strength(character=target_file.enemy, weapon=target_file.enemy.weapon)
    attack_factor = calculate_attack_factor_spell(character_file.char.active_spell, target_file.enemy.armor)
    att_random = random.randint(0,100)
    att_end_roll = end_roll(attack=attack_strength, defense=defense_strength, attack_factor=attack_factor, random=att_random)
    round_time = character_file.char.set_round_time(character_file.char.active_spell.cast_round_time)
    
    result = None
    if att_end_roll <= 100:
        result_character = f"""\
{target_file.enemy.name} evades the attack.
Round time:  {round_time} seconds\
            """
        result_room = f"""\
{character_file.char.first_name} {character_file.char.active_spell.text_cast_room} at {target_file.enemy.name} and misses.\
            """
    else:
        att_damage = get_damage_spell(att_end_roll, character_file.char.active_spell, target_file.enemy.armor)
        target_file.health = target_file.health - att_damage
        if target_file.enemy.is_killed(target_file):
            death_text = target_file.enemy.text_death
            target_file.enemy.replace_with_corpse(target_file)
            character_file.char.experience += int(target_file.enemy.experience * get_exerience_modifier(character_file.char.level, target_file.enemy.level))
        else:
            death_text = ""
        result_character = f"""\
You damage {target_file.enemy.name} by {att_damage}.
Round time:  {round_time} seconds
{death_text}\
            """
        result_room = f"""\
{character_file.char.name} {character_file.char.active_spell.text_cast_room} at {target_file.enemy.name}!
{death_text}\
            """

    update_character_output(character_output_text=f"""\
You {character_file.char.active_spell.text_cast_character} at {target_file.enemy.name}!
STR {attack_strength} - DEF {defense_strength} + AF {attack_factor} + D100 ROLL {att_random} = {att_end_roll}
{result_character}\
    """)
    update_room_output(room_output_text=result_room)
    return combat_result





