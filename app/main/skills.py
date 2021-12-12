

"""

"""


from app.main import spells, config


profession_skillpoint_bonus_file = config.PROFESSION_SKILLPOINT_BONUS_FILE
base_training_points = config.BASE_TRAINING_POINTS
skills_max_factors = config.SKILLS_MAX_FACTORS



def update_skills(result, character_file):
    character_file.char.physical_training_points = result['physical_training_points_var']
    character_file.char.mental_training_points = result['mental_training_points_var']
    for skill in character_file.char.skills:
        character_file.char.skills[skill] = int(result[skill])
        if character_file.char.skills[skill] > 40:
            character_file.char.skills_bonus[skill] = 140 + character_file.char.skills[skill] - 40
        elif character_file.char.skills[skill] > 30:
            character_file.char.skills_bonus[skill] = 120 + (character_file.char.skills[skill] - 30) * 2
        elif character_file.char.skills[skill] > 20:
            character_file.char.skills_bonus[skill] = 90 + (character_file.char.skills[skill] - 20) * 3
        elif character_file.char.skills[skill] > 10:
            character_file.char.skills_bonus[skill] = 50 + (character_file.char.skills[skill] - 10) * 4
        else:
            character_file.char.skills_bonus[skill] = character_file.char.skills[skill] * 5
        if skill == "spell_research":
            all_base_spells = spells.get_spells_skill_level(spell_base=character_file.char.profession.name, skill_level=int(result[skill]))
            spells_forget = character_file.char.check_spells_forget(spell_base=character_file.char.profession.name, spell_numbers=all_base_spells)
            spells_learned = character_file.char.check_spells_learned(spell_base=character_file.char.profession.name, spell_numbers=all_base_spells)
            character_file.char.learn_spells(spell_base=character_file.char.profession.name, spell_numbers=all_base_spells)
            if spells_forget:
                spell_message = f""""\
You unlearned the following spells:
{spells_forget}\
                """
            elif spells_learned:
                spell_message = f"""\
You learned new spells! Type SPELLS to access a list of all spells you know.
{spells_learned}\
                """
            else:
                spell_message = """"""

        if skill == "magic_harnessing":
            character_file.char.mana = int(character_file.char.mana_base + character_file.char.skills_bonus['magic_harnessing'])
    
    return spell_message


def level_up_skill_points(character):
    stat_value = {}
    for stat in character.stats:
        stat_value[stat] = int(round(float(character.stats[stat]))) * int(profession_skillpoint_bonus_file.loc[character.profession.name, stat])

    added_physical_points = base_training_points + ((stat_value['strength']
                                                    + stat_value['constitution']
                                                    + stat_value['dexterity']
                                                    + stat_value['agility']) / 40)
    added_mental_points = base_training_points + ((stat_value['intellect']
                                                    + stat_value['wisdom']
                                                    + stat_value['logic']
                                                    + stat_value['spirit']) / 40)
    character.physical_training_points = character.physical_training_points + added_physical_points
    character.mental_training_points = character.mental_training_points + added_mental_points
    for skill in character.skills:
        character.skills_max[skill] = (character.level + 1) * skills_max_factors.loc[skill, character.profession.name]
    return