import pathlib as pathlib
import pandas as pd
import json as json
from enum import Enum, auto

DATA_DIR = pathlib.Path(__file__).parents[1] / "resources"
DATA_FORMAT = "json"

ROOM_FILE = str(DATA_DIR / f"tiles.{DATA_FORMAT}")
ITEM_FILE = str(DATA_DIR / f"items.{DATA_FORMAT}")
ENEMY_FILE = str(DATA_DIR / f"enemies.{DATA_FORMAT}")
NPC_FILE = str(DATA_DIR / f"npcs.{DATA_FORMAT}")
QUEST_FILE = str(DATA_DIR / f"quests.{DATA_FORMAT}")
OBJECT_FILE = str(DATA_DIR / f"objects.{DATA_FORMAT}")
PLAYER_FILE = str(DATA_DIR / f"players.{DATA_FORMAT}")
SKILLS_FILE = str(DATA_DIR / f"skills.{DATA_FORMAT}")
SPELLS_FILE = str(DATA_DIR / f"spells.{DATA_FORMAT}")
STATS_FILE = str(DATA_DIR / f"stats.{DATA_FORMAT}")

TEXT_WRAPPER_WIDTH = 100

PROFESSION_STATS_GROWTH_FILE = pd.read_csv(DATA_DIR / "Profession_Stats_Growth.csv" )
PROFESSION_STATS_GROWTH_FILE.set_index('Profession', inplace=True)

PROFESSION_SKILLPOINT_BONUS_FILE = pd.read_csv(DATA_DIR / "Profession_SkillPoint_Bonus.csv")
PROFESSION_SKILLPOINT_BONUS_FILE.set_index('Profession', inplace=True)

HERITAGE_STATS_FILE = pd.read_csv(DATA_DIR / "Heritage_Stats.csv")
HERITAGE_STATS_FILE.set_index('heritage', inplace=True)

WEAPON_DAMAGE_FACTORS = pd.read_csv(DATA_DIR / "Weapon_Damage_Factors.csv")
WEAPON_DAMAGE_FACTORS.set_index('classification', inplace=True)

WEAPON_ATTACK_FACTORS = pd.read_csv(DATA_DIR / "Weapon_Attack_Factors.csv")
WEAPON_ATTACK_FACTORS.set_index('classification', inplace=True)

EXPERIENCE_ADJUSTMENT_FACTORS = pd.read_csv(DATA_DIR / "Experience_Adjustment_Factors.csv")
EXPERIENCE_ADJUSTMENT_FACTORS.set_index('Level_Variance', inplace=True)

POSITION_FACTORS = pd.read_csv(DATA_DIR / "Position_Factors.csv")
POSITION_FACTORS.set_index('position', inplace=True)

STANCE_FACTORS = pd.read_csv(DATA_DIR / "Stance_Factors.csv")
STANCE_FACTORS.set_index('stance', inplace=True)

SKILLS_MAX_FACTORS = pd.read_csv(DATA_DIR / "Skills_Max_Factors.csv")
SKILLS_MAX_FACTORS.set_index('skills', inplace=True)

SPELL_LEVELS = pd.read_csv(DATA_DIR / "Spell_Levels.csv")
SPELL_LEVELS.set_index('skill_level', inplace=True)

VERBS_PATH = DATA_DIR / 'verbs.txt'
with VERBS_PATH.open(mode='r') as file:
    verbs = file.readlines()
verbs = [x.strip() for x in verbs]

PREPOSITIONS_PATH = DATA_DIR / 'prepositions.txt'
with PREPOSITIONS_PATH.open(mode='r') as file:
    prepositions = file.readlines()
prepositions = [x.strip() for x in prepositions]

# importing all articles
ARTICLES_PATH = DATA_DIR / 'articles.txt'
with ARTICLES_PATH.open(mode='r') as file:
    articles = file.readlines()
articles = [x.strip() for x in articles]

# importing all determiners
DETERMINERS_PATH = DATA_DIR / 'determiners.txt'
with DETERMINERS_PATH.open(mode='r') as file:
    determiners = file.readlines()
determiners = [x.strip() for x in determiners]

# importing all nouns
NOUNS_PATH = DATA_DIR / 'nouns.txt'
with NOUNS_PATH.open(mode='r') as file:
    nouns = file.readlines()
nouns = [x.strip() for x in nouns]

#import all adjectives
ADJECTIVES_PATH = DATA_DIR / 'adjectives.txt'
with ADJECTIVES_PATH.open(mode='r') as file:
    adjectives = file.readlines()
adjectives = [x.strip() for x in adjectives]

def get_skill_data_file(profession: str, file=SKILLS_FILE, file_format=DATA_FORMAT) -> dict:
    with open(file) as fl:
        if file_format == "json":
            data = json.load(fl, parse_int=int, parse_float=float)
        else:
            raise NotImplementedError(fl, "Missing support for opening files of type: {file_format}")
    return data[profession]

def get_spell_data_file(file=SPELLS_FILE, file_format=DATA_FORMAT) -> dict:
    with open(file) as fl:
        if file_format == "json":
            data = json.load(fl, parse_int=int, parse_float=float)
        else:
            raise NotImplementedError(fl, "Missing support for opening files of type: {file_format}")
    return data

def get_stats_data_file(file=STATS_FILE, file_format=DATA_FORMAT) -> dict:
    with open(file) as fl:
        if file_format == "json":
            data = json.load(fl, parse_int=int, parse_float=float)
        else:
            raise NotImplementedError(fl, "Missing support for opening files of type: {file_format}")
    return data


class FormEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    @classmethod
    def check_for_name_match(cls, item):
        for choice in cls:
            if choice.name == item:
                return True
        return False

    def __str__(self):
        return str(self.value)


class Profession(FormEnum):
    """Profession choices"""

    Enchanter = 1
    Warrior = 2
    # Clairvoyant = auto()
    # Illusionist = auto()
    # Paladin = auto()
    # Ranger = auto()
    # Rogue = auto()
    # Inyanga = auto()


class Heritage(FormEnum):
    """Heritage choices"""

    Human = 1
    Elf = 2


class Stats(FormEnum):
    """Stats for character"""

    Strength = 1
    Constitution = 2
    Dexterity = 3
    Agility = 4
    Intellect = 5
    Wisdom = 6
    Logic = 7
    Spririt = 8


class Gender(FormEnum):
    """Gender choices"""

    Female = 1
    Male = 2


class Position(FormEnum):
    """Position choices"""

    standing = 1
    kneeling = 2
    sitting = 3
    lying = 4

    @classmethod
    def starting_position(cls):
        return cls.lying


class Stance(FormEnum):
    """Stance choices"""

    offense = 1
    forward = 2
    neutral = 3
    guarded = 4
    defense = 5

    @classmethod
    def starting_stance(cls):
        return cls.neutral

class CombatAction(FormEnum):
    """Combat action choices"""

    melee = 1
    range = 2

AVAILABLE_STAT_POINTS = 529
STAT_BONUS_DENOMINATOR = AVAILABLE_STAT_POINTS / len(Stats)
BASE_TRAINING_POINTS = 10
EXPERIENCE_POINTS_BASE = 1000
EXPERIENCE_GROWTH = 2
ENEMY_LEVEL_BASE = 10
ENEMY_GROWTH = 1
MANA_REGENERATION_BASE_PERCENTAGE = 0.15
PULSE_MIN_SECONDS = 50
PULSE_MAX_SECONDS = 70
PULSE_INTERVAL_SECONDS = 2