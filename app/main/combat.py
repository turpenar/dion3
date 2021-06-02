
"""


"""

import random as random

from app.main import items, config

weapon_damage_factors = config.WEAPON_DAMAGE_FACTORS
weapon_attack_factors = config.WEAPON_ATTACK_FACTORS
experience_adjustment_factors = config.EXPERIENCE_ADJUSTMENT_FACTORS
position_factors = config.POSITION_FACTORS
stance_factors = config.STANCE_FACTORS

    
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

def calculate_attack_factor(weapon, armor):
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

def end_roll(attack, defense, attack_factor, random):
    return int((attack - defense + attack_factor + random))

def get_damage(end_roll, weapon, armor):
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

def get_exerience_modifier(self_level, target_level):
    level_variance = int(target_level - self_level)
    return experience_adjustment_factors.loc[level_variance, 'Adjustment_Factor']

def melee_attack_enemy(self, target):
    attack_strength = calculate_attack_strength(self, self.get_dominant_hand_inv())
    defense_strength = calculate_defense_strength(character=target, weapon=target.weapon)
    attack_factor = calculate_attack_factor(self.get_dominant_hand_inv(), target.armor)
    att_random = random.randint(0,100)
    att_end_roll = end_roll(attack=attack_strength, defense=defense_strength, attack_factor=attack_factor, random=att_random)
    round_time = self.set_round_time(3)
    
    result = None
    if att_end_roll <= 100:
        result = """\
{} evades the attack.
Round time:  {} seconds
            """.format(target.name, round_time)
    else:
        att_damage = get_damage(att_end_roll, self.get_dominant_hand_inv(), target.armor)
        target.health = target.health - att_damage
        if target.is_killed():
            death_text = target.text_death
            target.replace_with_corpse()
            self.experience += int(target.experience * get_exerience_modifier(self.level, target.level))
        else:
            death_text = ""
        result = """\
{} damages {} by {}.
Round time:  {} seconds
{}\
            """.format(self.name, target.name, att_damage, round_time, death_text)

    events.game_event("""\
{} attacks {}!
STR {} - DEF {} + AF {} + D100 ROLL {} = {}
{}\
    """.format(self.name, target.name, attack_strength, defense_strength, attack_factor, att_random, att_end_roll, result))
    self.check_level_up()
    return target

def melee_attack_character(self, character):
    attack_strength = calculate_attack_strength(self, self.weapon)
    defense_strength = calculate_defense_strength(character=character, weapon=character.get_dominant_hand_inv())
    attack_factor = calculate_attack_factor(self.weapon, character.armor)
    att_random = random.randint(0,100)
    att_end_roll = end_roll(attack=attack_strength,defense=defense_strength, attack_factor=attack_factor, random=att_random)

    result = None
    death_text = None
    if att_end_roll <= 100:
        result = """\
{} evades the attack.\
            """.format(character.name)
    else:
        att_damage = get_damage(att_end_roll, self.weapon, character.armor)
        character.health = character.health - att_damage
        death_text = character.is_killed()
        result = """\
{} damages {} by {}.
{}\
            """.format(self.name, character.name, att_damage, death_text)

    events.game_event("""\
{} attacks {}!
STR {} - DEF {} + AF {} + D100 ROLL {} = {}
{}
\
    """.format(self.name, character.name, attack_strength, defense_strength, attack_factor, att_random, att_end_roll, result))

    return character




