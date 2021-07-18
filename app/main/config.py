import pathlib as pathlib
import pandas as pd
import json as json

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
STATS_FILE = str(DATA_DIR / f"stats.{DATA_FORMAT}")

TEXT_WRAPPER_WIDTH = 100

PROFESSION_STATS_GROWTH_FILE = pd.read_csv(DATA_DIR / "Profession_Stats_Growth.csv" )
PROFESSION_STATS_GROWTH_FILE.set_index('Profession', inplace=True)

PROFESSION_SKILLPOINT_BONUS_FILE = pd.read_csv(DATA_DIR / "Profession_SkillPoint_Bonus.csv")
PROFESSION_SKILLPOINT_BONUS_FILE.set_index('Profession', inplace=True)

RACE_STATS_FILE = pd.read_csv(DATA_DIR / "Race_Stats.csv")
RACE_STATS_FILE.set_index('Race', inplace=True)

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

verbs_path = DATA_DIR / 'verbs.txt'
with verbs_path.open(mode='r') as file:
    verbs = file.readlines()
verbs = [x.strip() for x in verbs]

prepositions_path = DATA_DIR / 'prepositions.txt'
with prepositions_path.open(mode='r') as file:
    prepositions = file.readlines()
prepositions = [x.strip() for x in prepositions]

# importing all articles
articles_path = DATA_DIR / 'articles.txt'
with articles_path.open(mode='r') as file:
    articles = file.readlines()
articles = [x.strip() for x in articles]

# importing all determiners
determiners_path = DATA_DIR / 'determiners.txt'
with determiners_path.open(mode='r') as file:
    determiners = file.readlines()
determiners = [x.strip() for x in determiners]

# importing all nouns
nouns_path = DATA_DIR / 'nouns.txt'
with nouns_path.open(mode='r') as file:
    nouns = file.readlines()
nouns = [x.strip() for x in nouns]

#import all adjectives
adjectives_path = DATA_DIR / 'adjectives.txt'
with adjectives_path.open(mode='r') as file:
    adjectives = file.readlines()
adjectives = [x.strip() for x in adjectives]

available_stat_points = 528
base_training_points = 25
experience_points_base = 1000
experience_growth = 2
enemy_level_base = 10
enemy_growth = 1
profession_choices = ['Clairvoyant', 'Enchanter', 'Illusionist', 'Paladin', 'Ranger', 'Rogue', 'Inyanga', 'Warrior']
stats = ['Strength', 'Constitution', 'Dexterity', 'Agility', 'Intellect', 'Wisdom', 'Logic', 'Spirit']
gender_choices = ['Female', 'Male']
positions = ['standing', 'kneeling', 'sitting', 'lying']
stances = ['offense', 'forward', 'neutral', 'guarded', 'defense']

def get_skill_data_file(file=SKILLS_FILE, file_format=DATA_FORMAT) -> dict:
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