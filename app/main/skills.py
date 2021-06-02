

"""

"""

import copy as copy

from app.main import player, config, mixins


profession_skillpoint_bonus_file = config.PROFESSION_SKILLPOINT_BONUS_FILE
base_training_points = config.base_training_points


def level_up_skill_points():

    stat_value = {}

    for stat in player.character.stats:
        stat_value[stat] = int(round(float(player.character.stats[stat]))) * int(profession_skillpoint_bonus_file.loc[player.character.profession, stat])

    added_physical_points = base_training_points + ((stat_value['strength']
                                                    + stat_value['constitution']
                                                    + stat_value['dexterity']
                                                    + stat_value['agility']) / 20)
    added_mental_points = base_training_points + ((stat_value['intellect']
                                                   + stat_value['wisdom']
                                                   + stat_value['logic']
                                                   + stat_value['spirit']) / 20)

    player.character.physical_training_points = player.character.physical_training_points + added_physical_points
    player.character.mental_training_points = player.character.mental_training_points + added_mental_points

    for skill in player.character.skills:
        player.character.skills_base[skill] = player.character.skills[skill]

